"""Pulse.is (SendPulse) live chat — CSP domains and defaults."""

PULSE_LIVE_CHAT_ID_DEFAULT = "67a3871d4a8b789c9e0cfdcd"

# Domains used by cdn.pulse.is/livechat/loader.js → bundle.js and runtime API.
PULSE_SCRIPT_SRC = (
    "https://cdn.pulse.is",
    "https://s3.eu-central-1.amazonaws.com",
)

PULSE_STYLE_SRC = (
    "https://cdn.pulse.is",
)

PULSE_FONT_SRC = (
    "https://cdn.pulse.is",
)

PULSE_CONNECT_SRC = (
    "https://cdn.pulse.is",
    "https://app.pulse.is",
    "wss://app.pulse.is",
    "https://lc.pulse.is",
    "wss://lc.pulse.is",
    "https://cb-wpayload.pulse.is",
    "wss://cb-wpayload.pulse.is",
    "https://geoip.sendpulse.com",
    "https://login.sendpulse.com",
    "https://api.sendpulse.com",
    "https://s3.eu-central-1.amazonaws.com",
)

PULSE_FRAME_SRC = (
    "https://app.pulse.is",
    "https://cdn.pulse.is",
    "https://lc.pulse.is",
)

PULSE_MEDIA_SRC = (
    "https://cdn.pulse.is",
    "https://s3.eu-central-1.amazonaws.com",
    "blob:",
)

PULSE_WORKER_SRC = (
    "blob:",
    "https://cdn.pulse.is",
)
