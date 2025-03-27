# Architecture Diagram for FraudM Project

```mermaid
graph TD
    A[CSV Generator] --> B[Logstash CSV to Kafka]
    B --> C[Kafka]
    C --> D[Logstash Kafka to OpenSearch]
    D --> E[OpenSearch]
    E --> F[OpenSearch Dashboards]
    C --> G[Kafka UI]
    E --> H[Grafana]
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

   Example of generated CSV format:
   ```csv
   tenant,val_euro,duration,economicUnitValue,other_party_country,routing_dest,service_type__desc,op35,carrier_in,carrier_out,selling_dest,raw_caller_number,raw_called_number,paese_destinazione,timestamp,xdrid
   Sparkle,6.54,2095,6.54,RU,Rome,Voice,,Orange,Bharti Airtel,Rome,101207102360,339576800213,Russia,2025-03-27T12:27:08.928474+02:00,2858d970-7f42-4625-85e7-1413eec1d016
   Sparkle,9.21,2114,9.21,JP,Rome,Voice,,Telefonica,Orange,Rome,722318916061,698101980017,Japan,2025-03-27T12:27:08.928571+02:00,a1f880f5-7557-40b0-9495-c37da00e222e
   ```

2. **Zookeeper**:
   - Coordinates and manages the Kafka cluster.
   - Ensures proper synchronization between Kafka brokers.
   - Exposed on port 2181.

3. **Kafka**:
   - Acts as a message broker to handle data streams.
   - Receives data from Logstash and distributes it to other components.
   - Exposed on ports 9092 (host) and 29092 (internal).

4. **Kafka UI**:
   - Provides a web-based interface to monitor and manage Kafka topics and messages.
   - Exposed on port 8080 for easy access.

5. **Logstash Pipelines**:
   - **CSV to Kafka**: Reads CSV files from the shared directory and sends the data to Kafka topics.
   - **Kafka to OpenSearch**: Consumes data from Kafka topics and sends it to OpenSearch for indexing and analysis.

6. **OpenSearch**:
   - A search and analytics engine used to store and analyze data.
   - Provides APIs for querying and retrieving data.
   - Exposed on ports 9200 (API) and 9600 (monitoring).

7. **OpenSearch Dashboards**:
   - A visualization tool for creating dashboards and analyzing data stored in OpenSearch.
   - Exposed on port 5601 for user interaction.

8. **Grafana**:
   - A monitoring and analytics platform used to create advanced visualizations and dashboards.
   - Connects to OpenSearch to display real-time metrics and insights.
   - Exposed on port 3000.

### Network and Volumes

- **Network**: All components are connected via the `fraud-network` bridge network to ensure seamless communication.
- **Volumes**:
  - `opensearch-data`: Persistent storage for OpenSearch to retain indexed data.
  - `data`: Shared directory for CSV files and other intermediate data.

This architecture enables efficient data processing and visualization, making it suitable for fraud detection and monitoring use cases.
