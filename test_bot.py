import unittest
from unittest.mock import patch
from urllib.error import URLError

import bot


class BotTests(unittest.TestCase):
    def test_messages_and_five_minute_gaps(self):
        events = []
        bot.send_series(
            "secret", "123",
            send=lambda token, method, payload: events.append(payload),
            sleep=lambda seconds: events.append(seconds),
        )
        self.assertEqual(events, [
            {"chat_id": "123", "text": bot.MESSAGES[0]},
            300,
            {"chat_id": "123", "text": bot.MESSAGES[1]},
            300,
            {"chat_id": "123", "text": bot.MESSAGES[2]},
        ])

    def test_network_error_does_not_expose_token(self):
        with patch("bot.urlopen", side_effect=URLError("URL contains secret-token")):
            with self.assertRaises(RuntimeError) as caught:
                bot.telegram_request("secret-token", "sendMessage", {})
        self.assertNotIn("secret-token", str(caught.exception))

    def test_failed_send_stops_series(self):
        with patch("bot.time.sleep") as sleep:
            send = unittest.mock.Mock(side_effect=RuntimeError("Failed"))
            with self.assertRaises(RuntimeError):
                bot.send_series("token", "123", send=send, sleep=sleep)
            self.assertEqual(send.call_count, 1)
            sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
