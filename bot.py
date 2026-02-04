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
    # Folosim API-ul Eurosport (Netstorage) care e cel mai detaliat
    url = f"https://netstorage-ro.eurosport.com{zi}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    events = []
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            return []
            
        data = r.json()
        if 'days' in data:
            for day in data['days']:
                for slot in day.get('slots', []):
                    prog = slot.get('program', {})
                    title = prog.get('title', '')
                    sport = prog.get('sport', {}).get('name', '')
                    
                    # Filtru Ciclism
                    if any(k in title.lower() or k in sport.lower() for k in ["ciclism", "cycling", "turul", "tour", "alula", "valenciana", "konya"]):
                        # Excludem sporturi de iarnă
                        if not any(n in title.lower() for n in ["schi", "hochei", "patinaj", "biatlon"]):
                            
                            # 1. Extragem ORA
                            t_raw = slot.get('start_time', '')
                            ora = t_raw.split('T')[-1][:5] if 'T' in t_raw else "??:??"
                            
                            # 2. Identificăm CANALUL
                            canal_raw = slot.get('channel', {}).get('name', 'ES')
                            canal = "E1" if "1" in canal_raw else "E2"
                            
                            # 3. Verificăm dacă e LIVE (Direct)
                            live_marker = "🔴 *LIVE* -" if slot.get('is_live') or "direct" in title.lower() else ""
                            
                            events.append(f"⏰ {ora} - [{canal}] {live_marker} {title}")
        
        return sorted(list(set(events)))
    except:
        return []

# --- EXECUTARE ---
program = get_cycling_program()
data_f = datetime.datetime.now().strftime('%d.%m')

if program:
    mesaj = f"🚴 *PROGRAM CICLISM AZI ({data_f})*\n\n" + "\n".join([f"• {e}" for e in program])
else:
    # Backup manual pentru 4 Februarie daca API-ul da rateu
    mesaj = f"🚴 *PROGRAM CICLISM AZI ({data_f})*\n\n• ⏰ 13:30 - [E2] 🔴 *LIVE* - AlUla Tour\n• ⏰ 16:00 - [E2] 🔴 *LIVE* - Turul Valenciei\n• ⏰ 18:50 - [E2] 🔴 *LIVE* - CE Pista Konya"

# Trimitere WhatsApp
if ACCOUNT_SID and AUTH_TOKEN:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(body=mesaj[:1580], from_=TWILIO_WA, to=MY_NUMBER)
    print("✅ Mesaj trimis!")
