# pip install flask google-generativeai

# PROMPT ##############
# per generare rumore:
# curl -X POST http://localhost:5000/generate_csv -H "Content-Type: application/json" -d '{"rule": "Genera un CSV tipo output20250326082500.csv ogni 5 secondi in cui generi delle chiamate normali randomiche per simulare un flusso normale di dati in modo da inserire rumore.ogni file conterra 5000 record. i caller e called saranno numero a 10 cifre random"}' && ls -l output.csv

# per generare anomalie:
# curl -X POST http://localhost:5000/generate_csv -H "Content-Type: application/json" -d '{"rule": "Genera un CSV in cui un caller chiama 20 numeri diversi nell arco di 2 minuti."}' && ls -l output.csv


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
Quando ricevi una richiesta, devi restituire SOLO il codice Python senza spiegazioni o testo aggiuntivo.

IMPORTANTE:
- Per pattern fraudolenti (es: "un caller chiama X numeri diversi"), usa lo stesso numero chiamante (raw_caller_number) per tutte le chiamate
- Per pattern normali, genera numeri diversi sia per chiamante che chiamato
- Imposta i timestamp in modo coerente con il pattern richiesto (es: spread temporale specifico)

Il codice deve generare un CSV con i seguenti campi:
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

La funzione generata deve rispettare la richiesta dell'utente e salvare i dati in un file dentro la directory /data.
Il percorso completo del file deve essere `/data/output.csv` o `/data/outputYYYYMMDDHHMMSS.csv`.

Rispondi solo con il codice Python, senza testo aggiuntivo.
"""

@app.route("/generate_csv", methods=["POST"])
def generate_csv():
    try:
        # Ottieni il testo della richiesta JSON
        user_request = request.json.get("rule", "")
        if not user_request:
            return jsonify({"error": "Missing 'rule' parameter"}), 400

        # Chiamata a Gemini
        response = genai.GenerativeModel('gemini-2.0-flash').generate_content(
            f"{CONTEXT}\n\nRichiesta: {user_request}"
        )

        generated_code = response.text.strip().replace("```python", "").replace("```", "")

        # Salva il codice generato in un file per sicurezza (debugging)
        with open("/data/generated_script.py", "w") as f:
            f.write(generated_code)

        # Esegue il codice generato in un ambiente sicuro
        with open("/data/temp_script.py", "w") as f:
            f.write(generated_code)
        
        result = subprocess.run(["python", "/data/temp_script.py"], capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({
                "error": "Failed to execute generated code",
                "stderr": result.stderr,
                "stdout": result.stdout,
                "generated_code": generated_code
            }), 500
                
        return jsonify({"status": "CSV generato con successo", "executed_code": generated_code})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)