import os
import requests
import datetime
from twilio.rest import Client

# Citim secretele din GitHub Actions
ACCOUNT_SID = os.environ.get('ACCOUNT_SID')
AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
TWILIO_WA = 'whatsapp:+14155238886'
MY_NUMBER = 'whatsapp:+40741077285'

def get_cycling_program():
    zi = datetime.datetime.now().strftime('%Y-%m-%d')
    # URL-ul de mai jos este simbolic, Eurosport nu are un API JSON public direct la acest link.
    # Dacă returnează 404 sau eroare, botul va trimite mesajul de "Nu am găsit".
    url = f"https://www.eurosport.ro{zi}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    events = []
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            return []
            
        data = r.json()
        # Logica de filtrare (depinde de structura JSON a Eurosport)
        if 'slots' in data:
            for slot in data.get('slots', []):
                title = slot.get('program', {}).get('title', '').lower()
                if any(k in title for k in ["ciclism", "cycling", "tour", "turul"]):
                    ora = slot.get('start_time', '').split('T')[-1][:5]
                    events.append(f"⏰ {ora} - {title.title()}")
        
        return sorted(list(set(events)))
    except Exception as e:
        print(f"Eroare la parsare: {e}")
        return []

# --- EXECUTARE ---
try:
    program = get_cycling_program()
    data_f = datetime.datetime.now().strftime('%d.%m')

    if program:
        mesaj = f"🚴 *PROGRAM CICLISM AZI ({data_f})*\n\n" + "\n".join([f"• {e}" for e in program])
    else:
        # FĂRĂ TEXT VECHI - Mesaj de siguranță
        mesaj = f"🚴 *INFO CICLISM ({data_f})*\n\nNu am găsit transmisiuni noi în programul Eurosport pentru astăzi."

    # Trimitere WhatsApp
    if ACCOUNT_SID and AUTH_TOKEN:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        client.messages.create(body=mesaj[:1580], from_=TWILIO_WA, to=MY_NUMBER)
        print("✅ Mesaj trimis!")
    else:
        print("❌ Lipsesc secretele Twilio!")

except Exception as e:
    print(f"❌ Eroare critică: {e}")
