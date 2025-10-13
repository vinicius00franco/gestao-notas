#!/bin/bash
# scripts/setup_test_environment.sh

echo "Configurando ambiente de teste..."

# 1. Subir o backend
echo "Iniciando containers Docker com sudo..."
cd infra
sudo docker compose up -d --build
cd ..
echo "Aguardando os containers iniciarem..."
sleep 25 # Aumentar o tempo de espera para garantir que o banco de dados esteja pronto

# 2. Criar dados de teste
echo "Criando dados de teste no backend..."
# Usar docker exec para rodar o script dentro do container do backend
sudo docker compose -f infra/docker-compose.yml exec backend python scripts/create_test_data.py

# 3. Verificar se backend está funcionando
echo "Verificando a saúde do backend..."
curl -f http://localhost:8000/healthz || {
    echo "Backend não está funcionando"
    exit 1
}

# 4. Subir o frontend mobile
echo "Iniciando o frontend mobile..."
cd mobile
npm start &
echo "Aguardando o frontend iniciar..."
sleep 30 # Aumentar o tempo de espera para o Metro bundler

echo "Ambiente configurado com sucesso!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:8081"