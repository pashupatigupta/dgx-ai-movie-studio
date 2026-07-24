"""
Video service smoke test
DGX AI Movie Studio

Tests workflow construction without generating a video (which takes minutes).
Verifies the LTX template exists and that values land in the right node IDs.

    python -m tests.test_video_service
"""

from services.video_service import (
    build_workflow, motion_prompt, WORKFLOW_PATH,
    NODE_IMAGE, NODE_PROMPT, NODE_WIDTH, NODE_HEIGHT,
    NODE_DURATION, NODE_SEED_A, NODE_SAVE,
)


def main():
    print("1. LTX workflow template present...")
    assert WORKFLOW_PATH.exists(), (
        f"missing {WORKFLOW_PATH} — export it from ComfyUI "
        "(Workflow -> Export (API))"
    )
    print(f"   {WORKFLOW_PATH}")

    print("2. Injecting values into the workflow...")
    wf = build_workflow(
        image_filename="STORY_1_SCENE_1.png",
        prompt="A robot turns slowly toward the camera in dim light.",
        width=768, height=512, duration=5, fps=25, seed=99,
        filename_prefix="video/TEST",
    )
    assert wf[NODE_IMAGE]["inputs"]["image"] == "STORY_1_SCENE_1.png"
    assert "robot" in wf[NODE_PROMPT]["inputs"]["value"]
    assert wf[NODE_WIDTH]["inputs"]["value"] == 768
    assert wf[NODE_HEIGHT]["inputs"]["value"] == 512
    assert wf[NODE_DURATION]["inputs"]["value"] == 5
    assert wf[NODE_SEED_A]["inputs"]["noise_seed"] == 99
    assert wf[NODE_SAVE]["inputs"]["filename_prefix"] == "video/TEST"
    print("   all injection points correct")

    print("3. Checkpoint still wired to the distilled model...")
    ckpt = wf["320:316"]["inputs"]["ckpt_name"]
    assert "distilled" in ckpt, ckpt
    print(f"   {ckpt}")

    print("4. Motion prompt falls back sensibly...")
    assert motion_prompt({"description": "A ship at sea"}) == "A ship at sea"
    assert motion_prompt({"title": "Scene 1: Opening", "description": ""}) \
        == "Scene 1: Opening"
    print("   ok")

    print("\nALL VIDEO SERVICE TESTS PASSED")


if __name__ == "__main__":
    main()
