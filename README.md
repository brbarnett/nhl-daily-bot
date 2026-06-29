# NHL Daily Bot

Sends a daily NHL morning digest to a Telegram chat using Claude AI with live web search. Focused on the Red Wings, Wild, and Stars.

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
make run
```

Each run costs roughly $0.06 and prints a token/cost breakdown to stdout. The digest is sent to Telegram with a date header.

## Digest format

- Date header
- Top story (linked to source)
- Team updates: Red Wings, Wild, Stars (player names linked to NHL.com profiles)
- Player to know
- Condensed game link (skipped during offseason)
