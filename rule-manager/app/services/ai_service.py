import os
import google.generativeai as genai
from typing import Dict, Any
import json
from datetime import datetime

# Contesto fisso per Gemini
SCALA_CONTEXT = """
Sei un esperto di Apache Flink e Scala specializzato nella generazione di codice per il rilevamento frodi in tempo reale.
Quando ricevi una richiesta, devi restituire SOLO il codice Scala senza spiegazioni o testo aggiuntivo.

IMPORTANTE:
- Usa sempre DataStream API di Flink 2.x
- Il codice deve leggere da un topic Kafka 'call-records'
- I record sono in formato JSON con i seguenti campi:
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

- Il codice deve:
  1. Implementare la logica di rilevamento frodi richiesta
  2. Gestire correttamente le finestre temporali se necessario
  3. Implementare pattern di aggregazione efficienti
  4. Scrivere gli alert su un topic Kafka 'fraud-alerts'
  5. Includere commenti esplicativi nei punti chiave
  6. Gestire gli errori in modo robusto

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
        """
        Generate Scala code for Flink from natural language description
        """
        try:
            # Costruisci il prompt completo
            prompt = f"{SCALA_CONTEXT}\n\nRichiesta: {description}"
            
            # Genera il codice usando Gemini
            response = self.model.generate_content(prompt)
            
            # Estrai e formatta il codice
            scala_code = response.text.strip()
            scala_code = self._cleanup_code(scala_code)
            
            # Validazione di base
            if not scala_code or "import org.apache.flink" not in scala_code:
                raise ValueError("Failed to generate valid Scala code")
            
            # Salva il codice generato per debug
            self._save_generated_code(scala_code, description)
            
            return self._format_scala_code(scala_code)
            
        except Exception as e:
            raise Exception(f"Failed to generate Scala code: {str(e)}")

    async def validate_generated_code(self, scala_code: str) -> Dict[str, Any]:
        """
        Validate the generated Scala code using Gemini AI
        """
        validation_prompt = f"""
        Analizza questo codice Scala per Apache Flink e validalo:

        {scala_code}

        Verifica:
        1. Importazioni Flink corrette
        2. Setup corretto dello stream processing
        3. Gestione degli errori
        4. Gestione delle risorse
        5. Considerazioni sulle performance

        Restituisci un oggetto JSON con:
        - is_valid: boolean
        - issues: array di stringhe (vuoto se valido)
        - suggestions: array di stringhe (miglioramenti opzionali)
        """

        try:
            response = await self.model.generate_content_async(validation_prompt)
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {
                "is_valid": False,
                "issues": ["Failed to parse validation result"],
                "suggestions": []
            }
        except Exception as e:
            return {
                "is_valid": False,
                "issues": [str(e)],
                "suggestions": []
            }

    def _cleanup_code(self, code: str) -> str:
        """Clean up the generated code removing markdown and unwanted text"""
        code = code.replace("```scala", "").replace("```", "")
        return code.strip()

    def _save_generated_code(self, code: str, description: str):
        """Save generated code with class name"""
        try:
            # Crea directory per il codice Scala
            scala_dir = "app/scala"
            os.makedirs(scala_dir, exist_ok=True)
            
            # Estrai nome classe dalla descrizione
            class_name = "".join(word.capitalize() for word in description.split()[:4])
            class_name = f"Rule{class_name}"
            
            # Rimuovi caratteri non validi per nome file/classe
            class_name = "".join(c for c in class_name if c.isalnum())
            
            # Salva il file con nome classe
            filename = f"{scala_dir}/{class_name}.scala"
            
            with open(filename, "w") as f:
                f.write(f"// Rule ID: Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"// Description: {description}\n\n")
                f.write(code)
                
            print(f"Scala code saved to: {filename}")
            
        except Exception as e:
            print(f"Error saving Scala code: {str(e)}")

    def _format_scala_code(self, code: str) -> str:
        """
        Format the generated Scala code for better readability
        """
        lines = code.split("\n")
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            line = line.strip()
            
            # Adjust indent level
            if line.endswith("{"):
                formatted_lines.append("  " * indent_level + line)
                indent_level += 1
            elif line.startswith("}"):
                indent_level = max(0, indent_level - 1)
                formatted_lines.append("  " * indent_level + line)
            else:
                formatted_lines.append("  " * indent_level + line)
        
        return "\n".join(formatted_lines)