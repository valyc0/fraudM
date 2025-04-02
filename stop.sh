#!/bin/bash

# Check for --all parameter
if [ "$1" = "--all" ]; then
    echo "Stopping all services and removing volumes..."
    docker-compose down -v
    echo "All services and volumes have been removed."
else
    echo "Stopping all services..."
    docker-compose down
    echo "All services have been stopped. Use --all to remove volumes as well."
fi