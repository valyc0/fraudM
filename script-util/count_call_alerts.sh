#!/bin/bash
docker exec -it fraudm-postgres-1 psql -U postgres -d mydb -c "SELECT COUNT(*) FROM call_alerts;"