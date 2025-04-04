#!/usr/bin/env python3
import os
import sys
import google.generativeai as genai
import tempfile

def get_user_prompt():
    print("\n=== Generatore di dati CSV ===")
    print("Esempi di pattern:")
    print("1. Normale: 'Genera un CSV con 5000 chiamate normali randomiche'")
    print("2. Periodico: 'Genera un CSV ogni 5 secondi con chiamate normali'")
    print("3. Fraudolento: 'CSV con caller che chiama 20 numeri in 2 minuti'")
    print("\nInserisci il tuo prompt (o 'q' per uscire):")
    return input("> ").strip()

def generate_code(prompt, data_dir):
    print("\nGenerazione codice Python in corso...")
    context = CONTEXT.replace("__DATA_DIR__", data_dir)  # Sostituisce il placeholder
    response = genai.GenerativeModel('gemini-2.0-flash').generate_content(
        f"{context}\n\nRichiesta: {prompt}"
    )
    return response.text.strip().replace("```python", "").replace("```", "")

def save_code(code):
    # Crea un file temporaneo per il codice Python
    fd, path = tempfile.mkstemp(suffix='.py', prefix='generator_')
    with os.fdopen(fd, 'w') as f:
        f.write(code)
    return path

def ask_yes_no(question):
    while True:
        response = input(f"\n{question} (y/n): ").lower().strip()
        if response in ['y', 'n']:
            return response == 'y'

def main():
    if len(sys.argv) != 2:
        print("Errore: Specificare la directory data")
        print("Uso: python generate_data.py <data_dir>")
        sys.exit(1)
        
    data_dir = sys.argv[1]

    while True:
        # Chiedi il prompt all'utente
        prompt = get_user_prompt()
        if prompt.lower() == 'q':
            break

        try:
            # Genera il codice Python
            generated_code = generate_code(prompt, data_dir)
            print("\nCodice Python generato con successo!")

            # Salva ed esegui il codice
            script_path = save_code(generated_code)
            
            print(f"\nGenerazione preview in preview_data.csv...")
            os.system(f"python {script_path}")
            
            # Pulisci il file temporaneo
            os.unlink(script_path)

        except Exception as e:
            print(f"\nErrore: {str(e)}")
            continue

        # Chiedi se vuole generare altro
        if not ask_yes_no("Vuoi generare altri dati?"):
            break

    print("\nProgramma terminato.")

# Configurazione Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")
genai.configure(api_key=GEMINI_API_KEY)

# Contesto per Gemini
CONTEXT = r"""
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
    "timestamp": formato ISO8601 con timezone, esempio: '2025-03-26T17:20:10.000+02:00',
    "xdrid": randomico univoco del cartellino'
}

La funzione generata deve seguire questi passi:
1. Generare prima una preview di 100 record in 'preview_data.csv'
2. Chiedere conferma all'utente con "Vuoi generare il dataset completo? (s/n): "
3. Se confermato con 's', salvare il dataset completo in `__DATA_DIR__/output_YYYYMMDD_HHMMSS.csv`

Rispondi solo con il codice Python, senza testo aggiuntivo.

Esempio di codice:

```python
import os
import time
import random
import datetime
import signal
import sys
import csv
import re
from datetime import datetime, timedelta, timezone

def is_periodic_request(prompt):
    # Cerca pattern "ogni X secondi"
    match = re.search(r'ogni (\d+) second[io]', prompt.lower())
    if match:
        return True, int(match.group(1))
    return False, 0

def create_dir_if_not_exists(filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

def save_to_csv(records, filename, preview=False):
    # Determina il percorso del file
    if preview:
        filepath = "./preview_data.csv"
    else:
        # Usa il timestamp per il nome del file
        now = datetime.now()
        filepath = f"__DATA_DIR__/output_{now.strftime('%Y%m%d_%H%M%S')}.csv"
        # Directory creation only needed for non-preview files
        create_dir_if_not_exists(filepath)
    
    # Salva il CSV
    fields = ["tenant", "val_euro", "duration", "economicUnitValue", ...]
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    print(f"File generato: {filepath}")

def main():
    try:
        # Genera preview
        records = generate_records(100)
        save_to_csv(records, "", preview=True)
        
        if input("Vuoi generare il dataset completo? (s/n): ").lower() != 's':
            return
            
        # Determina se è una richiesta periodica
        is_periodic, interval = is_periodic_request(user_request)
        
        print("Generazione in corso...")
        while True:
            records = generate_records(5000)
            save_to_csv(records, "")
            
            if not is_periodic:
                print("Completato.")
                break
                
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nGenerazione interrotta")
        sys.exit(0)
```

Rispondi solo con il codice Python completo, senza testo aggiuntivo.
"""

if __name__ == "__main__":
    main()