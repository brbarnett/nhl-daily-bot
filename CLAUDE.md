## Commands

```bash
make run   # run the bot
make fix   # auto-format and lint with ruff
```

```bash
uv add <package>          # add a runtime dependency
uv add --dev <package>    # add a dev dependency
```

## Architecture

Single-file bot ([main.py](main.py)) that generates a daily NHL digest and posts it to Telegram.

**Flow:** `get_digest()` calls the Anthropic API (Haiku 4.5) with the `web_search_20260318` server-side tool (`max_uses=3`, `allowed_callers=["direct"]` — required for Haiku). The text blocks from the response are joined with spaces, punctuation fragments are cleaned up with regex, and everything before the `🏒` header is stripped. A date header is prepended in Python before sending to Telegram.

**Config:** All secrets loaded from `.env` via pydantic-settings (`Settings` class). Required vars: `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`. See [.env.example](.env.example).

**Output format:** Telegram `parse_mode=HTML` — the digest uses `<b>` for bold and `<a href="">` for links. Claude is instructed to use HTML tags only, never Markdown. Player names link to NHL.com profile URLs; story headlines link to source articles. Links are only included when a real URL was found during search.

**Cost logging:** After each run, stdout shows token counts and an itemized cost breakdown. Search cost is estimated at `MAX_SEARCHES * $0.01` (actual count isn't reliably available with `allowed_callers=["direct"]`). Typical run: ~$0.06.
