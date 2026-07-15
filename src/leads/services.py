import html
import json
import logging
import urllib.error
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
    payloads = (
        {"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
        {"chat_id": chat_id, "text": text},
    )
    for payload in payloads:
        data = urllib.parse.urlencode(payload).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = json.loads(resp.read().decode("utf-8", errors="replace"))
            if body.get("ok"):
                return True
            logger.error("Telegram API rejected message: %s", body)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            logger.exception("Telegram HTTP error %s: %s", exc.code, detail)
        except Exception:
            logger.exception("Telegram send failed")
    return False


def _plain(value: str) -> str:
    return html.unescape(str(value or "")).strip()


def notify_phone_lead(tel: str, loc: str, channel: str = "") -> None:
    safe_tel = _plain(tel)
    safe_loc = _plain(loc)
    safe_channel = _plain(channel)
    if channel == "agent":
        token = settings.TELEGRAM_AGENT_BOT_TOKEN
        chat_id = settings.TELEGRAM_AGENT_CHAT_ID
    else:
        token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID
    lines = [
        "Нове звернення з сайту BTI Metrium",
        f"Телефон: {safe_tel}",
        f"Зі сторінки: {safe_loc or '—'}",
    ]
    if safe_channel:
        lines.append(f"Канал: {safe_channel}")
    ok = send_telegram(token, chat_id, "\n".join(lines))
    if not ok:
        logger.error(
            "Phone lead Telegram notify failed tel=%s loc=%s channel=%s",
            safe_tel,
            safe_loc,
            safe_channel,
        )


def notify_calculator_lead(data: dict) -> None:
    lines = [
        "Нове звернення з сайту BTI Metrium (калькулятор)",
        f"Ім'я: {_plain(data.get('name', ''))}",
        f"Телефон: {_plain(data.get('tel', ''))}",
        f"Тип: {_plain(data.get('type', ''))}",
        f"Площа: {_plain(data.get('square', ''))} м²",
        f"Вартість: {_plain(data.get('price', ''))}",
        f"Регіон: {_plain(data.get('region', ''))}",
        f"Місто: {_plain(data.get('cityInput', ''))}",
        f"Перепланування: {_plain(data.get('plan', ''))}",
    ]
    ok = send_telegram(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, "\n".join(lines))
    if not ok:
        logger.error("Calculator lead Telegram notify failed tel=%s", _plain(data.get("tel", "")))
    body = "<br>".join(html.escape(line) for line in lines)
    try:
        send_mail(
            "Звернення з сайту BTI Metrium",
            "\n".join(lines),
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, "DEFAULT_FROM_EMAIL") else "noreply@metrium.com.ua",
            [settings.LEADS_EMAIL],
            html_message=body,
            fail_silently=True,
        )
    except Exception:
        logger.exception("Email send failed")


def notify_review_lead(data: dict) -> None:
    msg = (
        "Новий відгук з сайту BTI Metrium\n"
        f"Ім'я: {_plain(data.get('name', ''))}\n"
        f"Коментар: {_plain(data.get('comment', ''))}\n"
        f"Оцінка: {_plain(data.get('rate', ''))}\n"
        f"Зі сторінки: {_plain(data.get('loc', ''))}"
    )
    ok = send_telegram(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, msg)
    if not ok:
        logger.error("Review lead Telegram notify failed")
