"""
Scene Generator
DGX AI Movie Studio

Turns a single story prompt into a list of scene beats.

This is a DETERMINISTIC, OFFLINE generator (no model download required) so
Phase A works out of the box. It is intentionally isolated behind one small
function so you can upgrade later: to use a real LLM on the DGX (e.g.
TinyLlama / Llama), replace `generate_scenes` with a model-backed version that
returns the same list-of-dicts shape:

    [{"scene_number": 1, "title": "...", "description": "..."}, ...]

Nothing else in the codebase needs to change when you do that swap.
"""


# Classic narrative beats. A slice of these is chosen to match scene_count.
BEATS = [
    ("Opening", "Establish the world and its mood"),
    ("Introduction", "Introduce the main subject in their environment"),
    ("Inciting Incident", "The event that sets the story in motion"),
    ("Rising Action", "Tension builds and the stakes increase"),
    ("Turning Point", "A pivotal discovery or decision"),
    ("Climax", "The dramatic high point of the story"),
    ("Falling Action", "The immediate consequences unfold"),
    ("Resolution", "The world settles into its new state"),
]


def _select_beats(scene_count):
    """Pick `scene_count` beats, spread across the available BEATS."""
    if scene_count <= 0:
        return []
    if scene_count <= len(BEATS):
        step = len(BEATS) / scene_count
        return [BEATS[int(i * step)] for i in range(scene_count)]
    # More scenes than beats: cycle through them.
    return [BEATS[i % len(BEATS)] for i in range(scene_count)]


def generate_scenes(prompt, genre="", style="", scene_count=5):
    """
    Return a list of scene dicts. Each `description` is written so it can be
    fed directly to the image generator as a prompt.
    """
    beats = _select_beats(int(scene_count))
    style_suffix = ", ".join(part for part in [genre, style] if part)

    scenes = []
    for index, (beat_title, beat_desc) in enumerate(beats, start=1):
        description = f"{prompt}. {beat_desc}."
        if style_suffix:
            description = f"{description} Style: {style_suffix}."

        scenes.append({
            "scene_number": index,
            "title": f"Scene {index}: {beat_title}",
            "description": description,
        })

    return scenes
