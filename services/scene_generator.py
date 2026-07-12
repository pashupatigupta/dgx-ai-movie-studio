"""
Scene Generator
DGX AI Movie Studio

Turns a single story prompt into scene beats. Each beat produces TWO texts,
because they do different jobs:

    description     -> the IMAGE prompt (style tags, keywords; fed to SDXL)
    narration_text  -> the SPOKEN line  (plain prose; fed to Piper TTS)

Mixing these was a mistake: narrating an image prompt means reading style tags
like "photorealistic, 8K" aloud, which sounds like a machine reading metadata
rather than a film narrator.

This is a DETERMINISTIC, OFFLINE generator (no model download required) so it
works out of the box. It is deliberately isolated behind one function so you
can later swap in an LLM on the DGX that returns the same shape:

    [{"scene_number": 1, "title": ..., "description": ..., "narration_text": ...}]

Nothing else in the codebase needs to change when you do that swap.
"""


# (beat name, image direction, narration line template)
BEATS = [
    ("Opening",
     "wide establishing shot, the world at rest",
     "It begins here, in a world that does not yet know what is coming."),
    ("Introduction",
     "close portrait, subject in their environment",
     "At the centre of it all, one figure moves through the ordinary hours."),
    ("Inciting Incident",
     "dramatic moment of discovery, sharp light",
     "And then, everything changes."),
    ("Rising Action",
     "tense atmosphere, deep shadows, motion",
     "What was small begins to grow, and the world starts to notice."),
    ("Turning Point",
     "pivotal confrontation, strong contrast",
     "There is a moment when turning back is no longer possible. This is it."),
    ("Climax",
     "epic wide shot, peak intensity, dramatic sky",
     "Everything that has happened has been leading to this."),
    ("Falling Action",
     "aftermath, quiet dust and stillness",
     "In the silence that follows, the cost becomes clear."),
    ("Resolution",
     "calm final frame, soft golden light",
     "And so the world settles, changed, into something new."),
]


def _select_beats(scene_count):
    """Pick `scene_count` beats, spread across the available BEATS."""
    if scene_count <= 0:
        return []
    if scene_count <= len(BEATS):
        step = len(BEATS) / scene_count
        return [BEATS[int(i * step)] for i in range(scene_count)]
    return [BEATS[i % len(BEATS)] for i in range(scene_count)]


def generate_scenes(prompt, genre="", style="", scene_count=5):
    """Return a list of scene dicts (image prompt + spoken narration line)."""
    beats = _select_beats(int(scene_count))
    style_suffix = ", ".join(part for part in [genre, style] if part)

    scenes = []
    for index, (beat_title, image_direction, narration) in enumerate(
        beats, start=1
    ):
        description = f"{prompt}, {image_direction}"
        if style_suffix:
            description = f"{description}, {style_suffix}"

        scenes.append({
            "scene_number": index,
            "title": f"Scene {index}: {beat_title}",
            "description": description,
            "narration_text": narration,
        })

    return scenes
