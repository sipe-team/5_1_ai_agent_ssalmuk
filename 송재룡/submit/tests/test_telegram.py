from market_agent.clients.telegram import split_telegram_message


def test_split_telegram_message_keeps_short_message_single_chunk() -> None:
    assert split_telegram_message("short message", max_length=100) == ["short message"]


def test_split_telegram_message_splits_on_paragraphs() -> None:
    message = "문단하나" + "\n\n" + "문단둘" + "\n\n" + "문단셋"

    chunks = split_telegram_message(message, max_length=7)

    assert len(chunks) == 3
    assert chunks[0] == "문단하나"
    assert chunks[1] == "문단둘"
    assert chunks[2] == "문단셋"


def test_split_telegram_message_splits_oversized_paragraph() -> None:
    chunks = split_telegram_message("a" * 25, max_length=10)

    assert chunks == ["a" * 10, "a" * 10, "a" * 5]
