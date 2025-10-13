#!/bin/bash

GRAFANA_URL="http://localhost:3000"
GRAFANA_USER="admin"
GRAFANA_PASS="admin"

echo "Importando dashboards para Grafana..."

for dashboard in infra/monitoring/dashboards/*.json; do
  echo "Importando $(basename $dashboard)..."
  curl -X POST \
    -H "Content-Type: application/json" \
    -u "$GRAFANA_USER:$GRAFANA_PASS" \
    --data-binary "@$dashboard" \
    "$GRAFANA_URL/api/dashboards/db"
  echo ""
done

echo "Dashboards importados com sucesso!"