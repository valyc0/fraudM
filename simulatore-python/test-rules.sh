#!/bin/bash

# Ensure the script stops on first error
set -e

# Create data directory if it doesn't exist
mkdir -p "../data"

# Remove existing container if it exists
docker rm -f csv-generator-test 2>/dev/null || true

# Build the image if needed
docker build -t csv-generator-test .

# Run a temporary container
docker run --rm \
  -v "$(pwd)/../data:/data" \
  -e GEMINI_API_KEY=$(grep GEMINI_API_KEY ../.env | cut -d '=' -f2) \
  -p 5000:5000 \
  --name csv-generator-test \
  csv-generator-test

# Note: The container will be automatically removed after it stops
# due to the --rm flag