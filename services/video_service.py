"""
Video Service
DGX AI Movie Studio

Phase D2: real AI motion. Animates a scene's still image into a short video
clip using LTX-Video 2.3 (distilled) through ComfyUI.

Mirrors ImageService: build a workflow from a template, submit it, wait, copy
the result out. The workflow template is workflows/ltx_i2v_api.json, exported
from the ComfyUI graph that was verified to work by hand — we inject values
into known node IDs rather than constructing the graph from scratch.

Node map (from the verified export):
    324      LoadImage            -> inputs.image        (filename in ComfyUI input/)
    320:319  Prompt               -> inputs.value        (motion description)
    320:313  Negative CLIPTextEncode -> inputs.text
    320:312  Width                -> inputs.value
    320:299  Height               -> inputs.value
    320:301  Duration (seconds)   -> inputs.value
    320:300  Frame rate           -> inputs.value
    320:277  RandomNoise          -> inputs.noise_seed
    320:276  RandomNoise (2nd pass) -> inputs.noise_seed
    325      SaveVideo            -> inputs.filename_prefix

LTX also generates synchronized ambient audio in the same pass, so the clip
arrives with atmosphere already on it.
"""

import json
import shutil
from pathlib import Path

from services import comfy_service
from repositories.scene_repository import SceneRepository


WORKFLOW_PATH = Path("workflows/ltx_i2v_api.json")
COMFY_OUTPUT = Path.home() / "jupyterlab" / "ComfyUI" / "output"
VIDEO_DIR = Path("generated/videos")

DEFAULT_NEGATIVE = "pc game, console game, video game, cartoon, childish, ugly"

# Node IDs in the exported workflow.
NODE_IMAGE = "324"
NODE_PROMPT = "320:319"
NODE_NEGATIVE = "320:313"
NODE_WIDTH = "320:312"
NODE_HEIGHT = "320:299"
NODE_DURATION = "320:301"
NODE_FPS = "320:300"
NODE_SEED_A = "320:277"
NODE_SEED_B = "320:276"
NODE_SAVE = "325"


def build_workflow(image_filename, prompt, width=768, height=512,
                   duration=5, fps=25, seed=42,
                   negative_prompt=DEFAULT_NEGATIVE,
                   filename_prefix="video/DGX"):
    """
    Load the LTX workflow template and inject this scene's values.

    Pure-ish function (reads the template from disk) so it can be tested
    without touching ComfyUI.
    """
    if not WORKFLOW_PATH.exists():
        raise FileNotFoundError(
            f"LTX workflow template not found at {WORKFLOW_PATH}. Export it "
            "from ComfyUI with Workflow -> Export (API)."
        )

    with open(WORKFLOW_PATH) as f:
        wf = json.load(f)

    wf[NODE_IMAGE]["inputs"]["image"] = image_filename
    wf[NODE_PROMPT]["inputs"]["value"] = prompt
    wf[NODE_NEGATIVE]["inputs"]["text"] = negative_prompt
    wf[NODE_WIDTH]["inputs"]["value"] = int(width)
    wf[NODE_HEIGHT]["inputs"]["value"] = int(height)
    wf[NODE_DURATION]["inputs"]["value"] = int(duration)
    wf[NODE_FPS]["inputs"]["value"] = int(fps)
    wf[NODE_SEED_A]["inputs"]["noise_seed"] = int(seed)
    wf[NODE_SEED_B]["inputs"]["noise_seed"] = int(seed)
    wf[NODE_SAVE]["inputs"]["filename_prefix"] = filename_prefix

    return wf


def motion_prompt(scene):
    """
    The text LTX should use to drive motion.

    Prefers an explicit motion_prompt; otherwise reuses the image prompt, which
    already describes the shot. LTX needs long descriptive text — short
    keywords produce mush — so the scene description is a reasonable default.
    """
    return (scene.get("description") or scene.get("title") or "").strip()


class VideoService:

    def __init__(self):
        self.scenes = SceneRepository()
        VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    def animate_scene(self, scene, duration=5, width=768, height=512,
                      fps=25, seed=42, negative_prompt=DEFAULT_NEGATIVE):
        """
        Turn a scene's still image into an animated clip.

        Stores the resulting MP4 path on the scene row and returns it.
        Takes roughly 2 minutes per 5-second clip on a DGX Spark.
        """
        image_path = scene.get("image_path")
        if not image_path or not Path(image_path).exists():
            raise RuntimeError(
                "This scene has no image yet. Generate the scene image first."
            )

        # LoadImage reads from ComfyUI's input folder, so push the file across.
        uploaded = comfy_service.upload_image(image_path)

        prefix = (
            f"video/STORY_{scene['story_id']}_SCENE_{scene['scene_number']}"
        )

        workflow = build_workflow(
            image_filename=uploaded,
            prompt=motion_prompt(scene),
            width=width,
            height=height,
            duration=duration,
            fps=fps,
            seed=int(seed) + int(scene.get("scene_number", 0)),
            negative_prompt=negative_prompt,
            filename_prefix=prefix,
        )

        response = comfy_service.queue_prompt(workflow)
        history = comfy_service.wait_for_completion(response["prompt_id"])

        outputs = comfy_service.get_outputs(history)
        if not outputs:
            raise RuntimeError("ComfyUI returned no video for this scene.")

        entry = outputs[0]
        source = COMFY_OUTPUT / entry.get("subfolder", "") / entry["filename"]

        if not source.exists():
            raise RuntimeError(
                f"ComfyUI reported a video at {source}, but it isn't there. "
                "Check that COMFY_OUTPUT points at your ComfyUI output folder."
            )

        dest = VIDEO_DIR / (
            f"story_{scene['story_id']}_scene_{scene['scene_number']}"
            f"{source.suffix}"
        )
        shutil.copy(source, dest)

        self.scenes.update_video(scene["id"], str(dest))
        return str(dest)

    def animate_story(self, story_id, **kwargs):
        """
        Animate every scene in a story that has an image.
        Returns a list of (scene_number, video_path). This is slow — roughly
        2 minutes per scene.
        """
        results = []
        for scene in self.scenes.list_by_story(story_id):
            if not scene.get("image_path"):
                continue
            path = self.animate_scene(scene, **kwargs)
            results.append((scene["scene_number"], path))
        return results

    def video_count(self, story_id):
        """How many scenes in this story already have an animated clip."""
        count = 0
        for scene in self.scenes.list_by_story(story_id):
            path = scene.get("video_path")
            if path and Path(path).exists():
                count += 1
        return count
