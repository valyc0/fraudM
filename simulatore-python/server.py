# pip install flask google-generativeai

# Workflow:
# 1. Genera il codice Python:
#    curl -X POST http://localhost:5000/generate_code -H "Content-Type: application/json" \
#      -d '{"rule": "Genera un CSV con 5000 chiamate normali randomiche"}'
#
# 2. Se vuoi vedere la preview (100 records):
#    python /data/preview_script.py
#
# 3. Se la preview è ok, genera il file completo:
#    python /data/generate_script.py
#
# Esempi di pattern:
# - Pattern normale: {"rule": "Genera un CSV con 5000 chiamate normali randomiche"}
# - Pattern periodico: {"rule": "Genera un CSV ogni 5 secondi con chiamate normali"}
# - Pattern fraudolento: {"rule": "CSV con caller che chiama 20 numeri in 2 minuti"}

from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import subprocess
import random
import datetime
import pytz

app = Flask(__name__)

# Imposta la chiave API di Gemini da variabile d'ambiente
GENAI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GENAI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")
genai.configure(api_key=GENAI_API_KEY)

# Contesto fisso per Gemini
CONTEXT = """
Sei un assistente AI specializzato nella generazione di codice Python per simulare pattern di chiamate telefoniche.
Genera SOLO il codice Python senza spiegazioni. Il codice deve:

1. Definire una funzione generate_records(num_records) che:
   - Accetta il numero di record da generare
   - Genera i record secondo il pattern richiesto
   - Ritorna una lista di dizionari con i record generati

2. Definire una funzione save_to_csv(records, filename) che:
   - Salva i record nel file CSV specificato
   - Mostra un messaggio di completamento

3. Nel main:
   - Se richiesta generazione periodica:
     * Implementare un loop con intervallo specificato
     * Gestire Ctrl+C mostrando "Generazione interrotta"
   - Altrimenti generazione singola

PATTERN DI CHIAMATE:
- Per pattern fraudolenti: stesso raw_caller_number
- Per pattern normali: numeri diversi per caller/called
- Timestamp coerenti col pattern richiesto

CAMPI CSV:
{
    "tenant": sempre "Sparkle",
    "val_euro": numero decimale random tra 0.1 e 10.0,
    "duration": numero intero random in secondi tra 1 e 3600,
    "economicUnitValue": uguale a val_euro,
    "other_party_country": codice paese valido dalla lista COUNTRIES (prima del ':'),
    "routing_dest": uguale a selling_dest,
    "service_type__desc": sempre "Voice",
    "op35": sempre null,
    "carrier_in": scegli dalla lista di veri carrier internazionali,
    "carrier_out": scegli dalla lista di veri carrier internazionali,
    "selling_dest": scegli dalla lista di vere selling destination,
    "raw_caller_number": numero di 12 cifre (DEVE rimanere costante in caso di pattern fraudolenti),
    "raw_called_number": numero di 12 cifre,
    "paese_destinazione": nome del paese dalla lista COUNTRIES (dopo il ':'),
    "timestamp": formato ISO8601 con timezone, esempio: '2025-03-26T17:20:10.000+0200',
    "xdrid": randomico univoco del cartellino'
}

Esempio di codice da seguire:

```python
import time
import random
import datetime
import signal
import sys
import csv
from datetime import datetime, timedelta

# Costanti e configurazione
CARRIERS = ["Carrier1", "Carrier2", "Carrier3"]
COUNTRIES = ["IT:Italy", "FR:France", "DE:Germany"]
SELLING_DEST = ["IT_Mobile", "FR_Mobile", "DE_Mobile"]

def generate_records(num_records):
    records = []
    for i in range(num_records):
        val_euro = round(random.uniform(0.1, 10.0), 2)
        record = {
            "tenant": "Sparkle",
            "val_euro": val_euro,
            "duration": random.randint(1, 3600),
            "economicUnitValue": val_euro,
            # ... altri campi ...
        }
        records.append(record)
    return records

def save_to_csv(records, filename):
    fields = ["tenant", "val_euro", "duration", "economicUnitValue", "other_party_country", 
              "routing_dest", "service_type__desc", "op35", "carrier_in", "carrier_out",
              "selling_dest", "raw_caller_number", "raw_called_number", "paese_destinazione",
              "timestamp", "xdrid"]
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    print(f"File generato: {filename}")

def main():
    try:
        print(f"Inizio generazione: {datetime.now()}")
        
        # Generazione record
        records = generate_records(num_records=5000)
        
        # Nome file basato su timestamp
        now = datetime.now()
        filename = f"/data/output{now.strftime('%Y%m%d%H%M%S')}.csv"
        
        # Salvataggio
        save_to_csv(records, filename)
        
        # Se richiesto periodico, attendi e ripeti
        if is_periodic:
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\nGenerazione interrotta dall'utente")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

Rispondi solo con il codice Python, senza testo aggiuntivo.
"""

@app.route("/generate_code", methods=["POST"])
def generate_code():
    try:
        # Get request
        user_request = request.json.get("rule", "")
        if not user_request:
            return jsonify({"error": "Missing 'rule' parameter"}), 400

        # Call Gemini
        response = genai.GenerativeModel('gemini-2.0-flash').generate_content(
            f"{CONTEXT}\n\nRichiesta: {user_request}"
        )

        generated_code = response.text.strip().replace("```python", "").replace("```", "")

        # Create preview script (100 records)
        preview_code = generated_code.replace("num_records=5000", "num_records=100")
        with open("/data/preview_script.py", "w") as f:
            f.write(preview_code)

        # Create full generation script
        with open("/data/generate_script.py", "w") as f:
            f.write(generated_code)

        message = """
Generated two scripts:
1. /data/preview_script.py - Run this to see 100 sample records
2. /data/generate_script.py - Run this to generate the full dataset

To preview: python /data/preview_script.py
To generate full CSV: python /data/generate_script.py"""

        return jsonify({
            "status": "Scripts generated successfully",
            "message": message.strip()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)