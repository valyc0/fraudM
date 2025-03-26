#!/bin/bash

# Ensure the data directory exists
mkdir -p /workspace/db-ready/fraudM/data

# Send request to generate random call data every 5 seconds
while true; do
    curl -X POST http://localhost:5000/generate_csv \
        -H "Content-Type: application/json" \
        -d '{
            "rule": "Genera un CSV ogni 5 secondi in /data con 5000 record randomici. Per ogni record: caller e called sono numeri a 10 cifre random, timestamp nel formato ISO8601 con timezone (esempio: 2025-03-26T17:20:10.000Z). Il nome del file deve essere outputYYYYMMDDHHMMSS.csv"
        }'
    echo -e "\n[$(date)] Generated new noise data CSV file in /data directory"
    sleep 5
done