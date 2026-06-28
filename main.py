import anthropic
import requests
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
One sentence on the biggest NHL story right now.

🔴 RED WINGS
One or two sentences on any Wings news, transactions, or notable updates.

🟢 WILD
One or two sentences on Wild news.

⭐ STARS
One or two sentences on Stars news. Note any Robertson/Larkin trade developments if active.

🎯 PLAYER TO KNOW
Name one player worth knowing today and one sentence on why they matter right now.

🔗 WATCH
Link to one condensed game from NHL.com worth watching.

Keep the entire digest under 300 words. Be direct, no fluff."""

USER_PROMPT = """Search for today's NHL news and produce my morning digest.
Focus on the Red Wings, Wild, and Stars. Check for any overnight transactions,
trade rumors, injury updates, or game results. Find a condensed game link on NHL.com."""


def get_digest() -> tuple[str, anthropic.types.Usage, int]:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20260318", "name": "web_search", "max_uses": 5}],
        messages=[{"role": "user", "content": USER_PROMPT}],
    )

    search_count = sum(
        1 for block in response.content
        if block.type == "server_tool_use" and block.name == "web_search"
    )

    text = "\n".join(
        block.text for block in response.content if block.type == "text"
    ).strip()

    return text, response.usage, search_count


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
    digest, usage, search_count = get_digest()

    input_cost = usage.input_tokens * 3.00 / 1_000_000
    output_cost = usage.output_tokens * 15.00 / 1_000_000
    search_cost = search_count * 0.01  # $10 per 1000 searches
    total_cost = input_cost + output_cost + search_cost

    print(f"Tokens: {usage.input_tokens} in / {usage.output_tokens} out | Searches: {search_count}")
    print(f"Cost: ${input_cost:.4f} input + ${output_cost:.4f} output + ${search_cost:.4f} search = ${total_cost:.4f} total")

    send_telegram(digest)
    print("Digest sent.")
    print(digest)
