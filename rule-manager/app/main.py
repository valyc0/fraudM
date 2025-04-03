# pip install flask google-generativeai

# PROMPT ##############
# Esempio di utilizzo:
# curl -X POST http://localhost:5001/generate_rule -H "Content-Type: application/json" \
#   -d '{"rule": "caller che chiama piu di 10 called in 10 min", "rule_name": "high_frequency_caller"}'


from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import datetime
import logging
from logging.handlers import RotatingFileHandler

# Determina la directory base e imposta permessi
def setup_directory(dir_path):
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # Se la directory esiste ma non è scrivibile, prova a cambiare i permessi
        elif not os.access(dir_path, os.W_OK):
            os.system(f"sudo chown -R gitpod:gitpod {dir_path}")
    except Exception as e:
        print(f"Warning: Could not set up directory {dir_path}: {str(e)}")
        return False
    return True

# Determina la directory base (container o locale)
BASE_DIR = os.getenv('APP_DIR', '/app')
if not os.access(BASE_DIR, os.W_OK):
    # Fallback to local directory if container directory is not writable
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

# Configurazione directory
LOG_DIR = os.path.join(BASE_DIR, 'logs')
SQL_DIR = os.path.join(BASE_DIR, 'sql-rules')

# Crea e configura le directory necessarie
for directory in [LOG_DIR, SQL_DIR]:
    if not setup_directory(directory):
        logger.warning(f"Could not set up directory {directory} - may have permission issues")
    else:
        logger.info(f"Successfully set up directory: {directory}")

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Handler per la rotazione dei file di log
log_file = os.path.join(LOG_DIR, 'rule_generator.log')
handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Handler per output su console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Log directories in use
logger.info(f"Using base directory: {BASE_DIR}")
logger.info(f"Logs directory: {LOG_DIR}")
logger.info(f"SQL rules directory: {SQL_DIR}")

logger.info(f"Logging configurato in {LOG_DIR}")

app = Flask(__name__)

# Imposta la chiave API di Gemini da variabile d'ambiente
GENAI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GENAI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")
genai.configure(api_key=GENAI_API_KEY)

# Contesto SQL per Gemini
CONTEXT = """
Sei un esperto di Apache Flink SQL specializzato nella generazione di query per il rilevamento frodi telefoniche in tempo reale.
Quando ricevi una richiesta, devi restituire SOLO lo script SQL Flink senza spiegazioni o testo aggiuntivo.

IMPORTANTE:
- Lo script deve sempre partire con la definizione delle tabelle:
CREATE TABLE calls_stream (
    tenant STRING,
    val_euro DOUBLE,
    duration BIGINT,
    economicUnitValue DOUBLE,
    other_party_country STRING,
    routing_dest STRING,
    service_type__desc STRING,
    op35 STRING,
    carrier_in STRING,
    carrier_out STRING,
    selling_dest STRING,
    raw_caller_number STRING,
    raw_called_number STRING,
    paese_destinazione STRING,
    event_time TIMESTAMP(3) METADATA FROM 'timestamp',
    xdrid STRING,
    WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'call-data-raw',
    'properties.bootstrap.servers' = 'kafka:29092',
    'properties.group.id' = 'flink-rule-group',
    'format' = 'json',
    'json.fail-on-missing-field' = 'false',
    'json.ignore-parse-errors' = 'true',
    'scan.startup.mode' = 'earliest-offset'
);

CREATE TABLE call_alerts (
    xdrid STRING,
    tenant STRING,
    val_euro DOUBLE,
    duration INT,
    raw_caller_number STRING,
    raw_called_number STRING,
    `timestamp` TIMESTAMP(3),
    event_time TIMESTAMP(3),
    carrier_in STRING,
    carrier_out STRING,
    selling_dest STRING,
    rule_name STRING
) WITH (
    'connector' = 'kafka',
    'topic' = 'call-alerts',
    'properties.bootstrap.servers' = 'kafka:29092',
    'format' = 'json'
);

LINEE GUIDA:
1. Usa GROUP BY e finestre temporali (TUMBLE o HOP) per aggregare i dati nel periodo specificato
2. Implementa le condizioni di frode usando HAVING o WHERE secondo necessità
3. Usa event_time per le operazioni temporali
4. Includi sempre INSERT INTO call_alerts per salvare le anomalie rilevate
5. Includi SEMPRE il nome della regola nel campo rule_name dell'INSERT INTO call_alerts
   Esempio:
   INSERT INTO call_alerts
   SELECT
     xdrid,
     tenant,
     val_euro,
     CAST(duration AS INT),
     raw_caller_number,
     raw_called_number,
     CURRENT_TIMESTAMP as timestamp,
     event_time,
     carrier_in,
     carrier_out,
     selling_dest,
     'nome_regola' as rule_name  -- Usa il nome regola fornito
   FROM ...

Rispondi solo con lo script SQL Flink, senza testo aggiuntivo.
"""

@app.route("/generate_rule", methods=["POST"])
def generate_rule():
    try:
        # Ottieni i parametri dalla richiesta JSON
        user_request = request.json.get("rule", "")
        rule_name = request.json.get("rule_name", "")
        
        if not user_request:
            return jsonify({"error": "Missing 'rule' parameter"}), 400
        if not rule_name:
            return jsonify({"error": "Missing 'rule_name' parameter"}), 400
            
        # Aggiorna il contesto con il nome della regola
        context_with_name = f"{CONTEXT}\n\nRichiesta: {user_request}\nNome Regola: {rule_name}"

        # Chiamata a Gemini
        response = genai.GenerativeModel('gemini-2.0-flash').generate_content(context_with_name)

        # Pulisci il codice generato e rimuovi eventuali delimitatori markdown
        generated_code = response.text.strip().replace("```sql", "").replace("```", "")

        # Genera un nome file basato sul timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"rule_{timestamp}.sql"

        # Salva lo script SQL nella directory sql-rules
        filepath = os.path.join(SQL_DIR, filename)
        with open(filepath, "w") as f:
            f.write(generated_code)
        
        logger.info(f"Script SQL salvato in: {filepath}")

        return jsonify({
            "status": "Script SQL generato con successo",
            "filename": filename,
            "script": generated_code
        })

    except Exception as e:
        logger.error(f"Error generating SQL rule: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Failed to generate SQL rule",
            "details": str(e),
            "request": user_request
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)