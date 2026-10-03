"""Send one series of personal Telegram reminders."""

import argparse
import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MESSAGES = (
    "🚫🍾 Я не вживаю алкоголь",
    "🚭 Я не курю",
    "⚖️ Я дотримуюсь дефіциту калорій",
)
INTERVAL_SECONDS = 5 * 60


def telegram_request(token, method, payload):
    request = Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
    except HTTPError as error:
        raise RuntimeError(f"Telegram повернув HTTP {error.code}. Перевірте токен і chat ID.") from None
    except (URLError, TimeoutError, OSError, ValueError):
        # Do not expose the request URL: it contains the bot token.
        raise RuntimeError("Не вдалося отримати відповідь Telegram. Перевірте з'єднання.") from None
    if not result.get("ok"):
        raise RuntimeError("Telegram відхилив запит. Перевірте налаштування бота.")
    return result["result"]


def send_series(token, chat_id, send=telegram_request, sleep=time.sleep):
    for index, message in enumerate(MESSAGES):
        if index:
            sleep(INTERVAL_SECONDS)
        send(token, "sendMessage", {"chat_id": chat_id, "text": message})
        print(f"Повідомлення {index + 1}/3 надіслано.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Показати повідомлення без надсилання")
    args = parser.parse_args()
    if args.dry_run:
        for index, message in enumerate(MESSAGES):
            print(f"+{index * 5:02d} хв: {message}")
        return
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        raise RuntimeError("Додайте TELEGRAM_BOT_TOKEN і TELEGRAM_CHAT_ID у GitHub Actions secrets.")
    send_series(token, chat_id)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
