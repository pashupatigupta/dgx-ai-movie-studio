"""
ComfyUI REST Client
DGX AI Movie Studio
"""

import json
import time
import requests

COMFY_URL = "http://127.0.0.1:8188"


def queue_prompt(workflow):
    """
    Submit workflow to ComfyUI.
    """

    payload = {
        "prompt": workflow
    }

    r = requests.post(
        f"{COMFY_URL}/prompt",
        json=payload
    )

    r.raise_for_status()

    return r.json()


def get_history(prompt_id):
    """
    Get workflow history.
    """

    r = requests.get(
        f"{COMFY_URL}/history/{prompt_id}"
    )

    r.raise_for_status()

    history = r.json()

    if prompt_id in history:
        return history[prompt_id]

    return {}


def wait_for_completion(
    prompt_id,
    timeout=300
):
    """
    Wait until ComfyUI finishes.
    """

    start = time.time()

    while True:

        history = get_history(prompt_id)

        if history:

            status = history.get(
                "status",
                {}
            )

            if status.get("completed"):

                return history

        if time.time() - start > timeout:

            raise TimeoutError(
                "ComfyUI generation timed out."
            )

        time.sleep(1)


def get_images(history):
    """
    Extract images from history.
    """

    outputs = history.get(
        "outputs",
        {}
    )

    images = []

    for node_id in outputs:

        node = outputs[node_id]

        if "images" in node:

            images.extend(
                node["images"]
            )

    return images


def print_history(history):

    print(
        json.dumps(
            history,
            indent=2
        )
    )
