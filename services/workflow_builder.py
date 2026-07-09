"""
Workflow Builder
DGX AI Movie Studio
"""

import json
import copy
from pathlib import Path


WORKFLOW_DIR = Path("workflows")


class WorkflowBuilder:

    def __init__(self, workflow_name="sdxl_api.json"):

        workflow_path = WORKFLOW_DIR / workflow_name

        with open(workflow_path, "r") as f:
            self.workflow = json.load(f)

    def set_prompt(self, prompt):

        self.workflow["7"]["inputs"]["text"] = prompt

    def set_negative_prompt(self, negative):

        self.workflow["3"]["inputs"]["text"] = negative

    def set_resolution(self, width, height):

        self.workflow["4"]["inputs"]["width"] = width
        self.workflow["4"]["inputs"]["height"] = height

    def set_seed(self, seed):

        self.workflow["5"]["inputs"]["seed"] = seed

    def set_steps(self, steps):

        self.workflow["5"]["inputs"]["steps"] = steps

    def set_cfg(self, cfg):

        self.workflow["5"]["inputs"]["cfg"] = cfg

    def set_checkpoint(self, checkpoint):

        self.workflow["8"]["inputs"]["ckpt_name"] = checkpoint

    def set_filename(self, filename):

        self.workflow["6"]["inputs"]["filename_prefix"] = filename

    def build(self):

        return copy.deepcopy(self.workflow)
