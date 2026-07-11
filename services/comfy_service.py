"""
ComfyUI REST Client
DGX AI Movie Studio

Talks to a local ComfyUI instance over HTTP: queue a workflow, wait for it to
finish, and pull the resulting images.

Note on waiting: we poll until real image outputs are attached to the job's
history record, rather than trusting only a 'completed' flag. ComfyUI can set
that flag a moment before the images are attached, which caused intermittent
"No image returned" failures when generating many images in a row.
"""

import json
import time
import requests

COMFY_URL = "http://127.0.0.1:8188"


def queue_prompt(workflow):
    """
    Submit a workflow to ComfyUI. Returns the ComfyUI response (includes
    prompt_id). Raises a clear error if ComfyUI rejects the workflow.
    """
    payload = {"prompt": workflow}
    r = requests.post(f"{COMFY_URL}/prompt", json=payload)

    if r.status_code != 200:
        raise RuntimeError(
            f"ComfyUI rejected the workflow ({r.status_code}): {r.text}"
        )

    data = r.json()
    if "prompt_id" not in data:
        # Validation errors come back here with no prompt_id.
        raise RuntimeError(f"ComfyUI did not accept the workflow: {data}")

    return data


def get_history(prompt_id):
    """Return the history record for a prompt_id, or {} if not present yet."""
    r = requests.get(f"{COMFY_URL}/history/{prompt_id}")
    r.raise_for_status()
    history = r.json()
    return history.get(prompt_id, {})


def _extract_images(history):
    """Collect image entries from a history record's outputs."""
    images = []
    for node in history.get("outputs", {}).values():
        if node.get("images"):
            images.extend(node["images"])
    return images


def wait_for_completion(prompt_id, timeout=600):
    """
    Poll until the prompt has actually produced image outputs.

    Returns the history record once images are present. Raises RuntimeError if
    ComfyUI reports an execution error, or TimeoutError if nothing arrives in
    `timeout` seconds.
    """
    start = time.time()
    grace_polls = 0

    while True:
        history = get_history(prompt_id)

        if history:
            # Success path: images are attached.
            if _extract_images(history):
                return history

            status = history.get("status", {})
            completed = status.get("completed")
            status_str = status.get("status_str")

            # Genuine failure (e.g. bad node, out of memory).
            if completed and status_str == "error":
                raise RuntimeError(
                    "ComfyUI reported an execution error:\n"
                    + json.dumps(status, indent=2)
                )

            # Marked complete but no images yet: allow a short grace window
            # for outputs to attach, then give up with a clear message.
            if completed:
                grace_polls += 1
                if grace_polls > 5:
                    raise RuntimeError(
                        "ComfyUI finished but returned no images. Check that "
                        "the workflow ends in a SaveImage node and that the "
                        "checkpoint loaded correctly."
                    )

        if time.time() - start > timeout:
            raise TimeoutError("ComfyUI generation timed out.")

        time.sleep(1)


def get_images(history):
    """Extract image entries from a completed history record."""
    return _extract_images(history)


def print_history(history):
    print(json.dumps(history, indent=2))
