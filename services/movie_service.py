"""
Movie Service
DGX AI Movie Studio

Phase B: stitch a story's scene images into a watchable MP4.

Approach: each scene image is rendered into a short H.264 clip (scaled and
letterboxed onto a 16:9 frame, with optional fade in/out), then all clips are
concatenated into the final movie. Rendering per-scene clips first — rather
than one giant ffmpeg filter graph — keeps each step simple and makes failures
easy to locate.

Requires the `ffmpeg` binary on PATH.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

from repositories.story_repository import StoryRepository
from repositories.scene_repository import SceneRepository


MOVIE_DIR = Path("outputs/movies")
TARGET_W = 1280
TARGET_H = 720


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


class MovieService:

    def __init__(self):
        self.stories = StoryRepository()
        self.scenes = SceneRepository()
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

    def _render_clip(self, image_path, clip_path, duration, fade):
        vf = build_video_filter(duration, fade)
        self._run([
            "ffmpeg", "-y",
            "-loop", "1",
            "-t", str(duration),
            "-i", str(image_path),
            "-vf", vf,
            "-r", "25",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(clip_path),
        ])

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

    def build_movie(self, story_id, seconds_per_scene=3.0, fade=True):
        """
        Render every image-bearing scene of a story into a single MP4.
        Returns the path to the finished movie.
        """
        if not self.ffmpeg_available():
            raise RuntimeError(
                "ffmpeg is not installed. Install it with: "
                "sudo apt install -y ffmpeg"
            )

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
                clip_path = temp_dir / f"clip_{index:03d}.mp4"
                self._render_clip(
                    scene["image_path"],
                    clip_path,
                    float(seconds_per_scene),
                    fade,
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
