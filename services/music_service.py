"""
Music Service
DGX AI Movie Studio

Phase F: lay a music bed under a finished movie.

Two separable concerns, deliberately kept apart:

  1. WHERE THE MUSIC COMES FROM  -> MusicProvider (pluggable)
  2. HOW IT'S MIXED INTO THE FILM -> MusicService (ffmpeg; source-agnostic)

Today the only provider is LibraryProvider (tracks you drop in assets/music/).
MusicGenProvider is stubbed with the same interface, so generating a score with
AI later is a one-class change — the mixing code below never needs to know.

Mixing details that matter:
  * The track is looped if it's shorter than the movie, and trimmed to length.
  * It fades in at the start and out at the end.
  * It is DUCKED under the narration via sidechain compression: whenever the
    narrator speaks, the music automatically drops so the voice stays clear,
    then swells back in the gaps. This is what makes it sound scored rather
    than like a song playing behind someone talking.
"""

import subprocess
from abc import ABC, abstractmethod
from pathlib import Path


MUSIC_DIR = Path("assets/music")
SUPPORTED_EXTS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"}

DEFAULT_VOLUME = 0.25
FADE_IN = 2.0
FADE_OUT = 3.0


# ---------------------------------------------------------------------
# Providers: where music comes from
# ---------------------------------------------------------------------

class MusicProvider(ABC):
    """A source of a music track for a movie."""

    @abstractmethod
    def get_track(self, duration=None, prompt=None):
        """Return a path to an audio file, or None if unavailable."""

    @abstractmethod
    def status_message(self):
        """Why this provider can't be used, or None if it's ready."""


class LibraryProvider(MusicProvider):
    """Uses an audio file the user placed in assets/music/."""

    def __init__(self, track_name=None):
        self.track_name = track_name

    def get_track(self, duration=None, prompt=None):
        if not self.track_name:
            return None
        path = MUSIC_DIR / self.track_name
        return str(path) if path.exists() else None

    def status_message(self):
        if not available_tracks():
            return (
                "No music tracks found. Drop .mp3 or .wav files into "
                f"{MUSIC_DIR}/ and they'll appear here."
            )
        if not self.track_name:
            return "No track selected."
        if not (MUSIC_DIR / self.track_name).exists():
            return f"Track not found: {self.track_name}"
        return None


class MusicGenProvider(MusicProvider):
    """
    Placeholder for AI-generated music (Meta's MusicGen).

    To implement: load MusicGen, generate `duration` seconds from `prompt`,
    write a WAV into MUSIC_DIR, and return its path. Because it satisfies the
    same interface, MusicService needs no changes at all.
    """

    def __init__(self, prompt=None):
        self.prompt = prompt

    def get_track(self, duration=None, prompt=None):
        raise NotImplementedError(
            "MusicGen is not wired up yet. Use the music library for now."
        )

    def status_message(self):
        return (
            "AI music generation (MusicGen) is not installed yet. "
            "Using library tracks instead."
        )


def available_tracks():
    """Music files present in assets/music/."""
    if not MUSIC_DIR.exists():
        return []
    return sorted(
        p.name for p in MUSIC_DIR.iterdir()
        if p.suffix.lower() in SUPPORTED_EXTS
    )


# ---------------------------------------------------------------------
# Mixing: how music is laid under the film
# ---------------------------------------------------------------------

def build_music_filter(duration, volume=DEFAULT_VOLUME, duck=True,
                       fade_in=FADE_IN, fade_out=FADE_OUT):
    """
    Build the ffmpeg -filter_complex graph that lays music under a movie.

    Input 0 = the movie (video + narration/silent audio)
    Input 1 = the music track (looped by the caller with -stream_loop)

    Pure function so the graph can be unit-tested without invoking ffmpeg.
    """
    fade_out_start = max(0.0, round(float(duration) - fade_out, 3))

    # Trim the (looped) music to the movie's length, set its level, and fade.
    music_chain = (
        f"[1:a]atrim=0:{duration},asetpts=N/SR/TB,"
        f"volume={volume},"
        f"afade=t=in:st=0:d={fade_in},"
        f"afade=t=out:st={fade_out_start}:d={fade_out}[music]"
    )

    if duck:
        # Sidechain: the narration track (0:a) drives the compressor, pushing
        # the music down whenever the narrator speaks.
        return (
            f"{music_chain};"
            f"[0:a]asplit=2[voice][key];"
            f"[music][key]sidechaincompress="
            f"threshold=0.02:ratio=8:attack=20:release=400[ducked];"
            f"[voice][ducked]amix=inputs=2:duration=first:"
            f"dropout_transition=0,volume=1.6[aout]"
        )

    return (
        f"{music_chain};"
        f"[0:a][music]amix=inputs=2:duration=first:"
        f"dropout_transition=0,volume=1.6[aout]"
    )


def media_duration(path):
    """Duration of an audio/video file in seconds, via ffprobe."""
    proc = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {path}: {proc.stderr.strip()}")
    return float(proc.stdout.strip())


class MusicService:

    def __init__(self, provider=None):
        self.provider = provider or LibraryProvider()
        MUSIC_DIR.mkdir(parents=True, exist_ok=True)

    def status_message(self):
        return self.provider.status_message()

    def mix(self, video_in, video_out, music_path=None,
            volume=DEFAULT_VOLUME, duck=True):
        """
        Lay music under `video_in`, writing `video_out`. Returns video_out.

        The video stream is copied untouched (no re-encode, no quality loss);
        only audio is rebuilt.
        """
        if music_path is None:
            music_path = self.provider.get_track()

        if not music_path:
            raise RuntimeError(
                self.provider.status_message() or "No music track available."
            )

        duration = media_duration(video_in)
        filter_complex = build_music_filter(
            duration, volume=volume, duck=duck
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_in),
            "-stream_loop", "-1", "-i", str(music_path),
            "-filter_complex", filter_complex,
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(video_out),
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            tail = "\n".join(proc.stderr.strip().splitlines()[-15:])
            raise RuntimeError(f"ffmpeg music mix failed:\n{tail}")

        return str(video_out)
