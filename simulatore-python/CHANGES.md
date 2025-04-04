# Simulator Enhancement Specification

## Context Modifications

The Gemini prompt context needs to be modified to generate Python code that includes the following features:

### 1. Preview Generation
The generated code should:
- First generate ~100 sample records
- Display these records in the console
- Show clear separation between preview and full generation

### 2. User Confirmation
After preview:
- Ask user for confirmation to proceed
- Only generate full CSV file if confirmed
- Exit gracefully if not confirmed

### 3. Periodic Generation Support
Add support for:
- Optional periodic generation mode
- Configurable interval between files
- Clean shutdown mechanism

## Modified Context Template

```python
CONTEXT = """
Sei un assistente AI specializzato nella generazione di codice Python per simulare pattern di chiamate telefoniche.
Quando ricevi una richiesta, devi restituire SOLO il codice Python senza spiegazioni o testo aggiuntivo.

IMPORTANTE:
1. Il codice deve prima generare e mostrare una preview di circa 100 record
2. Dopo la preview, chiede conferma all'utente prima di procedere
3. Se la richiesta include generazione periodica:
   - Implementa un loop con intervallo configurabile
   - Permetti di interrompere con Ctrl+C
   
- Per pattern fraudolenti (es: "un caller chiama X numeri diversi"), usa lo stesso numero chiamante (raw_caller_number) per tutte le chiamate
- Per pattern normali, genera numeri diversi sia per chiamante che chiamato
- Imposta i timestamp in modo coerente con il pattern richiesto (es: spread temporale specifico)

Il codice deve sempre:
1. Mostrare una preview di ~100 record
2. Chiedere conferma "Vuoi procedere con la generazione del file completo? (y/n): "
3. Solo dopo conferma positiva, generare il CSV completo

Il CSV deve avere i seguenti campi:
[original fields...]

La funzione generata deve rispettare la richiesta dell'utente e salvare i dati in un file dentro la directory /data.
Il percorso completo del file deve essere `/data/output.csv` o `/data/outputYYYYMMDDHHMMSS.csv`.

Rispondi solo con il codice Python, senza testo aggiuntivo.
"""
```

## Implementation Steps

1. Update server.py with the new CONTEXT
2. Test with various scenarios:
   - Normal generation
   - Fraudulent patterns
   - Periodic generation
3. Verify preview and confirmation work correctly
4. Ensure clean handling of Ctrl+C for periodic generation

## Example Usage

```bash
# Normal generation
curl -X POST http://localhost:5000/generate_csv -H "Content-Type: application/json" -d '{"rule": "Genera un CSV con chiamate normali randomiche"}' 

# Periodic generation
curl -X POST http://localhost:5000/generate_csv -H "Content-Type: application/json" -d '{"rule": "Genera un CSV tipo output20250326082500.csv ogni 5 secondi"}'