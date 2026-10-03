"""Read the bot token privately and find private chats that sent /start."""

from getpass import getpass

from bot import telegram_request


def main():
    print("Спочатку відкрийте свого бота в Telegram і надішліть /start.")
    token = getpass("Токен від BotFather (введення приховане): ").strip()
    updates = telegram_request(token, "getUpdates", {})
    chats = {}
    for update in updates:
        message = update.get("message", {})
        chat = message.get("chat", {})
        if chat.get("type") == "private":
            chats[chat["id"]] = chat.get("first_name", "")
    if not chats:
        print("Чатів не знайдено. Надішліть боту /start ще раз і повторіть команду.")
    for chat_id, name in chats.items():
        print(f"{name}: TELEGRAM_CHAT_ID={chat_id}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        raise SystemExit(str(error)) from None
