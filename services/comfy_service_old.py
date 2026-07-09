"""
ComfyUI Service
DGX AI Movie Studio
"""

import json
import time
import requests

COMFY_URL = "http://127.0.0.1:8188"


def load_workflow(path):

    with open(path, "r") as f:
        return json.load(f)


def queue_prompt(workflow):

    payload = {
        "prompt": workflow
    }

    response = requests.post(

        f"{COMFY_URL}/prompt",

        json=payload

    )

    response.raise_for_status()

    return response.json()


def get_history(prompt_id):

    response = requests.get(

        f"{COMFY_URL}/history/{prompt_id}"

    )

    response.raise_for_status()

    return response.json()


def wait_for_completion(prompt_id, timeout=300):

    start = time.time()

    while True:

        history = get_history(prompt_id)

        if prompt_id in history:

            return history[prompt_id]

        if time.time() - start > timeout:

            raise TimeoutError(
                "ComfyUI generation timed out."
            )

        time.sleep(1)
