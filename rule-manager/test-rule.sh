#!/bin/bash
curl -X POST http://localhost:5001/generate_rule -H "Content-Type: application/json" \
-d '{"rule": "caller che chiama piu di 10 called in 10 min", "rule_name": "high_frequency_caller"}'