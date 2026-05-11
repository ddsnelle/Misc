#!/usr/bin/env python3
"""Download a YouTube video's audio and transcribe it with Whisper."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REQUIRED_BINARIES = ("yt-dlp", "ffmpeg", "whisper")


def require(binary: str) -> None:
    if shutil.which(binary) is None:
        sys.exit(
            f"error: required tool '{binary}' not found in PATH. "
            f"Install it before running this script."
        )


def download_audio(url: str, work_dir: Path) -> Path:
    template = str(work_dir / "audio.%(ext)s")
    subprocess.run(
        ["yt-dlp", "-x", "--audio-format", "mp3", "-o", template, url],
        check=True,
    )
    matches = sorted(work_dir.glob("audio.*"))
    if not matches:
        sys.exit("error: yt-dlp finished but produced no audio file.")
    return matches[0]


def transcribe(audio: Path, work_dir: Path, model: str, language: str | None) -> Path:
    cmd = [
        "whisper",
        str(audio),
        "--model", model,
        "--output_format", "txt",
        "--output_dir", str(work_dir),
    ]
    if language:
        cmd += ["--language", language]
    subprocess.run(cmd, check=True)
    transcript = audio.with_suffix(".txt")
    if not transcript.exists():
        sys.exit(f"error: whisper finished but no transcript at {transcript}.")
    return transcript


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Transcribe a YouTube video using yt-dlp + Whisper."
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Force a language code (e.g. en, es). Auto-detect if omitted.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path to write the transcript. Prints to stdout if omitted.",
    )
    args = parser.parse_args()

    for binary in REQUIRED_BINARIES:
        require(binary)

    with tempfile.TemporaryDirectory(prefix="yt-transcribe-") as work:
        work_dir = Path(work)
        audio = download_audio(args.url, work_dir)
        transcript_file = transcribe(audio, work_dir, args.model, args.language)
        text = transcript_file.read_text()

    if args.output:
        Path(args.output).write_text(text)
        print(f"Transcript written to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
