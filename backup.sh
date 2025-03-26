#!/bin/bash

# Create backup directory if it doesn't exist
mkdir -p ../backup

# Get current timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="../backup/fraudM_config_${TIMESTAMP}.tar.gz"

# Create tar.gz archive of all configuration files
tar -czf $BACKUP_FILE \
    --exclude='**/data' \
    --exclude='data' \
    --exclude='**/generated_script.py' \
    --exclude='**/temp_script.py' \
    --exclude='**/output.csv' \
    --exclude='**/*.log' \
    --exclude='**/*.tmp' \
    --exclude='**/*.bak' \
    --exclude='**/*.swp' \
    --exclude='**/*.gz' \
    --exclude='**/*.zip' \
    --exclude='**/*.tar' \
    --exclude='**/node_modules' \
    --exclude='**/__pycache__' \
    --exclude='.git' \
    ../fraudM

echo "Backup created: $BACKUP_FILE"
echo "Included configurations:"
echo "- Docker Compose configuration"
echo "- Scripts (start.sh, cleanup.sh)"
echo "- Logstash pipeline configurations"
echo "- Python CSV generator files"
echo "- Grafana provisioning files"