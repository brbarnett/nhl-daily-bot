# NHL Daily Bot

Sends a daily NHL morning digest to a Telegram chat using Claude AI with live web search.

## Setup

1. Copy `.env.example` to `.env` and fill in your credentials:

   ```
   ANTHROPIC_API_KEY=...
   TELEGRAM_BOT_TOKEN=...
   TELEGRAM_CHAT_ID=...
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

## Usage

```bash
uv run main.py
```

The bot searches for current NHL news, generates a structured digest focused on the Red Wings, Wild, and Stars, posts it to Telegram, and prints a cost breakdown to stdout.

## Digest format

- Top story
- Team updates (Red Wings, Wild, Stars)
- Player to know
- Condensed game link from NHL.com
