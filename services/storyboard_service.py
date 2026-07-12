"""
Storyboard Service
DGX AI Movie Studio

Orchestration layer for Phase A. Sits between the UI and the
repository / image / generator layers. The UI calls only this service.
"""

from repositories.story_repository import StoryRepository
from repositories.scene_repository import SceneRepository
from services.scene_generator import generate_scenes
from services.image_service import ImageService


DEFAULT_NEGATIVE = "blurry, low quality, distorted, watermark, text"
DEFAULT_CHECKPOINT = "sd_xl_base_1.0.safetensors"


class StoryboardService:

    def __init__(self):
        self.stories = StoryRepository()
        self.scenes = SceneRepository()
        self.image_service = ImageService()

    # ---- story lifecycle -------------------------------------------

    def create_storyboard(self, title, prompt, genre, style, scene_count):
        """
        Create a story row plus its generated scene rows.
        Returns the new story_id.
        """
        story_id = self.stories.create(
            title=title,
            prompt=prompt,
            genre=genre,
            style=style,
            scene_count=int(scene_count),
            status="storyboard_ready",
        )

        for scene in generate_scenes(prompt, genre, style, scene_count):
            self.scenes.create(
                story_id=story_id,
                scene_number=scene["scene_number"],
                title=scene["title"],
                description=scene["description"],
                narration_text=scene.get("narration_text"),
                status="draft",
            )

        return story_id

    def list_stories(self):
        return self.stories.list_all()

    def get_story(self, story_id):
        return self.stories.get(story_id)

    def get_scenes(self, story_id):
        return self.scenes.list_by_story(story_id)

    def update_scene(self, scene_id, title, description,
                     narration_text=None):
        self.scenes.update_content(
            scene_id, title, description, narration_text
        )

    def delete_story(self, story_id):
        self.scenes.delete_by_story(story_id)
        self.stories.delete(story_id)

    # ---- image generation ------------------------------------------

    def generate_scene_image(
        self,
        scene,
        width=1024,
        height=1024,
        steps=30,
        cfg=8.0,
        seed=12345,
        checkpoint=DEFAULT_CHECKPOINT,
        negative_prompt=DEFAULT_NEGATIVE,
    ):
        """
        Generate one image for a scene via the existing ImageService, store the
        resulting path on the scene row, and return the path.

        The seed is offset by scene_number so each scene renders a distinct
        frame while staying reproducible.
        """
        effective_seed = int(seed) + int(scene.get("scene_number", 0))

        result = self.image_service.generate_image(
            prompt=scene["description"],
            negative_prompt=negative_prompt,
            width=int(width),
            height=int(height),
            steps=int(steps),
            cfg=float(cfg),
            seed=effective_seed,
            checkpoint=checkpoint,
            filename=(
                f"STORY_{scene['story_id']}_SCENE_{scene['scene_number']}"
            ),
        )

        self.scenes.update_image(
            scene_id=scene["id"],
            image_path=result["image"],
        )

        return result["image"]

    def generate_all_images(self, story_id, **kwargs):
        """
        Generate an image for every scene in a story.
        Returns a list of (scene_number, image_path).
        """
        results = []
        for scene in self.scenes.list_by_story(story_id):
            path = self.generate_scene_image(scene, **kwargs)
            results.append((scene["scene_number"], path))

        self.stories.update_status(story_id, "images_ready")
        return results
