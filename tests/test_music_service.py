"""
Music service smoke test
DGX AI Movie Studio

Tests the mixing logic without rendering: the ffmpeg filter graph, provider
status handling, and track discovery. Run from the project root:

    python -m tests.test_music_service
"""

from services.music_service import (
    build_music_filter, available_tracks, LibraryProvider,
    MusicService, MUSIC_DIR,
)


def main():
    print("1. Music filter with ducking...")
    vf = build_music_filter(30.0, volume=0.25, duck=True)
    assert "volume=0.25" in vf
    assert "sidechaincompress" in vf
    assert "afade=t=in" in vf
    assert "afade=t=out:st=27.0" in vf, vf
    assert vf.endswith("[aout]")
    print("   ok (ducking enabled)")

    print("2. Music filter without ducking...")
    vf_flat = build_music_filter(30.0, volume=0.4, duck=False)
    assert "sidechaincompress" not in vf_flat
    assert "amix" in vf_flat
    print("   ok")

    print("3. Fade-out never starts before zero on short movies...")
    vf_short = build_music_filter(1.0, duck=False)
    assert "afade=t=out:st=0.0" in vf_short, vf_short
    print("   ok")

    print("4. Track discovery...")
    tracks = available_tracks()
    print(f"   {len(tracks)} track(s) in {MUSIC_DIR}/: {tracks or '(none)'}")

    print("5. Provider status when nothing is selected...")
    provider = LibraryProvider()
    msg = provider.status_message()
    assert msg is not None
    print(f"   {msg}")

    print("6. MusicService instantiates...")
    MusicService()
    print("   ok")

    print("\nALL MUSIC SERVICE TESTS PASSED")


if __name__ == "__main__":
    main()
