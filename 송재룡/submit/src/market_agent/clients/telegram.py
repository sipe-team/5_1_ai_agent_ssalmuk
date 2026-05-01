import logging

import httpx

logger = logging.getLogger(__name__)
TELEGRAM_SAFE_MAX_LENGTH = 3500


def split_telegram_message(text: str, max_length: int = TELEGRAM_SAFE_MAX_LENGTH) -> list[str]:
    if len(text) <= max_length:
        return [text]
    chunks: list[str] = []
    current = ""
    for paragraph in text.split("\n\n"):
        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= max_length:
            current = candidate
            continue
        if current:
            chunks.append(current)
            current = ""
        if len(paragraph) <= max_length:
            current = paragraph
            continue
        for start in range(0, len(paragraph), max_length):
            chunks.append(paragraph[start : start + max_length])
    if current:
        chunks.append(current)
    return chunks


class TelegramClient:
    def __init__(self, dry_run: bool = True, bot_token: str | None = None, chat_id: str | None = None) -> None:
        self.dry_run = dry_run
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, text: str) -> None:
        chunks = split_telegram_message(text)
        if self.dry_run:
            logger.info("telegram dry-run message", extra={"message_length": len(text), "chunk_count": len(chunks)})
            for index, chunk in enumerate(chunks, start=1):
                print(f"--- Telegram dry-run chunk {index}/{len(chunks)} ---")
                print(chunk)
            return
        if not self.bot_token or not self.chat_id:
            raise ValueError("Telegram bot token and chat id are required when dry-run is disabled")
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        for chunk in chunks:
            response = httpx.post(url, json={"chat_id": self.chat_id, "text": chunk}, timeout=10)
            response.raise_for_status()
