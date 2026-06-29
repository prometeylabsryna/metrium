from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Перевірка готовності Pulse.is live chat до деплою"

    def handle(self, *args, **options):
        csp = settings.CONTENT_SECURITY_POLICY["DIRECTIVES"]
        pulse_domains = set()

        for directive in ("script-src", "connect-src", "frame-src", "style-src"):
            for value in csp.get(directive, ()):
                if "pulse" in value or "sendpulse" in value:
                    pulse_domains.add(value)

        self.stdout.write(self.style.SUCCESS("Pulse.is live chat — pre-deploy check"))
        self.stdout.write("")

        enabled = settings.PULSE_LIVE_CHAT_ENABLED
        chat_id = settings.PULSE_LIVE_CHAT_ID
        site_url = settings.SITE_URL

        self.stdout.write(f"  PULSE_LIVE_CHAT_ENABLED: {enabled}")
        self.stdout.write(f"  PULSE_LIVE_CHAT_ID:      {chat_id or '(empty)'}")
        self.stdout.write(f"  SITE_URL:                {site_url}")
        self.stdout.write(f"  CSP pulse domains:       {len(pulse_domains)}")
        self.stdout.write("")

        ok = True

        if not enabled:
            self.stdout.write(self.style.WARNING("  [!] Chat disabled via PULSE_LIVE_CHAT_ENABLED=False"))
        elif not chat_id:
            self.stdout.write(self.style.ERROR("  [x] PULSE_LIVE_CHAT_ID is empty"))
            ok = False

        required_connect = {"wss://lc.pulse.is", "https://cdn.pulse.is"}
        missing = required_connect - pulse_domains
        if missing:
            self.stdout.write(self.style.ERROR(f"  [x] Missing CSP connect-src: {', '.join(sorted(missing))}"))
            ok = False

        if "'unsafe-eval'" not in csp.get("script-src", ()):
            self.stdout.write(self.style.ERROR("  [x] script-src needs 'unsafe-eval' for Pulse bundle"))
            ok = False

        if ok and enabled:
            self.stdout.write(self.style.SUCCESS("  [ok] Configuration looks ready"))
            self.stdout.write("")
            self.stdout.write("After deploy:")
            self.stdout.write(f"  1. Open {site_url} — chat button bottom-left (mobile/tablet)")
            self.stdout.write("  2. DevTools Console — no CSP errors for pulse.is")
            self.stdout.write("  3. Network → WS — wss://lc.pulse.is status 101")
            self.stdout.write("  4. SendPulse panel — domain allowed for widget")
            self.stdout.write("  5. iPhone Safari — chat not overlapping call/Telegram FABs")

        if not ok:
            self.stdout.write("")
            self.stdout.write(self.style.ERROR("Fix issues above before deploy."))
