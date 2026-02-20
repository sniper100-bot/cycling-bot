import os
import re
import datetime as dt
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

# ================= TWILIO =================
ACCOUNT_SID = os.environ.get("ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")

TWILIO_WA = "whatsapp:+14155238886"
MY_NUMBER = "whatsapp:+40741077285"

# ================= SURSE PROGRAM TV =================
SOURCES = {
    "Eurosport 1": [
        "https://video.gsp.ro/program-tv/eurosport-1-11.html",
        "https://www.cinemagia.ro/program-tv/eurosport-1/",
    ],
    "Eurosport 2": [
        "https://video.gsp.ro/program-tv/eurosport-2-7.html",
        "https://www.cinemagia.ro/program-tv/eurosport-2/",
    ],
}

# ================= FILTRE =================
CYCLING_KEYWORDS = [
    "ciclism", "cycling", "tour", "turul", "giro", "vuelta",
    "uci", "uae tour", "paris-nice", "tirreno", "romandie",
    "dauphine", "volta", "catalunya", "cyclocross", "ciclocross"
]

EXCLUDE_WORDS = [
    "snooker", "tenis", "fotbal", "handbal", "baschet", "golf",
    "schi", "biatlon", "bob", "snowboard", "curling", "patinaj",
    "olimpi", "milano cortina", "cele mai citite", "ultima oră"
]

# ================= PARSER =================
def extract_events(text: str):

    text = re.sub(r"\s+", " ", text)

    matches = re.findall(r"(\d{1,2}:\d{2})\s+(.*?)(?=\s+\d{1,2}:\d{2}\s+|$)", text)

    events = []

    for hour, title in matches:

        title_clean = title.strip(" -•|")
        low = title_clean.lower()

        if not any(k in low for k in CYCLING_KEYWORDS):
            continue

        if any(x in low for x in EXCLUDE_WORDS):
            continue

        # ignoră reluările nocturne
        h = int(hour.split(":")[0])
        if h < 7:
            continue

        # curățări
        title_clean = re.sub(r"\b(luni|marti|miercuri|joi|vineri|sambata|duminica)\b", "", title_clean, flags=re.I)
        title_clean = re.sub(r"(etapa [^ ]+).*?\1", r"\1", title_clean, flags=re.I)

        events.append((hour, title_clean.strip()))

    # elimină duplicate -> păstrează prima apariție
    unique = {}
    for hour, title in events:
        key = re.sub(r"etapa.*", "", title.lower())
        if key not in unique:
            unique[key] = (hour, title)

    return sorted(unique.values(), key=lambda x: x[0])

# ================= FETCH =================
def fetch_channel(channel):

    headers = {"User-Agent": "Mozilla/5.0"}

    for url in SOURCES[channel]:
        try:
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code != 200:
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            text = soup.get_text(" ")

            events = extract_events(text)

            if events:
                return events

        except Exception:
            continue

    return []

# ================= FORMAT =================
def format_channel(name, events):

    if not events:
        return f"*{name}*\n— nimic azi"

    lines = "\n".join([f"• ⏰ {h} — {t}" for h, t in events])
    return f"*{name}*\n{lines}"

# ================= MAIN =================
def main():

    today = dt.datetime.now().strftime("%d.%m.%Y")

    es1 = fetch_channel("Eurosport 1")
    es2 = fetch_channel("Eurosport 2")

    message = f"🚴 *PROGRAM CICLISM (RO) — {today}*\n\n"
    message += format_channel("Eurosport 1", es1)
    message += "\n\n"
    message += format_channel("Eurosport 2", es2)

    if ACCOUNT_SID and AUTH_TOKEN:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        client.messages.create(
            body=message[:1500],
            from_=TWILIO_WA,
            to=MY_NUMBER
        )
        print("Mesaj trimis OK")
    else:
        print("Lipsesc secretele Twilio")

# ================= RUN =================
if __name__ == "__main__":
    main()
