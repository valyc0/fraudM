#!/bin/bash

# Function to display usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --from-beginning    Read all messages from the beginning"
    echo "  --new-group        Create a new consumer group"
    echo "  --reset-offset     Reset offset for existing consumer group"
}

# Default consumer group
GROUP_ID="message-viewer"

# Parse arguments
FROM_BEGINNING=""
if [ "$1" == "--from-beginning" ]; then
    FROM_BEGINNING="--from-beginning"
elif [ "$1" == "--new-group" ]; then
    GROUP_ID="message-viewer-$(date +%s)"
elif [ "$1" == "--reset-offset" ]; then
    echo "Resetting offset for group $GROUP_ID..."
    docker-compose exec kafka kafka-consumer-groups \
        --bootstrap-server kafka:29092 \
        --group $GROUP_ID \
        --topic call-data-raw \
        --reset-offsets \
        --to-earliest \
        --execute
fi

# View messages
echo "Viewing messages with consumer group: $GROUP_ID"
docker-compose exec kafka kafka-console-consumer \
    --bootstrap-server kafka:29092 \
    --topic call-data-raw \
    --group $GROUP_ID \
    $FROM_BEGINNING