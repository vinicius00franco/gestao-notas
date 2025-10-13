#!/bin/bash

# infra/scripts/setup_monitoring.sh
echo "Setting up observability stack..."

# Criar diretórios
mkdir -p infra/monitoring/dashboards
mkdir -p infra/monitoring/alerts

# Subir stack completa
docker-compose -f infra/docker-compose.yml up -d prometheus jaeger node-exporter grafana loki promtail

# Aguardar serviços
sleep 10

# Importar dashboards
chmod +x infra/scripts/import_dashboards.sh
./infra/scripts/import_dashboards.sh

echo "Observability stack ready!"
echo "Prometheus: http://localhost:9090"
echo "Jaeger: http://localhost:16686"
echo "Grafana: http://localhost:3000"
echo "Loki: http://localhost:3100"