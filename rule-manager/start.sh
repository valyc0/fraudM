#!/bin/bash

# Check for build parameter
BUILD_FLAG=""
if [ "$1" = "build" ]; then
    echo "Force rebuilding containers..."
    BUILD_FLAG="--build"
    docker-compose down -v
fi

# Check if network exists
if ! docker network ls | grep -q fraud-network; then
    echo "Creating fraud-network..."
    docker network create fraud-network
fi

echo "Starting Rule Manager services..."
docker-compose up -d $BUILD_FLAG

echo "Rule Manager environment is ready!"
echo "Access points:"
echo "- Rule Manager API: http://localhost:5001"
echo "- Flink Dashboard: http://localhost:8081"