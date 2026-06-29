import html
import logging
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_telegram(token: str, chat_id: str, text: str) -> bool:
    if not token or not chat_id:
        logger.warning("Telegram credentials not configured")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode(
        {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    ).encode()
    req = urllib.request.Request(url, data=data)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        logger.exception("Telegram send failed")
        return False


def notify_phone_lead(tel: str, loc: str, channel: str = "") -> None:
    safe_tel = html.escape(tel)
    safe_loc = html.escape(loc)
    if channel == "agent":
        token = settings.TELEGRAM_AGENT_BOT_TOKEN
        chat_id = settings.TELEGRAM_AGENT_CHAT_ID
    else:
        token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID
    msg = f"*Нове звернення з сайту BTI Metrium*\n*Телефон:* {safe_tel}\n*Зі сторінки:* {safe_loc}"
    send_telegram(token, chat_id, msg)


def notify_calculator_lead(data: dict) -> None:
    lines = [
        "*Нове звернення з сайту BTI Metrium*",
        f"*Ім'я:* {html.escape(data.get('name', ''))}",
        f"*Телефон:* {html.escape(data.get('tel', ''))}",
        f"*Тип:* {html.escape(data.get('type', ''))}",
        f"*Площа:* {html.escape(data.get('square', ''))} м²",
        f"*Вартість:* {html.escape(data.get('price', ''))}",
        f"*Регіон:* {html.escape(data.get('region', ''))}",
        f"*Місто:* {html.escape(data.get('cityInput', ''))}",
        f"*Перепланування:* {html.escape(data.get('plan', ''))}",
    ]
    send_telegram(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, "\n".join(lines))
    body = "<br>".join(lines)
    try:
        send_mail(
            "Звернення з сайту BTI Metrium",
            body,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, "DEFAULT_FROM_EMAIL") else "noreply@metrium.com.ua",
            [settings.LEADS_EMAIL],
            html_message=body,
            fail_silently=True,
        )
    except Exception:
        logger.exception("Email send failed")


def notify_review_lead(data: dict) -> None:
    msg = (
        f"*Нове звернення з сайту BTI Metrium*\n"
        f"*Ім'я:* {html.escape(data.get('name', ''))}\n"
        f"*Коментар:* {html.escape(data.get('comment', ''))}\n"
        f"*Оцінка:* {html.escape(data.get('rate', ''))}\n"
        f"*Зі сторінки:* {html.escape(data.get('loc', ''))}"
    )
    send_telegram(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, msg)
