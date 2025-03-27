#!/bin/bash

# Check for build parameter
BUILD_FLAG=""
if [ "$1" = "build" ]; then
    echo "Force rebuilding containers..."
    BUILD_FLAG="--build"
    # Stop and remove existing containers and volumes
    docker-compose down -v
    # Clean up data directory
    rm -rf data/*
fi

# Create necessary directories
mkdir -p data
mkdir -p logstash/pipeline

# Ensure correct permissions
chmod 777 data

# Start the environment
docker-compose up -d $BUILD_FLAG

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