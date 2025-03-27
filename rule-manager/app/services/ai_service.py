import os
import google.generativeai as genai
from typing import Dict, Any
import json
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import time

# Configurazione directory log
LOG_DIR = '/app/logs'
os.makedirs(LOG_DIR, exist_ok=True)

# Periodo di rotazione dei log in giorni (default 30)
LOG_ROTATION_DAYS = int(os.getenv('LOG_ROTATION_DAYS', '30'))

# Configurazione logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Formattazione dei log
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Handler per la rotazione dei file di log
file_handler = TimedRotatingFileHandler(
    os.path.join(LOG_DIR, 'ai_service.log'),
    when='midnight',
    interval=1,
    backupCount=LOG_ROTATION_DAYS
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Handler per output su console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.info(f"Logging configurato con rotazione ogni {LOG_ROTATION_DAYS} giorni in {LOG_DIR}")

# Contesto fisso per Gemini
SCALA_CONTEXT = """
Sei un esperto di Apache Flink e Scala specializzato nella generazione di codice per il rilevamento frodi in tempo reale.
Quando ricevi una richiesta, devi restituire SOLO il codice Scala senza spiegazioni o testo aggiuntivo.

IMPORTANTE:
OBBLIGATORI i seguenti import:
```scala
import org.apache.flink.streaming.api.scala._
import org.apache.flink.streaming.api.windowing.time.Time
import org.apache.flink.streaming.connectors.kafka._
import org.apache.flink.api.common.serialization.SimpleStringSchema
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.{JsonNode, ObjectMapper}
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows
import org.apache.flink.api.common.functions.AggregateFunction
import org.opensearch.client.{RestClient, RestHighLevelClient}
import org.opensearch.client.indices.CreateIndexRequest
import org.opensearch.action.index.IndexRequest
import org.opensearch.common.xcontent.XContentType
import org.apache.http.HttpHost
import org.apache.http.auth.{AuthScope, UsernamePasswordCredentials}
import org.apache.http.impl.client.BasicCredentialsProvider
```

Il codice deve:
1. Leggere da un topic Kafka 'input-topic' (verrà sostituito dopo)
2. Usare un Kafka bootstrap server 'localhost:9092' (verrà sostituito dopo)
3. Usare un OpenSearch host 'localhost' e porta 9200 (verranno sostituiti dopo)
4. Usare credenziali OpenSearch temporanee 'user'/'pass' (verranno sostituite dopo)

I record sono in formato JSON con i seguenti campi:
* timestamp: ISO8601 con timezone
* raw_caller_number: numero chiamante (12 cifre)
* raw_called_number: numero chiamato (12 cifre)
* duration: durata in secondi
* val_euro: valore in euro della chiamata
* tenant: identificativo del tenant
* carrier_in: carrier di ingresso
* carrier_out: carrier di uscita
* paese_destinazione: paese di destinazione
* service_type__desc: tipo di servizio

STRUTTURA OBBLIGATORIA:
1. La classe deve chiamarsi 'Rule' ed estendere Serializable
2. Deve avere un metodo 'createStream' che configura la sorgente Kafka
3. Deve avere un metodo 'execute' che implementa la logica e scrive su OpenSearch
4. Deve usare una finestra temporale di 2 minuti (TumblingProcessingTimeWindows)
5. Deve scrivere i risultati su OpenSearch nell'indice 'output-index'
6. Deve includere commenti esplicativi nei punti chiave
7. Deve gestire gli errori in modo robusto

NOTA: Tutti i valori di configurazione (host, porte, topics, credenziali) verranno sostituiti dopo con i valori corretti.
Rispondi solo con il codice Scala, senza testo aggiuntivo.
"""

class AIService:
    def __init__(self):
        # Verifica e configura la API key di Gemini
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def generate_scala_code(self, description: str) -> str:
        """Generate Scala code for Flink from natural language description"""
        try:
            logger.info(f"Ricevuta richiesta in linguaggio naturale: {description}")
            
            # Genera il codice completo
            prompt = f"{SCALA_CONTEXT}\n\nRichiesta: {description}"
            logger.info(f"Prompt generato per l'AI:\n{prompt}")
            
            # Misura il tempo di risposta dell'AI
            start_time = time.time()
            response = self.model.generate_content(prompt)
            elapsed_time = time.time() - start_time
            logger.info(f"Risposta ricevuta dall'AI in {elapsed_time:.2f} secondi")
            
            # Pulisci e logga il codice iniziale
            scala_code = self._cleanup_code(response.text)
            logger.info("Codice Scala iniziale generato dall'AI:\n" + scala_code)
            
            # Validazione di base
            self._validate_generated_code(scala_code)
            logger.info("Validazione del codice completata con successo")
            
            # Sostituisci i placeholder con i valori reali
            scala_code = self._replace_config_values(scala_code)
            logger.info("Codice Scala finale dopo le sostituzioni:\n" + scala_code)
            
            # Salva il codice generato
            self._save_generated_code(scala_code, description)
            
            formatted_code = self._format_scala_code(scala_code)
            logger.info("Generazione del codice completata con successo")
            return formatted_code
            
        except Exception as e:
            logger.error(f"Errore durante la generazione del codice Scala: {str(e)}", exc_info=True)
            raise

    def _replace_config_values(self, code: str) -> str:
        """Sostituisce i placeholder con i valori di configurazione reali"""
        try:
            replacements = {
                'localhost:9092': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092'),
                'input-topic': os.getenv('KAFKA_INPUT_TOPIC', 'call-data-raw'),
                'output-index': os.getenv('KAFKA_OUTPUT_TOPIC', 'fraud-alerts'),
                'localhost': os.getenv('OPENSEARCH_HOST', 'opensearch'),
                '9200': os.getenv('OPENSEARCH_PORT', '9200'),
                'user': os.getenv('OPENSEARCH_USER', 'admin'),
                'pass': os.getenv('OPENSEARCH_PASSWORD', 'admin')
            }
            
            logger.info("Iniziata sostituzione dei placeholder")
            for old_value, new_value in replacements.items():
                code = code.replace(old_value, new_value)
                logger.info(f"Sostituito '{old_value}' con '{new_value}'")
                
            return code
        except Exception as e:
            logger.error(f"Errore durante la sostituzione dei valori: {str(e)}", exc_info=True)
            raise

    def _validate_generated_code(self, code: str):
        """Validazione base del codice generato"""
        try:
            required_elements = [
                "import org.apache.flink",
                "import org.apache.flink.streaming",
                "import org.opensearch",
                "class",
                "createStream",
                "execute",
                "localhost:9092",  # placeholder da sostituire
                "localhost",       # placeholder da sostituire
                "input-topic"      # placeholder da sostituire
            ]
            
            logger.info("Inizio validazione del codice generato")
            for element in required_elements:
                if element not in code:
                    logger.error(f"Elemento mancante: {element}")
                    raise ValueError(f"Generated code missing required element: {element}")
            logger.info("Validazione completata con successo")
        except Exception as e:
            logger.error(f"Errore durante la validazione: {str(e)}", exc_info=True)
            raise

    def _cleanup_code(self, code: str) -> str:
        """Clean up the generated code removing markdown and unwanted text"""
        try:
            logger.info("Pulizia del codice generato")
            code = code.replace("```scala", "").replace("```", "")
            return code.strip()
        except Exception as e:
            logger.error(f"Errore durante la pulizia del codice: {str(e)}", exc_info=True)
            raise

    def _save_generated_code(self, code: str, description: str):
        """Save generated code with class name"""
        try:
            # Crea directory per il codice Scala
            scala_dir = "app/scala"
            os.makedirs(scala_dir, exist_ok=True)
            logger.info(f"Directory {scala_dir} creata/verificata")
            
            # Estrai nome classe dalla descrizione
            class_name = "".join(word.capitalize() for word in description.split()[:4])
            class_name = f"Rule{class_name}"
            
            # Rimuovi caratteri non validi per nome file/classe
            class_name = "".join(c for c in class_name if c.isalnum())
            logger.info(f"Nome classe generato: {class_name}")
            
            # Salva il file con nome classe
            filename = f"{scala_dir}/{class_name}.scala"
            
            with open(filename, "w") as f:
                f.write(f"// Rule ID: Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"// Description: {description}\n\n")
                f.write(code)
                
            logger.info(f"Codice Scala salvato in: {filename}")
            
        except Exception as e:
            logger.error(f"Errore durante il salvataggio del codice: {str(e)}", exc_info=True)
            raise

    def _format_scala_code(self, code: str) -> str:
        """Format the generated Scala code for better readability"""
        try:
            logger.info("Inizio formattazione del codice")
            lines = code.split("\n")
            formatted_lines = []
            indent_level = 0
            
            for line in lines:
                line = line.strip()
                
                if line.endswith("{"):
                    formatted_lines.append("  " * indent_level + line)
                    indent_level += 1
                elif line.startswith("}"):
                    indent_level = max(0, indent_level - 1)
                    formatted_lines.append("  " * indent_level + line)
                else:
                    formatted_lines.append("  " * indent_level + line)
            
            logger.info("Formattazione completata")
            return "\n".join(formatted_lines)
        except Exception as e:
            logger.error(f"Errore durante la formattazione: {str(e)}", exc_info=True)
            raise