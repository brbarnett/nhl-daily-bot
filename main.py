import re
import anthropic
import requests
from datetime import date
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        ignore_extra=True,
        frozen=True,
    )

    anthropic_api_key: str = Field(...)
    telegram_bot_token: str = Field(...)
    telegram_chat_id: str = Field(...)


settings = Settings()

SYSTEM_PROMPT = """You are an NHL digest assistant. Your job is to produce a concise daily
morning briefing for a Wings fan who is also following the Minnesota Wild and Dallas Stars.

Always structure your digest exactly like this:

🏒 NHL MORNING DIGEST

📰 TOP STORY
One sentence on the biggest NHL story right now. Link only the 2-4 word story headline (not the whole sentence) to its specific source article URL.

🔴 RED WINGS
One or two sentences on any Wings news, transactions, or notable updates. Link only each player's name to their specific NHL.com player profile URL (e.g. https://www.nhl.com/player/firstname-lastname-ID).

🟢 WILD
One or two sentences on Wild news. Link only player names to their specific NHL.com player profile URLs.

⭐ STARS
One or two sentences on Stars news. Note any Robertson/Larkin trade developments if active. Link only player names to their specific NHL.com player profile URLs.

🎯 PLAYER TO KNOW
Name one player worth knowing today and one sentence on why they matter right now. Link only their name to their specific NHL.com player profile URL.

🔗 WATCH
It is currently the NHL offseason, so skip this section if no condensed games are available.

The output is rendered in Telegram with HTML parse mode. Use only HTML tags for all formatting — never Markdown syntax like **bold** or *italic*:
- Bold: <b>text</b>
- Links: <a href="URL">Player Name</a> or <a href="URL">Headline</a>
Never link an entire sentence. Only link to specific URLs you found during your search — never link to a team homepage or generic page. If you don't have a real player profile URL, just write the name as plain text. Keep the entire digest under 300 words. Be direct, no fluff."""

USER_PROMPT = """Search for today's NHL news and produce my morning digest.
Focus on the Red Wings, Wild, and Stars. Check for any overnight transactions,
trade rumors, injury updates, or game results."""


MAX_SEARCHES = 3


def get_digest() -> tuple[str, anthropic.types.Usage]:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=[
            {
                "type": "web_search_20260318",
                "name": "web_search",
                "max_uses": MAX_SEARCHES,
                "allowed_callers": ["direct"],
            }
        ],
        messages=[{"role": "user", "content": USER_PROMPT}],
    )

    text = " ".join(block.text for block in response.content if block.type == "text")
    text = re.sub(r"\s*\n\s*([,\.!?])", r"\1", text)  # pull punctuation up to previous line
    text = re.sub(r" +([,\.!?])", r"\1", text)  # remove space before punctuation
    text = re.sub(r"\n{3,}", "\n\n", text)  # collapse excessive blank lines
    text = text.strip()

    if "🏒" in text:
        text = text[text.index("🏒") :]

    return text, response.usage


def send_telegram(message: str) -> None:
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": message,
        "parse_mode": "HTML",
    }
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()


if __name__ == "__main__":
    digest, usage = get_digest()

    input_cost = usage.input_tokens * 1.00 / 1_000_000
    output_cost = usage.output_tokens * 5.00 / 1_000_000
    search_cost = MAX_SEARCHES * 0.01
    total_cost = input_cost + output_cost + search_cost

    print(
        f"Tokens: {usage.input_tokens} in / {usage.output_tokens} out | Searches: ≤{MAX_SEARCHES}"
    )
    print(
        f"Cost: ${input_cost:.4f} input + ${output_cost:.4f} output + ${search_cost:.4f} search = ${total_cost:.4f} total"
    )

    dated_digest = f"📅 {date.today().strftime('%B %d, %Y')}\n\n{digest}"
    send_telegram(dated_digest)
    print("Digest sent.")
    print(digest)
