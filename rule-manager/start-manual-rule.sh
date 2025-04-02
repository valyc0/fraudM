#!/bin/bash

# Chiamata per recuperare tutte le regole dal database
 docker exec -it rule-manager-jobmanager-1 bash ./bin/sql-client.sh -f /opt/flink/sql-rules/simple-copy.sql