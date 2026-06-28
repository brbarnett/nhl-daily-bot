## Running the bot

```bash
uv run main.py
```

## Adding dependencies

```bash
uv add <package>
```

## Architecture

Single-file bot (`main.py`) that generates a daily NHL digest and posts it to Telegram.

**Flow:** `get_digest()` calls the Anthropic API with the `web_search_20260318` server-side tool (max 5 searches), which lets Claude search the web and compose the digest in one call. The text blocks from the response are joined into the final digest string. Usage stats and cost are printed to stdout, then the digest is sent to Telegram via `send_telegram()`.

**Config:** All secrets are loaded from `.env` via pydantic-settings (`Settings` class). Required vars: `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`. See `.env.example`.

**Cost logging:** After each run, stdout shows token counts, search query count, and an itemized cost breakdown (Sonnet 4.6: $3.00/M input, $15.00/M output, $0.01/search).
