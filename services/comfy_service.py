"""
ComfyUI REST Client
DGX AI Movie Studio

Talks to a local ComfyUI instance over HTTP: upload inputs, queue a workflow,
wait for it to finish, and pull the resulting media.

Note on waiting: we poll until real outputs are attached to the job's history
record, rather than trusting only a 'completed' flag. ComfyUI can set that flag
a moment before the outputs are attached, which caused intermittent "nothing
returned" failures when generating many items in a row.
"""

import json
import time
from pathlib import Path

import requests

COMFY_URL = "http://127.0.0.1:8188"

# History output keys that carry produced media, across node types.
# SaveImage uses "images"; SaveVideo/animation nodes vary.
OUTPUT_KEYS = ("images", "video", "videos", "gifs", "audio")


def upload_image(image_path, overwrite=True):
    """
    Upload a local image into ComfyUI's input folder so a LoadImage node can
    reference it by filename. Returns the filename ComfyUI stored it under.

    This matters for video: LoadImage reads from ComfyUI/input/, not from an
    arbitrary path on disk, so scene images must be pushed across first.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    with open(path, "rb") as f:
        files = {"image": (path.name, f, "image/png")}
        data = {"overwrite": "true" if overwrite else "false"}
        r = requests.post(f"{COMFY_URL}/upload/image", files=files, data=data)

    if r.status_code != 200:
        raise RuntimeError(
            f"ComfyUI rejected the image upload ({r.status_code}): {r.text}"
        )

    return r.json().get("name", path.name)


def queue_prompt(workflow):
    """
    Submit a workflow to ComfyUI. Returns the response (includes prompt_id).
    Raises a clear error if ComfyUI rejects the workflow.
    """
    r = requests.post(f"{COMFY_URL}/prompt", json={"prompt": workflow})

    if r.status_code != 200:
        raise RuntimeError(
            f"ComfyUI rejected the workflow ({r.status_code}): {r.text}"
        )

    data = r.json()
    if "prompt_id" not in data:
        raise RuntimeError(f"ComfyUI did not accept the workflow: {data}")

    return data


def get_history(prompt_id):
    """Return the history record for a prompt_id, or {} if not present yet."""
    r = requests.get(f"{COMFY_URL}/history/{prompt_id}")
    r.raise_for_status()
    return r.json().get(prompt_id, {})


def _extract_outputs(history):
    """Collect produced media entries from a history record's outputs."""
    results = []
    for node in history.get("outputs", {}).values():
        for key in OUTPUT_KEYS:
            if node.get(key):
                results.extend(node[key])
    return results


def wait_for_completion(prompt_id, timeout=1800):
    """
    Poll until the prompt has actually produced outputs.

    Returns the history record. Raises RuntimeError if ComfyUI reports an
    execution error, or TimeoutError if nothing arrives in `timeout` seconds.

    The default timeout is generous because video generation is slow: a single
    LTX clip takes minutes, and the first run of a session also pays the cost
    of loading tens of GB of weights.
    """
    start = time.time()
    grace_polls = 0

    while True:
        history = get_history(prompt_id)

        if history:
            if _extract_outputs(history):
                return history

            status = history.get("status", {})
            completed = status.get("completed")

            if completed and status.get("status_str") == "error":
                raise RuntimeError(
                    "ComfyUI reported an execution error:\n"
                    + json.dumps(status, indent=2)
                )

            # Marked complete but nothing attached yet: allow a short grace
            # window for outputs to land, then fail with a clear message.
            if completed:
                grace_polls += 1
                if grace_polls > 5:
                    raise RuntimeError(
                        "ComfyUI finished but returned no output. Check that "
                        "the workflow ends in a Save node."
                    )

        if time.time() - start > timeout:
            raise TimeoutError(
                f"ComfyUI generation timed out after {timeout}s."
            )

        time.sleep(2)


def get_images(history):
    """Extract output entries from a completed history record."""
    return _extract_outputs(history)


# Backwards-compatible alias: video jobs read better with this name.
get_outputs = get_images


def print_history(history):
    print(json.dumps(history, indent=2))
