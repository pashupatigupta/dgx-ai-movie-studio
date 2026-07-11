"""
Storyboard smoke test
DGX AI Movie Studio

Exercises the Phase A data path end-to-end WITHOUT generating images:
create a storyboard -> read story -> read scenes -> delete (clean up).

Run from the project root:
    python -m tests.test_storyboard

It writes to the real movie_studio.db but deletes everything it creates,
so it leaves the database as it found it.
"""

from services.storyboard_service import StoryboardService


def main():
    service = StoryboardService()

    print("1. Creating a test storyboard...")
    story_id = service.create_storyboard(
        title="__TEST_STORY__",
        prompt="A lighthouse keeper befriends a sea creature",
        genre="Fantasy",
        style="painterly, warm light",
        scene_count=4,
    )
    assert isinstance(story_id, int), "create_storyboard should return an id"
    print(f"   created story #{story_id}")

    print("2. Reading the story back...")
    story = service.get_story(story_id)
    assert story is not None, "story should exist"
    assert story["title"] == "__TEST_STORY__"
    assert story["scene_count"] == 4
    print(f"   title={story['title']!r} status={story['status']!r}")

    print("3. Reading its scenes...")
    scenes = service.get_scenes(story_id)
    assert len(scenes) == 4, f"expected 4 scenes, got {len(scenes)}"
    for scene in scenes:
        assert scene["description"], "each scene needs a description"
        print(f"   #{scene['scene_number']}: {scene['title']}")

    print("4. Editing a scene...")
    first = scenes[0]
    service.update_scene(first["id"], first["title"], "EDITED DESCRIPTION")
    reread = service.get_scenes(story_id)[0]
    assert reread["description"] == "EDITED DESCRIPTION"
    print("   edit persisted")

    print("5. Cleaning up (deleting test story and scenes)...")
    service.delete_story(story_id)
    assert service.get_story(story_id) is None
    assert service.get_scenes(story_id) == []
    print("   cleaned up")

    print("\nALL STORYBOARD TESTS PASSED")


if __name__ == "__main__":
    main()
