"""
Narration Service
DGX AI Movie Studio

Phase E: turn scene descriptions into spoken audio using Piper TTS.

Piper runs locally on CPU (no GPU needed, so it doesn't compete with SDXL)
and is invoked through its CLI, which is the most stable interface across
Piper versions.

Requires:
    pip install piper-tts
    python3 -m piper.download_voices --data-dir models/piper en_US-lessac-medium
"""

import shutil
import subprocess
from pathlib import Path

from repositories.scene_repository import SceneRepository


VOICE_DIR = Path("models/piper")
NARRATION_DIR = Path("outputs/narration")
DEFAULT_VOICE = "en_US-lessac-medium"


class NarrationService:

    def __init__(self, voice=DEFAULT_VOICE):
        self.voice = voice
        self.scenes = SceneRepository()
        NARRATION_DIR.mkdir(parents=True, exist_ok=True)

    # ---- availability ----------------------------------------------

    @staticmethod
    def piper_available():
        return shutil.which("piper") is not None

    def voice_path(self):
        return VOICE_DIR / f"{self.voice}.onnx"

    def voice_available(self):
        return self.voice_path().exists()

    def ready(self):
        """True when both the piper binary and the voice model are present."""
        return self.piper_available() and self.voice_available()

    def status_message(self):
        """Human-readable reason narration isn't available, or None if it is."""
        if not self.piper_available():
            return (
                "Piper is not installed. Run:  pip install piper-tts"
            )
        if not self.voice_available():
            return (
                f"Voice model not found at {self.voice_path()}. Run:\n"
                f"python3 -m piper.download_voices --data-dir models/piper "
                f"{self.voice}"
            )
        return None

    # ---- synthesis --------------------------------------------------

    def narration_path(self, story_id, scene_number):
        """Deterministic path for a scene's narration audio."""
        return NARRATION_DIR / f"story_{story_id}_scene_{scene_number}.wav"

    def synthesize(self, text, output_path):
        """Speak `text` into a WAV file at output_path. Returns the path."""
        problem = self.status_message()
        if problem:
            raise RuntimeError(problem)

        if not text or not text.strip():
            raise ValueError("Cannot synthesize empty text.")

        proc = subprocess.run(
            [
                "piper",
                "--model", str(self.voice_path()),
                "--output_file", str(output_path),
            ],
            input=text,
            capture_output=True,
            text=True,
        )

        if proc.returncode != 0 or not Path(output_path).exists():
            tail = "\n".join(proc.stderr.strip().splitlines()[-10:])
            raise RuntimeError(f"Piper failed:\n{tail}")

        return str(output_path)

    def narrate_scene(self, scene, force=False):
        """
        Generate (or reuse) narration for one scene.
        Returns the path to the WAV file.
        """
        path = self.narration_path(scene["story_id"], scene["scene_number"])

        if path.exists() and not force:
            return str(path)

        text = scene.get("description") or scene.get("title") or ""
        return self.synthesize(text, path)

    def narrate_story(self, story_id, force=False):
        """
        Generate narration for every scene in a story.
        Returns a list of (scene_number, wav_path).
        """
        results = []
        for scene in self.scenes.list_by_story(story_id):
            wav = self.narrate_scene(scene, force=force)
            results.append((scene["scene_number"], wav))
        return results

    def narration_count(self, story_id):
        """How many scenes already have narration audio on disk."""
        count = 0
        for scene in self.scenes.list_by_story(story_id):
            if self.narration_path(
                story_id, scene["scene_number"]
            ).exists():
                count += 1
        return count


def audio_duration(path):
    """Return the duration of an audio file in seconds, via ffprobe."""
    proc = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {path}: {proc.stderr.strip()}")
    return float(proc.stdout.strip())
