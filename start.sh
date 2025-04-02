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

# Check if network exists
if ! docker network ls | grep -q fraud-network; then
    echo "Creating fraud-network..."
    docker network create fraud-network
fi

# Create necessary directories
mkdir -p data
mkdir -p data/done
mkdir -p logstash/pipeline

# Ensure correct permissions
chmod -R 777 data

# Start the environment
echo "Starting main services..."
docker-compose up -d $BUILD_FLAG

echo "Waiting for services to be ready..."

# Function to check if a service is ready
check_service() {
    local service=$1
    local max_attempts=$2
    local attempt=1
    
    echo "Waiting for $service to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps $service | grep -q "running"; then
            echo "$service is running"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts: $service not ready yet..."
        sleep 3
        attempt=$((attempt + 1))
    done
    echo "$service failed to start in time"
    return 1
}

# Check Kafka
check_service "kafka" 10

# Wait for Kafka broker to be ready
echo "Waiting for Kafka broker to be ready..."
until docker-compose exec kafka bash -c "kafka-topics --bootstrap-server kafka:29092 --list" > /dev/null 2>&1; do
    echo "Kafka broker not ready yet..."
    sleep 3
done

# Check PostgreSQL
echo "Waiting for PostgreSQL to be ready..."
until docker-compose exec postgres pg_isready -h localhost -U postgres > /dev/null 2>&1; do
    echo "PostgreSQL not ready yet..."
    sleep 3
done

echo "Creating Kafka topics with 30 days retention..."
docker-compose exec kafka kafka-topics --create --topic call-data-raw --bootstrap-server kafka:29092 --partitions 1 --replication-factor 1 --config retention.ms=2592000000 || true

docker-compose exec kafka kafka-topics --create --topic call-alerts --bootstrap-server kafka:29092 --partitions 1 --replication-factor 1 --config retention.ms=2592000000 || true

# Check other essential services
check_service "opensearch" 10
check_service "grafana" 5
check_service "logstash-input" 5
check_service "logstash-postgres" 5

echo "Main environment is ready!"
echo "Access points:"
echo "- Flask API: http://localhost:5000"
echo "- Kafka UI: http://localhost:8080"
echo "- OpenSearch: http://localhost:9200"
echo "- OpenSearch Dashboards: http://localhost:5601"
echo "- Grafana: http://localhost:3000 (admin/admin)"
echo "- PostgreSQL Admin: http://localhost:8090"
echo ""
echo "To start Rule Manager services, run:"
echo "cd rule-manager && ./start.sh"