#!/bin/bash

# Directory setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAUD_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load environment variables from the root .env file
ENV_FILE="$FRAUD_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment from $ENV_FILE"
    export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
else
    echo "Error: .env file not found in $FRAUD_DIR"
    echo "Please create a .env file with GEMINI_API_KEY=your_key_here"
    exit 1
fi

# Check if GEMINI_API_KEY is now set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "Error: GEMINI_API_KEY not found in $ENV_FILE"
    echo "Please add GEMINI_API_KEY=your_key_here to $ENV_FILE"
    exit 1
fi

echo "GEMINI_API_KEY loaded successfully"

# Create and set permissions for necessary directories
echo "Creating and configuring required directories..."
for dir in "logs" "sql-rules"; do
    mkdir -p "$SCRIPT_DIR/$dir"
    # If we're in Gitpod and directory is not writable, fix permissions
    if [ -n "$GITPOD_WORKSPACE_ID" ] && [ ! -w "$SCRIPT_DIR/$dir" ]; then
        echo "Fixing permissions for $dir directory..."
        sudo chown -R gitpod:gitpod "$SCRIPT_DIR/$dir"
    fi
done

echo "Directories configured:"
echo "- Logs: $SCRIPT_DIR/logs ($(stat -c '%U:%G' "$SCRIPT_DIR/logs"))"
echo "- SQL Rules: $SCRIPT_DIR/sql-rules ($(stat -c '%U:%G' "$SCRIPT_DIR/sql-rules"))"

# Check and install Python dependencies
echo "Checking Python dependencies..."
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "Installing required packages from requirements.txt..."
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
else
    echo "Warning: requirements.txt not found, installing minimal dependencies..."
    pip3 install flask google-generativeai
fi

# Set up environment for local execution
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
export APP_DIR="$SCRIPT_DIR"
cd "$SCRIPT_DIR"

# Verify environment setup
echo "Environment configuration:"
echo "- PYTHONPATH: $PYTHONPATH"
echo "- APP_DIR: $APP_DIR"

# Run the Flask application
echo "Starting Rule Manager..."
echo "Directories:"
echo "- Logs: $SCRIPT_DIR/logs"
echo "- SQL Rules: $SCRIPT_DIR/sql-rules"
echo "- Environment: $ENV_FILE"
echo
echo "Service will be available at: http://localhost:5001"
echo
echo "Example usage:"
echo "curl -X POST http://localhost:5001/generate_rule \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"rule\": \"caller che chiama piu di 10 called in 10 min\", \"rule_name\": \"high_frequency_caller\"}'"
echo
echo "Parameters:"
echo "- rule: description of the rule to generate"
echo "- rule_name: unique identifier for the rule (required)"
echo

# Execute the Flask application
python3 -u app/main.py