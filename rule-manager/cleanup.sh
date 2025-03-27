#!/bin/bash

echo "Stopping Rule Manager services..."
docker-compose down

# Non rimuoviamo la rete fraud-network qui perché potrebbe essere in uso dal sistema principale
# Per rimuoverla manualmente: docker network rm fraud-network

echo "Rule Manager cleanup complete!"