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

# Imposta la chiave API di Gemini
GENAI_API_KEY = "AIzaSyBdO5jVg1vi5MRGsGUfUO-g9sVlt8QTaM4"
genai.configure(api_key=GENAI_API_KEY)

# Liste di valori validi
CARRIERS = """
AT&T,Verizon,TIM,Vodafone,Orange,Deutsche Telekom,Telefonica,China Mobile,
NTT DoCoMo,SingTel,Telstra,Airtel,MTN,Etisalat,America Movil,UAE,
Saudi Telecom,Turkcell,MTS,Telenor,SK Telecom,KDDI,Globe,Telkomsel
""".strip().split(',')

DESTINATIONS = """
UAE,USA,ITA,GBR,FRA,DEU,ESP,CHN,JPN,SGP,AUS,IND,ZAF,ARE,MEX,SAU,TUR,RUS,NOR,KOR,JPN,PHL,IDN,
THURAYA-Reg,Inmarsat,GlobalStar,Iridium
""".strip().split(',')

COUNTRIES = """
001:USA,039:ITA,044:GBR,033:FRA,049:DEU,034:ESP,086:CHN,081:JPN,065:SGP,061:AUS,091:IND,
027:ZAF,971:ARE,052:MEX,966:SAU,090:TUR,007:RUS,047:NOR,082:KOR,081:JPN,063:PHL,062:IDN,
882:THURAYA,881:Inmarsat
""".strip().split(',')

# Contesto fisso per Gemini
CONTEXT = """
Sei un assistente AI specializzato nella generazione di codice Python.
Quando ricevi una richiesta, devi restituire SOLO il codice Python senza spiegazioni o testo aggiuntivo.
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
    "raw_caller_number": numero di 12 cifre,
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

        # Modifica il codice per salvare i file CSV in /data
        modified_code = generated_code.replace('output.csv', '/data/output.csv')
        
        # Esegue il codice generato in un ambiente sicuro
        with open("/data/temp_script.py", "w") as f:
            f.write(modified_code)
        
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