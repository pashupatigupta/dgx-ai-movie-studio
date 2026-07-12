"""
Narration smoke test
DGX AI Movie Studio

Verifies Piper is installed, the voice model is present, that a short line of
text actually synthesizes to audio, and that scene durations follow the
voiceover length. Run from the project root:

    python -m tests.test_narration_service
"""

import os
import tempfile

from services.narration_service import NarrationService, audio_duration
from services.movie_service import scene_duration


def main():
    service = NarrationService()

    print("1. Piper availability...")
    problem = service.status_message()
    if problem:
        print("   NOT READY:\n   " + problem.replace("\n", "\n   "))
        return
    print(f"   piper found, voice: {service.voice_path()}")

    print("2. Synthesizing a test line...")
    tmp = os.path.join(tempfile.gettempdir(), "dgx_narration_test.wav")
    service.synthesize("A robot discovers humanity.", tmp)
    assert os.path.exists(tmp), "no wav produced"
    duration = audio_duration(tmp)
    assert duration > 0.3, f"suspiciously short audio: {duration}s"
    print(f"   produced {tmp} ({duration:.2f}s)")

    print("3. Scene duration follows narration length...")
    # Long narration should extend the scene beyond the minimum.
    assert scene_duration(tmp, 0.5) > 0.5
    # A generous minimum should still win over short narration.
    assert scene_duration(tmp, 60.0) == 60.0
    # No narration falls back to the fixed duration.
    assert scene_duration(None, 3.0) == 3.0
    print("   ok")

    os.remove(tmp)
    print("\nALL NARRATION TESTS PASSED")


if __name__ == "__main__":
    main()
