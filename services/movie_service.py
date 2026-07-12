"""
Movie Service
DGX AI Movie Studio

Phases B + E: stitch a story's scene images into a watchable MP4, optionally
with a spoken narration track.

Approach: each scene image becomes a short H.264 clip (scaled and letterboxed
onto a 16:9 frame, with optional fade in/out), then all clips are concatenated.
Rendering per-scene clips first — rather than one giant ffmpeg filter graph —
keeps each step simple and makes failures easy to locate.

With narration enabled, a scene stays on screen for as long as its voiceover
takes (plus a little breathing room), so the picture never cuts off mid-
sentence. Every clip is given an audio track (silent if a scene has no
narration) so the final concatenation stays consistent.

Requires the `ffmpeg` binary on PATH.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

from repositories.story_repository import StoryRepository
from repositories.scene_repository import SceneRepository
from services.narration_service import NarrationService, audio_duration


MOVIE_DIR = Path("outputs/movies")
TARGET_W = 1280
TARGET_H = 720
SAMPLE_RATE = 22050

# Silence held after a narration line finishes, so scenes don't cut abruptly.
NARRATION_TAIL = 1.0


def build_video_filter(duration, fade, width=TARGET_W, height=TARGET_H):
    """
    Build the ffmpeg -vf filter string for a single scene clip.

    Kept as a pure function so it can be unit-tested without running ffmpeg.
    Fades are skipped for very short durations where they'd overlap.
    """
    parts = [
        f"scale={width}:{height}:force_original_aspect_ratio=decrease",
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
        "setsar=1",
    ]

    if fade and duration >= 1.2:
        out_start = round(duration - 0.5, 3)
        parts.append("fade=t=in:st=0:d=0.5")
        parts.append(f"fade=t=out:st={out_start}:d=0.5")

    parts.append("format=yuv420p")
    return ",".join(parts)


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
        """Return this story's scenes that have an existing image file, in order."""
        result = []
        for scene in self.scenes.list_by_story(story_id):
            path = scene.get("image_path")
            if path and Path(path).exists():
                result.append(scene)
        return result

    def movie_path(self, story_id):
        """Return the path to an already-built movie for this story, or None."""
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
                     audio_path=None):
        """
        Render one scene image into a clip of `duration` seconds.

        Always produces an audio track: the narration WAV (padded with silence
        to fill the clip) when given, otherwise pure silence. Uniform streams
        let the clips be concatenated without re-encoding.
        """
        vf = build_video_filter(duration, fade)

        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(image_path)]

        if audio_path:
            cmd += ["-i", str(audio_path)]
            audio_filter = "apad"
        else:
            cmd += [
                "-f", "lavfi",
                "-i", f"anullsrc=r={SAMPLE_RATE}:cl=mono",
            ]
            audio_filter = "anull"

        cmd += [
            "-t", str(duration),
            "-vf", vf,
            "-af", audio_filter,
            "-r", "25",
            "-c:v", "libx264",
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
                    narrate=False):
        """
        Render every image-bearing scene of a story into a single MP4.

        When `narrate` is True, generates (or reuses) Piper narration for each
        scene and sizes each scene to its voiceover.

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
                wav = None
                if narrate:
                    wav = self.narration.narrate_scene(scene)

                duration = scene_duration(wav, seconds_per_scene)

                clip_path = temp_dir / f"clip_{index:03d}.mp4"
                self._render_clip(
                    scene["image_path"],
                    clip_path,
                    duration,
                    fade,
                    audio_path=wav,
                )
                clips.append(clip_path)

            list_file = temp_dir / "clips.txt"
            with open(list_file, "w") as f:
                for clip in clips:
                    f.write(f"file '{clip.resolve()}'\n")

            output = MOVIE_DIR / f"story_{story_id}.mp4"
            self._concat(list_file, output)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        self.stories.update_status(story_id, "movie_ready")
        return str(output)
