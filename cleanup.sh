#!/bin/bash

echo "Stopping main services..."
docker-compose down

# Non rimuoviamo automaticamente la rete fraud-network perché potrebbe essere in uso dal rule-manager
echo "Note: fraud-network will not be removed if Rule Manager is running"
echo "To manually remove the network: docker network rm fraud-network"

echo "Cleaning up data directory..."
rm -rf data/*

echo "Main environment cleanup complete!"
echo "To clean up Rule Manager services, run:"
echo "cd rule-manager && ./cleanup.sh"