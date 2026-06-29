from django.test import SimpleTestCase, override_settings

from config.pulse_chat import PULSE_CONNECT_SRC, PULSE_SCRIPT_SRC


class PulseChatCspTests(SimpleTestCase):
    def test_csp_includes_pulse_script_domains(self):
        from django.conf import settings

        script_src = settings.CONTENT_SECURITY_POLICY["DIRECTIVES"]["script-src"]
        for domain in PULSE_SCRIPT_SRC:
            self.assertIn(domain, script_src)

    def test_csp_includes_pulse_websocket(self):
        from django.conf import settings

        connect_src = settings.CONTENT_SECURITY_POLICY["DIRECTIVES"]["connect-src"]
        self.assertIn("wss://lc.pulse.is", connect_src)
        self.assertIn("wss://app.pulse.is", connect_src)

    def test_csp_includes_worker_and_media_for_pulse(self):
        from django.conf import settings

        directives = settings.CONTENT_SECURITY_POLICY["DIRECTIVES"]
        self.assertIn("blob:", directives["worker-src"])
        self.assertIn("blob:", directives["media-src"])

    @override_settings(PULSE_LIVE_CHAT_ENABLED=False, PULSE_LIVE_CHAT_ID="test-id")
    def test_pulse_settings_from_django_conf(self):
        from django.conf import settings

        self.assertFalse(settings.PULSE_LIVE_CHAT_ENABLED)
        self.assertEqual(settings.PULSE_LIVE_CHAT_ID, "test-id")

    def test_default_chat_id_matches_wordpress(self):
        from django.conf import settings

        self.assertEqual(settings.PULSE_LIVE_CHAT_ID, "67a3871d4a8b789c9e0cfdcd")

    def test_pulse_connect_src_has_api_endpoints(self):
        self.assertIn("https://geoip.sendpulse.com", PULSE_CONNECT_SRC)
        self.assertIn("wss://cb-wpayload.pulse.is", PULSE_CONNECT_SRC)
