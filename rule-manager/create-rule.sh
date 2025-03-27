#!/bin/bash

# Chiamata per creare una nuova regola e mostra la risposta completa
curl -X POST http://localhost:5001/rules/create \
-H "Content-Type: application/json" \
-d '{
    "name": "Regola_CallFrequency",
    "description": "trova un caller che chiama piu di 3 caller nell'\''arco di 2 minuti"
}' | json_pp

# Il risultato mostrerà:
# - rule_id: ID univoco della regola
# - name: nome della regola
# - natural_language: descrizione in linguaggio naturale
# - scala_code: codice Scala generato da Gemini
