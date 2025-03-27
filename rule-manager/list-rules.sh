#!/bin/bash

# Chiamata per recuperare tutte le regole dal database
echo "Recupero tutte le regole..."
curl -X GET http://localhost:5001/rules \
-H "Content-Type: application/json" | json_pp

# Il risultato mostrerà per ogni regola:
# - rule_id
# - name
# - natural_language
# - scala_code
# - status
# - created_at
# - version
# - is_active