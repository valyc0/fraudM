# Architecture Diagram for FraudM Project

```mermaid
graph TD
    subgraph Data Flow
        A[CSV Generator] --> B[Logstash CSV to Kafka]
        B --> C[Kafka]
        C --> D[Logstash Kafka to OpenSearch]
        D --> E[OpenSearch]
        E --> F[OpenSearch Dashboards]
        C --> G[Kafka UI]
        E --> H[Grafana]
    end

    subgraph Rule Engine
        C --> I[Rule Manager]
        I --> J[Rule Execution Engine]
        J --> E
    end
```

## Overview

The FraudM project is designed to process and analyze data for fraud detection. It consists of several interconnected components that handle data generation, processing, storage, and visualization.

### Key Components and Their Roles

1. **CSV Generator**:
   - Generates synthetic CSV files containing data for analysis using Gemini AI.
   - Saves the files in a shared directory (`./data`) for further processing.
   - Exposed on port 5000 for interaction.
   - Requires `GEMINI_API_KEY` environment variable to be set.

   To run the service, replace the XXXXX placeholder in the `.env` file with your Gemini API key, then use:
   ```bash
   docker compose up
   ```

   For testing rule generation without starting the full stack, use the provided test script:
   ```bash
   cd simulatore-python
   ./test-rules.sh
   ```
   This will start a temporary container with just the CSV generator service.
   You can then test rules using curl, for example:
   ```bash
   curl -X POST http://localhost:5000/generate_csv -H "Content-Type: application/json" \
   -d '{"rule": "Genera un CSV in cui un caller chiama 20 numeri diversi nell arco di 2 minuti."}'
   ```

   Example of generated CSV format:
   ```csv
   tenant,val_euro,duration,economicUnitValue,other_party_country,routing_dest,service_type__desc,op35,carrier_in,carrier_out,selling_dest,raw_caller_number,raw_called_number,paese_destinazione,timestamp,xdrid
   Sparkle,6.54,2095,6.54,RU,Rome,Voice,,Orange,Bharti Airtel,Rome,101207102360,339576800213,Russia,2025-03-27T12:27:08.928474+02:00,2858d970-7f42-4625-85e7-1413eec1d016
   Sparkle,9.21,2114,9.21,JP,Rome,Voice,,Telefonica,Orange,Rome,722318916061,698101980017,Japan,2025-03-27T12:27:08.928571+02:00,a1f880f5-7557-40b0-9495-c37da00e222e
   ```

2. **Rule Engine Components**:
   - **Rule Manager**:
     - Manages and executes fraud detection rules through an API.
     - Consumes data from Kafka for real-time analysis.
     - Uses AI to assist in rule generation and management.
     - Exposes APIs for rule creation and management.
     - Available on port 8000.
   - **Rule Execution Engine**:
     - Processes rules against data streams from Kafka in real-time.
     - Evaluates conditions and triggers actions based on rule definitions.
     - Writes results to OpenSearch for monitoring and alerting.

3. **Zookeeper**:
   - Coordinates and manages the Kafka cluster.
   - Ensures proper synchronization between Kafka brokers.
   - Exposed on port 2181.

4. **Kafka**:
   - Acts as a message broker to handle data streams.
   - Receives data from Logstash and distributes it to other components.
   - Exposed on ports 9092 (host) and 29092 (internal).

5. **Kafka UI**:
   - Provides a web-based interface to monitor and manage Kafka topics and messages.
   - Exposed on port 8080 for easy access.

6. **Logstash Pipelines**:
   - **CSV to Kafka**: Reads CSV files from the shared directory and sends the data to Kafka topics.
   - **Kafka to OpenSearch**: Consumes data from Kafka topics and sends it to OpenSearch for indexing and analysis.

7. **OpenSearch**:
   - A search and analytics engine used to store and analyze data.
   - Provides APIs for querying and retrieving data.
   - Exposed on ports 9200 (API) and 9600 (monitoring).

8. **OpenSearch Dashboards**:
   - A visualization tool for creating dashboards and analyzing data stored in OpenSearch.
   - Exposed on port 5601 for user interaction.

9. **Grafana**:
   - A monitoring and analytics platform used to create advanced visualizations and dashboards.
   - Connects to OpenSearch to display real-time metrics and insights.
   - Exposed on port 3000.

### Network and Volumes

- **Network**: All components are connected via the `fraud-network` bridge network to ensure seamless communication.
- **Volumes**:
  - `opensearch-data`: Persistent storage for OpenSearch to retain indexed data.
  - `data`: Shared directory for CSV files and other intermediate data.

## Getting Started

To start the entire FraudM system:

1. First, ensure you have the required environment variables set:
   ```bash
   cd fraudM/rule-manager
   cp .env.example .env
   # Edit .env and set your GEMINI_API_KEY
   ```

2. Start all services:
   ```bash
   cd fraudM
   ./start.sh
   ```

The start script will launch all components in the correct order. Once started, you can access:

- Rule Manager API: http://localhost:8000
- Kafka UI: http://localhost:8080
- OpenSearch Dashboards: http://localhost:5601
- Grafana: http://localhost:3000

To clean up and stop all services:
```bash
./cleanup.sh
```

This architecture enables efficient data processing and visualization, making it suitable for fraud detection and monitoring use cases.
