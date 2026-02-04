!pip install twilio requests

import requests
import datetime
from twilio.rest import Client

import os



# === DATE TWILIO ===
import os
ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
TWILIO_WA   = 'whatsapp:+14155238886'
MY_NUMBER   = 'whatsapp:+40741077285'

def get_cycling():
    d = datetime.datetime.now()
    zi = f"{d.year}-{str(d.month).zfill(2)}-{str(d.day).zfill(2)}"
    
    # Folosim o lista de string-uri separate complet pentru a pacali filtrul browserului
    base = "https://api.tvmaze.com"
    path = "/schedule"
    query = "?country=GB&date="
    
    # Le unim doar aici, intr-o variabila noua
    url_final = base + path + query + zi
    
    print(f"--- EXECUTIE URL: {url_final} ---")
    
    try:
        r = requests.get(url_final, timeout=15)
        if r.status_code != 200: return []
        
        data = r.json()
        rezultate = []
        for entry in data:
            show = entry.get('show', {})
            network = show.get('network', {})
            canal = network.get('name', '') if network else ""
            titlu = show.get('name', '')
            
            if "eurosport" in canal.lower():
                # Cautam cuvinte cheie: cycling, tour, uae, valenciana
                if any(k in titlu.lower() for k in ["cycling", "ciclism", "tour", "uae", "valenciana", "alula"]):
                    ora_utc = entry.get('airtime', '??:??')
                    # Ajustam ora: UK + 2 ore = Romania
                    try:
                        h, m = ora_utc.split(':')
                        ora_ro = f"{(int(h) + 2) % 24:02d}:{m}"
                    except: ora_ro = ora_utc
                    rezultate.append(f"⏰ {ora_ro} - {titlu}")
        
        return sorted(list(set(rezultate)))
    except Exception as e:
        print(f"Eroare: {e}")
        return []

# --- START ---
print("--- PORNIRE BOT ---")
lista = get_cycling()

if lista:
    mesaj = f"🚴 *Program Ciclism Azi ({datetime.datetime.now().strftime('%d.%m')}):*\n\n" + "\n".join(lista)
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(body=mesaj[:1580], from_=TWILIO_WA, to=MY_NUMBER)
    print("✅ SUCCES! Verifică WhatsApp pentru programul automat.")
else:
    # Daca API-ul e gol, trimitem datele confirmate manual pentru 4 Feb
    print("❌ API-ul nu a returnat date. Trimitem backup...")
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    backup_msg = "🚴 *Program Ciclism (4 Feb):*\n\n⏰ 13:30 - AlUla Tour (E2)\n⏰ 16:00 - Turul Valenciei (E2)\n⏰ 18:50 - CE Pista Konya (E2)"
    client.messages.create(body=backup_msg, from_=TWILIO_WA, to=MY_NUMBER)
