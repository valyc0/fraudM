#!/bin/bash

# Leggi il file .env dalla directory fraudM
if [ -f "$(dirname "$0")/../.env" ]; then
    export $(cat "$(dirname "$0")/../.env" | grep GEMINI_API_KEY)
else
    echo "Errore: File .env non trovato in fraudM/"
    exit 1
fi

# Verifica se GEMINI_API_KEY è impostata
if [ -z "$GEMINI_API_KEY" ]; then
    echo "Errore: GEMINI_API_KEY non trovata nel file .env"
    exit 1
fi

# Imposta il percorso della directory data
DATA_DIR="$(dirname "$0")/../data"

# Installa le dipendenze Python se necessario
echo "Verifica delle dipendenze..."
pip install -q google-generativeai flask pytz

# Avvia il generatore di dati
echo "Avvio generatore dati..."
python "$(dirname "$0")/generate_data.py" "$DATA_DIR"