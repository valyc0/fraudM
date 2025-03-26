#!/bin/bash

# Create necessary directories
mkdir -p data
mkdir -p logstash/pipeline

# Start the environment
docker-compose up -d

echo "Waiting for services to start..."
sleep 30

echo "Creating Kafka topic..."
docker-compose exec kafka kafka-topics --create --topic call-data-raw --bootstrap-server kafka:29092 --partitions 1 --replication-factor 1

echo "Environment is ready!"
echo "Access points:"
echo "- Flask API: http://localhost:5000"
echo "- Kafka UI: http://localhost:8080"
echo "- OpenSearch: http://localhost:9200"
echo "- OpenSearch Dashboards: http://localhost:5601"
echo "- Grafana: http://localhost:3000 (admin/admin)"