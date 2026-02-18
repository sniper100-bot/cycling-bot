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
    def get_cycling_program():
    zi = datetime.datetime.now().strftime('%Y-%m-%d')
    # ATENȚIE: Acest URL trebuie să fie unul valid. 
    # Eurosport folosește acum adesea: https://www.eurosport.ro{zi}
    url = f"https://www.eurosport.ro{zi}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    events = []
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            return []
            
        data = r.json()
        # Structura JSON de la Eurosport se schimbă des. 
        # Trebuie verificat în "Inspect Element" -> "Network" pe site-ul lor ce chei apar.
        # ... (restul logicii de filtrare) ...
        return sorted(list(set(events)))
    except Exception as e:
        print(f"Eroare API: {e}")
        return []

# --- EXECUTARE ---
program = get_cycling_program()
data_f = datetime.datetime.now().strftime('%d.%m')

if program:
    mesaj = f"🚴 *PROGRAM CICLISM AZI ({data_f})*\n\n" + "\n".join(program)
else:
    # MODIFICARE AICI: Nu mai pune text fix vechi!
    mesaj = f"🚴 *PROGRAM CICLISM ({data_f})*\n\nNu s-au găsit transmisii live în baza de date Eurosport pentru azi.

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
