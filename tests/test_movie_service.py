"""
Movie service smoke test
DGX AI Movie Studio

Checks the pieces that don't require rendering a full video:
ffmpeg availability, the video-filter builder, and that MovieService
instantiates. Run from the project root:

    python -m tests.test_movie_service
"""

import shutil

from services.movie_service import MovieService, build_video_filter


def main():
    print("1. ffmpeg availability...")
    if shutil.which("ffmpeg"):
        print("   ffmpeg found")
    else:
        print("   WARNING: ffmpeg NOT found — install with: "
              "sudo apt install -y ffmpeg")

    print("2. video filter (normal duration, fade on)...")
    vf = build_video_filter(3.0, True)
    assert "scale=1280:720" in vf
    assert "fade=t=in" in vf
    assert "fade=t=out" in vf
    assert vf.endswith("format=yuv420p")
    print("   " + vf)

    print("3. video filter (short duration -> no fade)...")
    vf_short = build_video_filter(0.5, True)
    assert "fade" not in vf_short
    print("   " + vf_short)

    print("4. video filter (fade off)...")
    vf_nofade = build_video_filter(5.0, False)
    assert "fade" not in vf_nofade
    print("   ok")

    print("5. MovieService instantiates...")
    MovieService()
    print("   ok")

    print("\nALL MOVIE SERVICE TESTS PASSED")


if __name__ == "__main__":
    main()
