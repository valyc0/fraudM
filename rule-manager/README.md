# Rule Manager

Service che converte regole di fraud detection da linguaggio naturale in applicazioni Flink utilizzando AI.

## Architettura

Il servizio è composto da:
- API FastAPI per la gestione delle regole
- Integrazione con Gemini AI per la generazione del codice
- Storage su OpenSearch per la persistenza
- Integrazione con Apache Flink per l'esecuzione

## Configurazione

1. Configurare le variabili d'ambiente:
   - Copiare `.env.example` in `.env`
   - Impostare GEMINI_API_KEY
   - Configurare i parametri di connessione OpenSearch
   - Configurare l'URL del Flink Job Manager

2. Build:
   ```
   docker build -t rule-manager .
   ```

3. Avvio:
   ```
   docker compose up -d
   ```

## API Endpoints

Il servizio espone i seguenti endpoint:

- POST `/rules/create`: Crea una nuova regola
- GET `/rules`: Lista tutte le regole
- GET `/rules/{id}`: Dettaglio singola regola
- PUT `/rules/{id}`: Aggiorna una regola
- DELETE `/rules/{id}`: Elimina una regola
- POST `/rules/{id}/deploy`: Deploya una regola su Flink

La documentazione dettagliata delle API è disponibile su:
```
http://localhost:5001/docs
```

## Struttura Progetto

```
rule-manager/
├── app/
│   ├── services/
│   │   ├── ai_service.py      # Integrazione Gemini AI
│   │   └── opensearch_service.py  # Gestione persistenza
│   ├── models.py              # Modelli dati
│   └── main.py               # API endpoints
├── Dockerfile                # Container configuration
└── requirements.txt          # Dipendenze Python
```

## Monitoring

Il servizio integra:
- Logging strutturato
- Metriche Flink
- Dashboard OpenSearch
- Alerting su errori

## Note di Sviluppo

- Utilizzare Python 3.11+
- Installare le dipendenze da requirements.txt
- Seguire PEP 8 per il codice Python
- Documentare le modifiche