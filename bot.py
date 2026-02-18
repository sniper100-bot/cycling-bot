import os
import requests
import datetime
from twilio.rest import Client

# Configurare Secrete
ACCOUNT_SID = os.environ.get('ACCOUNT_SID')
AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
TWILIO_WA = 'whatsapp:+14155238886'
MY_NUMBER = 'whatsapp:+40741077285'

def get_cycling_program():
    zi = datetime.datetime.now().strftime('%Y-%m-%d')
    # Încercăm un URL mai simplu pentru Eurosport (poate fi instabil)
    url = f"https://www.eurosport.ro{zi}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    events = []
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # Căutăm meciuri în structura Eurosport
            for slot in data.get('slots', []):
                title = slot.get('program', {}).get('title', '').lower()
                if any(k in title for k in ["ciclism", "cycling", "tour", "turul"]):
                    ora = slot.get('start_time', '').split('T')[-1][:5]
                    events.append(f"⏰ {ora} - {title.title()}")
    except Exception as e:
        print(f"Eroare API: {e}")
    
    return sorted(list(set(events)))

# --- EXECUTARE ---
try:
    program = get_cycling_program()
    data_f = datetime.datetime.now().strftime('%d.%m')

    if program:
        mesaj = f"🚴 *PROGRAM CICLISM AZI ({data_f})*\n\n" + "\n".join([f"• {e}" for e in program])
    else:
        # Mesaj de TEST ca să verificăm dacă Twilio merge
        mesaj = f"🚴 *BOT CICLISM ({data_f})*\n\nNu am găsit nicio cursă în programul Eurosport pentru astăzi. Verifică manual pe site!"

    # Trimitere WhatsApp
    if ACCOUNT_SID and AUTH_TOKEN:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        client.messages.create(body=mesaj[:1500], from_=TWILIO_WA, to=MY_NUMBER)
        print("✅ Script finalizat cu succes!")
    else:
        print("❌ Lipsesc ACCOUNT_SID sau AUTH_TOKEN din GitHub Secrets!")

except Exception as e:
    print(f"❌ Eroare fatală în script: {e}")

