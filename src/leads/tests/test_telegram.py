import json
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings

from src.leads.services import notify_phone_lead, send_telegram


class SendTelegramTests(SimpleTestCase):
    @override_settings(TELEGRAM_BOT_TOKEN="token", TELEGRAM_CHAT_ID="123")
    def test_send_telegram_checks_api_ok_flag(self):
        mock_resp = MagicMock()
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.__exit__.return_value = False
        mock_resp.read.return_value = json.dumps({"ok": False, "description": "bad"}).encode()

        with patch("src.leads.services.urllib.request.urlopen", return_value=mock_resp) as urlopen:
            self.assertFalse(send_telegram("token", "123", "hello *broken_ markdown_"))
            self.assertTrue(urlopen.called)

    @override_settings(TELEGRAM_BOT_TOKEN="token", TELEGRAM_CHAT_ID="123")
    def test_send_telegram_success(self):
        mock_resp = MagicMock()
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.__exit__.return_value = False
        mock_resp.read.return_value = json.dumps({"ok": True, "result": {}}).encode()

        with patch("src.leads.services.urllib.request.urlopen", return_value=mock_resp):
            self.assertTrue(send_telegram("token", "123", "hello"))

    @override_settings(
        TELEGRAM_BOT_TOKEN="token",
        TELEGRAM_CHAT_ID="123",
        TELEGRAM_AGENT_BOT_TOKEN="",
        TELEGRAM_AGENT_CHAT_ID="",
    )
    def test_notify_phone_lead_plain_text_includes_channel_and_loc(self):
        with patch("src.leads.services.send_telegram", return_value=True) as send:
            notify_phone_lead(
                "+380501112233",
                'Офіційний сайт БТІ | /bti-official/',
                "cms-banner",
            )
            send.assert_called_once()
            text = send.call_args.args[2]
            self.assertIn("+380501112233", text)
            self.assertIn("Офіційний сайт БТІ | /bti-official/", text)
            self.assertIn("cms-banner", text)
            self.assertNotIn("*Телефон:*", text)
