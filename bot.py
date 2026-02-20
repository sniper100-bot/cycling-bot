import os
import re
import datetime as dt
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

# ============ TWILIO SECRETS ============
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID") or os.environ.get("ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN")  or os.environ.get("AUTH_TOKEN")

TWILIO_WA = "whatsapp:+14155238886"
MY_NUMBER = "whatsapp:+40741077285"

# ============ SOURCES (RO) ============
SOURCES = {
    "Eurosport 1": [
        "https://www.gsp.ro/program-tv/eurosport-1-11.html",        # :contentReference[oaicite:2]{index=2}
        "https://m.cinemagia.ro/program-tv/eurosport-1/",           # :contentReference[oaicite:3]{index=3}
        "https://www.cinemagia.ro/program-tv/eurosport-1/",         # :contentReference[oaicite:4]{index=4}
    ],
    "Eurosport 2": [
        "https://www.gsp.ro/program-tv/eurosport-2-7.html",         # :contentReference[oaicite:5]{index=5}
        "https://m.cinemagia.ro/program-tv/eurosport-2/",           # :contentReference[oaicite:6]{index=6}
        "https://www.cinemagia.ro/program-tv/eurosport-2/",         # :contentReference[oaicite:7]{index=7}
    ],
}

KEYWORDS = [
    "ciclism", "cycling", "tour", "turul", "giro", "vuelta",
    "uci", "cyclocross", "ciclocross", "mtb", "bmx"
]

UA = {"User-Agent": "Mozilla/5.0"}

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def _extract_events_from_text(text: str):
    lines = [_norm(x) for x in text.split("\n")]
    lines = [x for x in lines if x]

    events = []
    for i in range(len(lines) - 2):
        # ora validă
        if re.match(r"^\d{1,2}:\d{2}$", lines[i]):
            hour = lines[i]
            title = lines[i + 1] + " " + lines[i + 2]
            low = title.lower()

            # IMPORTANT: acceptă DOAR ciclism
            if any(k in low for k in KEYWORDS):
                # elimină explicit alte sporturi
                if any(x in low for x in ["snooker", "tenis", "fotbal", "handbal", "baschet"]):
                    continue

                events.append((hour, title.strip()))

    # deduplicare + sort
    events = sorted(set(events), key=lambda x: x[0])
    return events

def fetch_channel(channel_name: str):
    for url in SOURCES[channel_name]:
        try:
            r = requests.get(url, headers=UA, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            text = soup.get_text("\n")
            events = _extract_events_from_text(text)
            # dacă nu găsim ciclism, poate layout-ul e altul azi; trecem la următoarea sursă
            if events:
                return events, url
        except Exception:
            continue
    return [], None

def build_message():
    ro_tz = ZoneInfo("Europe/Bucharest")
    now = dt.datetime.now(ro_tz)
    data_f = now.strftime("%d.%m.%Y")

    es1, src1 = fetch_channel("Eurosport 1")
    es2, src2 = fetch_channel("Eurosport 2")

    def fmt(ch, events, src):
        if not events:
            return f"*{ch}*\n— nimic de ciclism detectat azi."
        lines = "\n".join([f"• ⏰ {t} — {title}" for t, title in events])
        return f"*{ch}*\n{lines}"

    msg = (
        f"🚴 *PROGRAM CICLISM (RO) — {data_f}*\n\n"
        f"{fmt('Eurosport 1', es1, src1)}\n\n"
        f"{fmt('Eurosport 2', es2, src2)}"
    )

    # (opțional) dacă vrei să vezi sursa folosită, deblochează:
    # msg += f"\n\n(Surse: ES1={src1 or 'n/a'} | ES2={src2 or 'n/a'})"

    return msg[:1500]

def send_whatsapp(message: str):
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN):
        raise RuntimeError("Lipsesc TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN din Secrets (GitHub).")
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(body=message, from_=TWILIO_WA, to=MY_NUMBER)

if __name__ == "__main__":
    mesaj = build_message()
    send_whatsapp(mesaj)
    print("✅ Trimis pe WhatsApp.")
