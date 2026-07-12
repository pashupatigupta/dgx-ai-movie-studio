"""
Movie service smoke test
DGX AI Movie Studio

Checks the pieces that don't require rendering a full video: ffmpeg
availability and the video-filter builder (including camera motion).

    python -m tests.test_movie_service
"""

import shutil

from services.movie_service import (
    MovieService, build_video_filter, motion_for_scene, AUTO_CYCLE,
)


def main():
    print("1. ffmpeg availability...")
    if shutil.which("ffmpeg"):
        print("   ffmpeg found")
    else:
        print("   WARNING: ffmpeg NOT found — sudo apt install -y ffmpeg")

    print("2. Static filter (no motion, fade on)...")
    vf = build_video_filter(3.0, True, motion="none")
    assert "scale=1280:720" in vf
    assert "zoompan" not in vf
    assert "fade=t=in" in vf
    assert vf.endswith("format=yuv420p")
    print("   ok")

    print("3. Zoom-in filter...")
    vf = build_video_filter(3.0, True, motion="zoom_in")
    assert "zoompan" in vf
    assert "scale=2560:1440" in vf, "should upscale before zoompan"
    assert "s=1280x720" in vf
    assert "min(zoom+" in vf
    print("   ok")

    print("4. Zoom-out filter...")
    vf = build_video_filter(3.0, True, motion="zoom_out")
    assert "max(1.0,zoom-" in vf
    print("   ok")

    print("5. Pan filters...")
    right = build_video_filter(3.0, False, motion="pan_right")
    left = build_video_filter(3.0, False, motion="pan_left")
    assert "on/75" in right, right
    assert "(1-on/75)" in left, left
    print("   ok")

    print("6. Fill vs letterbox...")
    filled = build_video_filter(3.0, False, motion="zoom_in", fill=True)
    boxed = build_video_filter(3.0, False, motion="zoom_in", fill=False)
    assert "crop=2560:1440" in filled
    assert "pad=2560:1440" in boxed
    print("   ok")

    print("7. Short clips skip fades...")
    assert "fade" not in build_video_filter(0.5, True, motion="none")
    print("   ok")

    print("8. Auto motion cycles across scenes...")
    picked = [motion_for_scene("auto", i) for i in range(len(AUTO_CYCLE) + 1)]
    assert picked[0] == AUTO_CYCLE[0]
    assert len(set(picked[:len(AUTO_CYCLE)])) == len(AUTO_CYCLE), (
        "auto should vary motion between consecutive scenes"
    )
    assert picked[len(AUTO_CYCLE)] == AUTO_CYCLE[0], "should wrap around"
    assert motion_for_scene("zoom_in", 3) == "zoom_in", "explicit wins"
    print("   ok")

    print("9. Unknown motion is rejected...")
    try:
        build_video_filter(3.0, True, motion="barrel_roll")
        raise AssertionError("should have raised")
    except ValueError:
        print("   ok")

    print("10. MovieService instantiates...")
    MovieService()
    print("   ok")

    print("\nALL MOVIE SERVICE TESTS PASSED")


if __name__ == "__main__":
    main()
