"""
Movie Service
DGX AI Movie Studio

Phases B + E + F + D1: turn a story's scene images into a watchable MP4, with
optional camera motion, spoken narration, and a music bed.

Rendering strategy: each scene image becomes its own short H.264 clip, then all
clips are concatenated. Doing it per-clip rather than as one giant ffmpeg filter
graph keeps each step simple and makes failures easy to locate.

Phase D1 — camera motion (the "Ken Burns" effect): a still image with a slow
push-in or drift across it reads as cinematic, while a static frame reads as a
slideshow. This is done entirely in ffmpeg (seconds per clip, no model, no GPU),
and it is deliberately built behind a small `motion` abstraction so that Phase
D2 — real AI motion via a video model like LTX-Video — can slot in later as
another animator without touching this rendering code.

Requires the `ffmpeg` binary on PATH.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

from repositories.story_repository import StoryRepository
from repositories.scene_repository import SceneRepository
from services.narration_service import NarrationService, audio_duration
from services.music_service import MusicService, LibraryProvider, media_duration


MOVIE_DIR = Path("outputs/movies")
TARGET_W = 1280
TARGET_H = 720
FPS = 25
SAMPLE_RATE = 22050

# Silence held after a narration line finishes, so scenes don't cut abruptly.
NARRATION_TAIL = 1.0

# How far a zoom travels over a scene (1.15 = a 15% push).
ZOOM_RANGE = 0.15

# Motion styles. "auto" cycles through the others so consecutive scenes don't
# all move the same way, which is what makes a sequence feel edited.
MOTION_STYLES = ["none", "zoom_in", "zoom_out", "pan_right", "pan_left"]
AUTO_CYCLE = ["zoom_in", "pan_right", "zoom_out", "pan_left"]


def motion_for_scene(motion, index):
    """Resolve the motion style for a given scene position."""
    if motion == "auto":
        return AUTO_CYCLE[index % len(AUTO_CYCLE)]
    return motion


def build_video_filter(duration, fade, motion="none", fill=True,
                       width=TARGET_W, height=TARGET_H, fps=FPS):
    """
    Build the ffmpeg -vf filter string for one scene clip.

    Pure function, so the filter graph can be unit-tested without ffmpeg.

    With motion, the image is first upscaled to 2x the target. zoompan samples
    from that larger source, which is what prevents the shaky, stair-stepping
    look you get when zooming a small image directly.

    `fill` crops the image to fill the 16:9 frame (no black bars, and room to
    pan). Turn it off to letterbox instead and keep the whole image visible.
    """
    frames = max(1, int(round(float(duration) * fps)))

    # ---- no motion: the original static path ------------------------
    if motion in (None, "none"):
        parts = [
            f"scale={width}:{height}:force_original_aspect_ratio=decrease",
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
            "setsar=1",
        ]
        parts += _fade_parts(duration, fade)
        parts.append("format=yuv420p")
        return ",".join(parts)

    # ---- motion: upscale, then zoompan ------------------------------
    big_w, big_h = width * 2, height * 2

    if fill:
        prescale = (
            f"scale={big_w}:{big_h}:force_original_aspect_ratio=increase,"
            f"crop={big_w}:{big_h}"
        )
    else:
        prescale = (
            f"scale={big_w}:{big_h}:force_original_aspect_ratio=decrease,"
            f"pad={big_w}:{big_h}:(ow-iw)/2:(oh-ih)/2"
        )

    step = ZOOM_RANGE / frames
    zoom_max = 1 + ZOOM_RANGE
    centre_x = "iw/2-(iw/zoom/2)"
    centre_y = "ih/2-(ih/zoom/2)"

    if motion == "zoom_in":
        z = f"min(zoom+{step:.6f},{zoom_max})"
        x, y = centre_x, centre_y
    elif motion == "zoom_out":
        # zoompan resets zoom to 1 on the first frame, so we jump to the top
        # of the range and walk back down.
        z = f"if(lte(zoom,1.0),{zoom_max},max(1.0,zoom-{step:.6f}))"
        x, y = centre_x, centre_y
    elif motion == "pan_right":
        z = f"{zoom_max}"
        x = f"(iw-iw/zoom)*on/{frames}"
        y = centre_y
    elif motion == "pan_left":
        z = f"{zoom_max}"
        x = f"(iw-iw/zoom)*(1-on/{frames})"
        y = centre_y
    else:
        raise ValueError(f"Unknown motion style: {motion}")

    zoompan = (
        f"zoompan=z='{z}':x='{x}':y='{y}':"
        f"d={frames}:s={width}x{height}:fps={fps}"
    )

    parts = [prescale, zoompan, "setsar=1"]
    parts += _fade_parts(duration, fade)
    parts.append("format=yuv420p")
    return ",".join(parts)


def _fade_parts(duration, fade):
    """Fade in/out, skipped on clips too short to hold them."""
    if not fade or float(duration) < 1.2:
        return []
    out_start = round(float(duration) - 0.5, 3)
    return [
        "fade=t=in:st=0:d=0.5",
        f"fade=t=out:st={out_start}:d=0.5",
    ]


def scene_duration(narration_wav, fallback, tail=NARRATION_TAIL):
    """
    How long a scene should stay on screen.

    With narration: the length of the voiceover plus a tail of silence, but
    never shorter than `fallback`. Without narration: just `fallback`.
    """
    if not narration_wav:
        return float(fallback)
    spoken = audio_duration(narration_wav)
    return round(max(float(fallback), spoken + tail), 3)


class MovieService:

    def __init__(self, voice=None):
        self.stories = StoryRepository()
        self.scenes = SceneRepository()
        self.narration = NarrationService(voice=voice)
        MOVIE_DIR.mkdir(parents=True, exist_ok=True)

    # ---- helpers ---------------------------------------------------

    @staticmethod
    def ffmpeg_available():
        return shutil.which("ffmpeg") is not None

    def scenes_with_images(self, story_id):
        """This story's scenes that have an existing image file, in order."""
        result = []
        for scene in self.scenes.list_by_story(story_id):
            path = scene.get("image_path")
            if path and Path(path).exists():
                result.append(scene)
        return result

    def movie_path(self, story_id):
        """Path to an already-built movie for this story, or None."""
        path = MOVIE_DIR / f"story_{story_id}.mp4"
        return str(path) if path.exists() else None

    @staticmethod
    def _run(cmd):
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            tail = "\n".join(proc.stderr.strip().splitlines()[-15:])
            raise RuntimeError(f"ffmpeg failed:\n{tail}")

    # ---- clip rendering --------------------------------------------

    def _render_clip(self, image_path, clip_path, duration, fade,
                     motion="none", fill=True, audio_path=None):
        """
        Render one scene image into a clip of `duration` seconds.

        Always produces an audio track — the narration WAV (padded with silence
        to fill the clip) when given, otherwise pure silence. Uniform streams
        let the clips be concatenated without re-encoding.
        """
        vf = build_video_filter(duration, fade, motion=motion, fill=fill)

        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(image_path)]

        if audio_path:
            cmd += ["-i", str(audio_path)]
            audio_filter = "apad"
        else:
            cmd += ["-f", "lavfi", "-i", f"anullsrc=r={SAMPLE_RATE}:cl=mono"]
            audio_filter = "anull"

        cmd += [
            "-t", str(duration),
            "-vf", vf,
            "-af", audio_filter,
            "-r", str(FPS),
            "-c:v", "libx264",
            "-preset", "medium",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", str(SAMPLE_RATE),
            "-ac", "1",
            str(clip_path),
        ]

        self._run(cmd)

    def _render_ai_clip(self, video_path, clip_path, duration, fade,
                        audio_path=None):
        """
        Normalise an AI-generated clip (LTX outputs 768x512 with its own
        ambient audio) into the same format as our still-image clips, so they
        concatenate cleanly.

        If the scene needs to be longer than the generated clip (because the
        narration runs past it), the final frame is held with tpad rather than
        cutting the voice off mid-sentence.
        """
        vf = [
            f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=decrease",
            f"pad={TARGET_W}:{TARGET_H}:(ow-iw)/2:(oh-ih)/2",
            "setsar=1",
            f"tpad=stop_mode=clone:stop_duration={duration}",
        ]
        vf += _fade_parts(duration, fade)
        vf.append("format=yuv420p")

        cmd = ["ffmpeg", "-y", "-i", str(video_path)]

        if audio_path:
            # Narration replaces the model's ambient audio.
            cmd += ["-i", str(audio_path), "-map", "0:v", "-map", "1:a"]
            audio_filter = "apad"
        else:
            # Keep LTX's generated ambient audio.
            audio_filter = "apad"

        cmd += [
            "-t", str(duration),
            "-vf", ",".join(vf),
            "-af", audio_filter,
            "-r", str(FPS),
            "-c:v", "libx264",
            "-preset", "medium",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", str(SAMPLE_RATE),
            "-ac", "1",
            str(clip_path),
        ]

        self._run(cmd)

    def _concat(self, list_file, output):
        self._run([
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            str(output),
        ])

    # ---- main entry point ------------------------------------------

    def build_movie(self, story_id, seconds_per_scene=3.0, fade=True,
                    motion="auto", fill=True, narrate=False,
                    music_track=None, music_volume=0.25, duck_music=True):
        """
        Render every image-bearing scene of a story into a single MP4.

        motion:  "none" | "zoom_in" | "zoom_out" | "pan_right" | "pan_left"
                 | "auto" (cycles, so consecutive scenes move differently)
        narrate: generate/reuse Piper narration and size scenes to the voiceover
        music_track: a filename in assets/music/, laid under and ducked

        Returns the path to the finished movie.
        """
        if not self.ffmpeg_available():
            raise RuntimeError(
                "ffmpeg is not installed. Install it with: "
                "sudo apt install -y ffmpeg"
            )

        if narrate:
            problem = self.narration.status_message()
            if problem:
                raise RuntimeError(problem)

        scenes = self.scenes_with_images(story_id)
        if not scenes:
            raise RuntimeError(
                "No scene images found for this story. Generate scene images "
                "in the Storyboard page first."
            )

        temp_dir = Path(tempfile.mkdtemp(prefix="dgx_movie_"))
        try:
            clips = []
            for index, scene in enumerate(scenes):
                wav = self.narration.narrate_scene(scene) if narrate else None
                clip_path = temp_dir / f"clip_{index:03d}.mp4"

                ai_clip = scene.get("video_path")
                use_ai = (
                    motion == "ai"
                    and ai_clip
                    and Path(ai_clip).exists()
                )

                if use_ai:
                    # Scene lasts at least as long as its generated clip, and
                    # longer if the narration needs the room.
                    clip_len = media_duration(ai_clip)
                    duration = max(
                        clip_len, scene_duration(wav, seconds_per_scene)
                    )
                    self._render_ai_clip(
                        ai_clip, clip_path, duration, fade, audio_path=wav,
                    )
                else:
                    duration = scene_duration(wav, seconds_per_scene)
                    # "ai" with no clip falls back to Ken Burns, not a freeze.
                    style = "auto" if motion == "ai" else motion
                    self._render_clip(
                        scene["image_path"],
                        clip_path,
                        duration,
                        fade,
                        motion=motion_for_scene(style, index),
                        fill=fill,
                        audio_path=wav,
                    )

                clips.append(clip_path)

            list_file = temp_dir / "clips.txt"
            with open(list_file, "w") as f:
                for clip in clips:
                    f.write(f"file '{clip.resolve()}'\n")

            output = MOVIE_DIR / f"story_{story_id}.mp4"

            if music_track:
                # Concat to a temp file first, then mix music into the final.
                silent = temp_dir / "no_music.mp4"
                self._concat(list_file, silent)

                music = MusicService(LibraryProvider(music_track))
                music.mix(
                    video_in=silent,
                    video_out=output,
                    volume=float(music_volume),
                    duck=bool(duck_music),
                )
            else:
                self._concat(list_file, output)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        self.stories.update_status(story_id, "movie_ready")
        return str(output)
