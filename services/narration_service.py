"""
Narration Service
DGX AI Movie Studio

Phase E: turn a scene's SPOKEN LINE into audio using Piper TTS.

Speaks `narration_text` (plain prose written for a narrator), falling back to
`description` only if no narration line exists. Never assume the image prompt
is speakable: it's full of style tags like "photorealistic, 8K" that sound
absurd read aloud.

Piper runs locally on CPU (no GPU needed, so it doesn't compete with SDXL) and
is invoked through its CLI, the most stable interface across Piper versions.

Binary lookup: we look for `piper` next to the running interpreter (this venv's
bin/) BEFORE falling back to PATH. A long-running Streamlit server keeps the
environment it started with, so a tool installed mid-session may not be on its
PATH even though it works in the shell. Resolving via sys.executable avoids it.

Requires:
    pip install piper-tts
    python3 -m piper.download_voices --data-dir models/piper en_US-lessac-medium
"""

import shutil
import subprocess
import sys
from pathlib import Path

from repositories.scene_repository import SceneRepository


VOICE_DIR = Path("models/piper")
NARRATION_DIR = Path("outputs/narration")
DEFAULT_VOICE = "en_US-lessac-medium"


def find_piper():
    """Return the path to the piper binary, or None if it can't be found."""
    candidate = Path(sys.executable).parent / "piper"
    if candidate.exists():
        return str(candidate)
    return shutil.which("piper")


def available_voices():
    """Voice names (without extension) present in models/piper/."""
    if not VOICE_DIR.exists():
        return []
    return sorted(p.stem for p in VOICE_DIR.glob("*.onnx"))


class NarrationService:

    def __init__(self, voice=None):
        self.voice = voice or DEFAULT_VOICE
        self.scenes = SceneRepository()
        NARRATION_DIR.mkdir(parents=True, exist_ok=True)

    # ---- availability ----------------------------------------------

    @staticmethod
    def piper_binary():
        return find_piper()

    def piper_available(self):
        return self.piper_binary() is not None

    def voice_path(self):
        return VOICE_DIR / f"{self.voice}.onnx"

    def voice_available(self):
        return self.voice_path().exists()

    def ready(self):
        return self.piper_available() and self.voice_available()

    def status_message(self):
        """Human-readable reason narration isn't available, or None if it is."""
        if not self.piper_available():
            return (
                "Piper was not found. Install it with:  pip install piper-tts\n"
                "If you just installed it, restart Streamlit so it picks up "
                "the new binary."
            )
        if not self.voice_available():
            return (
                f"Voice model not found at {self.voice_path()}. Run:\n"
                f"python3 -m piper.download_voices --data-dir models/piper "
                f"{self.voice}"
            )
        return None

    # ---- text selection ---------------------------------------------

    @staticmethod
    def spoken_text(scene):
        """
        The line a narrator should actually say for this scene.

        Prefers narration_text; falls back to the scene title (never the raw
        image prompt, which is full of unspeakable style tags).
        """
        text = (scene.get("narration_text") or "").strip()
        if text:
            return text
        title = (scene.get("title") or "").split(":", 1)[-1].strip()
        return title

    # ---- synthesis --------------------------------------------------

    def narration_path(self, story_id, scene_number):
        """Deterministic path, keyed by voice so switching voices re-renders."""
        return NARRATION_DIR / (
            f"story_{story_id}_scene_{scene_number}_{self.voice}.wav"
        )

    def synthesize(self, text, output_path):
        """Speak `text` into a WAV file at output_path. Returns the path."""
        problem = self.status_message()
        if problem:
            raise RuntimeError(problem)

        if not text or not text.strip():
            raise ValueError("Cannot synthesize empty text.")

        proc = subprocess.run(
            [
                self.piper_binary(),
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
        """Generate (or reuse) narration for one scene. Returns the WAV path."""
        path = self.narration_path(scene["story_id"], scene["scene_number"])

        if path.exists() and not force:
            return str(path)

        text = self.spoken_text(scene)
        if not text:
            return None

        return self.synthesize(text, path)

    def narrate_story(self, story_id, force=False):
        results = []
        for scene in self.scenes.list_by_story(story_id):
            wav = self.narrate_scene(scene, force=force)
            results.append((scene["scene_number"], wav))
        return results

    def clear_narration(self, story_id):
        """Delete cached narration WAVs for a story (all voices)."""
        removed = 0
        for path in NARRATION_DIR.glob(f"story_{story_id}_scene_*.wav"):
            path.unlink()
            removed += 1
        return removed

    def narration_count(self, story_id):
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
