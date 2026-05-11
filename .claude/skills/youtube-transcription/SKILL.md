---
name: youtube-transcription
description: Transcribe a YouTube video by downloading its audio and running Whisper. Use when the user provides a YouTube URL and asks for a transcript, summary, or quote extraction from a YouTube video.
---

# YouTube Transcription

Produce a plain-text transcript of a YouTube video by downloading its audio with `yt-dlp` and running OpenAI Whisper on it.

## When to use

Use this skill when the user supplies a YouTube link and asks for any of:

- a transcript / captions
- a summary of the spoken content
- specific quotes, claims, or timestamps from the video

Recognized URL shapes: `https://www.youtube.com/watch?v=<ID>`, `https://youtu.be/<ID>`, `https://www.youtube.com/shorts/<ID>`, `https://m.youtube.com/...`.

## Required tools

The skill needs three external tools. If any are missing, stop and tell the user the exact install command — **do not auto-install**.

| Tool | Install command |
| --- | --- |
| `yt-dlp` | `pip install -U yt-dlp` (or `pipx install yt-dlp`) |
| `ffmpeg` | `apt install ffmpeg` (Linux) / `brew install ffmpeg` (macOS) |
| `whisper` | `pip install -U openai-whisper` |

`openai-whisper` pulls in PyTorch (~1 GB). Mention this so the user isn't surprised.

## Workflow

### 1. Validate the URL

Confirm the URL matches one of the recognized YouTube shapes. If it points at a non-YouTube site, stop and tell the user this skill is YouTube-only.

### 2. Check dependencies

```bash
which yt-dlp ffmpeg whisper
```

If any binary is missing, list the missing ones and the install command from the table above, then stop. Wait for the user to install before proceeding.

### 3. Run the helper script

```bash
python3 .claude/skills/youtube-transcription/transcribe.py "<URL>"
```

Common flags:

- `--model {tiny,base,small,medium,large}` — Whisper model size (default `base`). Use `tiny` for a fast first pass, `small` or `medium` for better accuracy. `large` is high quality but slow on CPU.
- `--language <code>` — force a language (e.g. `en`, `es`, `de`) when auto-detection guesses wrong.
- `--output <path>` — write the transcript to a file instead of stdout.

The script prints progress from `yt-dlp` and `whisper` on stderr; the final transcript goes to stdout (or to `--output`).

### 4. Return the result

Hand the transcript back to the user. If they asked for a summary, quotes, or specific information, work from the transcript text to produce that — don't just dump raw output unless asked.

## Notes & troubleshooting

- **Long videos**: Whisper on CPU runs roughly at real-time-or-slower for `base`, much slower for `medium`/`large`. A 1-hour video can take 10+ minutes. Warn the user before kicking off long runs.
- **GPU**: Whisper auto-uses CUDA if available. No flag needed.
- **`Sign in to confirm you're not a bot`**: yt-dlp is being rate-limited. The user may need to pass cookies via `yt-dlp --cookies-from-browser <browser>` or `--cookies <file>`. The helper script doesn't expose this flag — re-run `yt-dlp` manually with cookies if needed.
- **Age-restricted / private / region-locked videos**: yt-dlp will exit with an explanatory error. Surface it verbatim to the user.
- **Disk space**: audio is downloaded to a temp directory and deleted when the script exits. The transcript itself is small.
