import os
import google.generativeai as genai
from typing import Dict, Any
import json
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import time
import shutil

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

# Template files
TEMPLATE_DIR = "app/templates"
KAFKA_TEMPLATE = os.path.join(TEMPLATE_DIR, "KafkaInput.scala")
OPENSEARCH_TEMPLATE = os.path.join(TEMPLATE_DIR, "OpenSearchOutput.scala")
SCALA_CONTEXT = """
Sei un esperto di Apache Flink e Scala specializzato nella generazione di codice per il rilevamento frodi in tempo reale.
Quando ricevi una richiesta, devi restituire SOLO il codice Scala senza spiegazioni o testo aggiuntivo.

IMPORTANTE:
OBBLIGATORI i seguenti import:
```scala
import org.apache.flink.streaming.api.scala._
import org.apache.flink.streaming.api.windowing.time.Time
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows
import org.apache.flink.api.common.functions.AggregateFunction
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper
import java.time.Instant
import java.time.format.DateTimeFormatter
import java.io.Serializable

// Import delle classi di input/output predefinite
import KafkaInput
import OpenSearchOutput
```

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
2. Deve implementare la logica di business nel metodo 'execute'
3. Deve usare una finestra temporale di 2 minuti (TumblingProcessingTimeWindows)
4. Deve gestire gli errori in modo robusto

UTILIZZO DELLE CLASSI PREDEFINITE:
1. Per ottenere lo stream da Kafka:
   ```scala
   val kafkaInput = new KafkaInput()
   val stream = kafkaInput.createStream(env)
   ```

2. Per inviare gli alert a OpenSearch:
   ```scala
   alerts.addSink(new OpenSearchOutput())
   ```

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
            
            # Salva il codice generato
            self._save_generated_code(scala_code, description)
            
            formatted_code = self._format_scala_code(scala_code)
            logger.info("Generazione del codice completata con successo")
            return formatted_code
            
        except Exception as e:
            logger.error(f"Errore durante la generazione del codice Scala: {str(e)}", exc_info=True)
            raise

    def _validate_generated_code(self, code: str):
        """Validazione base del codice generato"""
        try:
            required_elements = [
                "import org.apache.flink",
                "import org.apache.flink.streaming",
                "import KafkaInput",
                "import OpenSearchOutput",
                "class Rule",
                "execute",
                "createStream",
                "addSink"
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
        """Save generated code and copy template files to a new dated directory"""
        try:
            # Crea directory con data per il codice Scala
            now = datetime.now()
            scala_dir = f"app/scala/{now.strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(scala_dir, exist_ok=True)
            logger.info(f"Directory {scala_dir} creata")
            
            # Copia i file template
            shutil.copy2(KAFKA_TEMPLATE, os.path.join(scala_dir, "KafkaInput.scala"))
            shutil.copy2(OPENSEARCH_TEMPLATE, os.path.join(scala_dir, "OpenSearchOutput.scala"))
            logger.info("File template copiati nella nuova directory")
            
            # Estrai nome classe dalla descrizione
            class_name = "".join(word.capitalize() for word in description.split()[:4])
            class_name = f"Rule{class_name}"
            class_name = "".join(c for c in class_name if c.isalnum())
            logger.info(f"Nome classe generato: {class_name}")
            
            # Salva il file della regola
            rule_file = os.path.join(scala_dir, f"{class_name}.scala")
            with open(rule_file, "w") as f:
                f.write(f"// Rule ID: Generated at {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"// Description: {description}\n\n")
                f.write(code)
            
            logger.info(f"Codice Scala salvato in: {rule_file}")
            
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