Infra moved into `infra/`.

To run locally:

  cd infra
  docker compose up --build -d

The compose file uses the project root as build context so images will be built from the project sources.

Environment overrides for host ports live in the top-level `.env` (e.g. `HOST_NGINX_PORT=8081`).
# Gestão de Notas - API (Django + DRF + Celery)

API robusta, assíncrona e profissional para processamento de notas fiscais, seguindo princípios SOLID. Infra containerizada com Docker Compose, PostgreSQL e RabbitMQ.

## Stack
- Django 4.2 + Django REST Framework
- Celery 5 + RabbitMQ (broker)
- PostgreSQL 14
- Gunicorn
- Docker e Docker Compose

## Estrutura
Consulte as pastas em `backend/` e `notas_fiscais/` conforme o código.

## Pré-requisitos
- Docker e Docker Compose instalados

## Configurar
1. Crie e ajuste o arquivo `.env` na raiz do projeto `gestao_notas/`:
```
DJANGO_SECRET_KEY='sua-chave-secreta-super-segura-aqui'
DB_NAME=gestao_notas_db
DB_USER=seu_usuario_aqui
DB_PASSWORD=sua_senha_forte_aqui
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
```

## Executar
1. Suba os containers:
```
docker-compose up --build
```
2. Em outro terminal, aplique migrações e crie superusuário:
```
docker-compose exec web python manage.py makemigrations

docker-compose exec web python manage.py migrate

docker-compose exec web python manage.py createsuperuser
```
3. Cadastre a sua empresa (MinhaEmpresa) no admin em http://localhost:8000/admin/

## Endpoints
- POST `/api/v1/processar-nota/` (multipart): arquivo, meu_cnpj
- GET `/api/v1/jobs/<id>/`
- GET `/api/v1/contas-a-pagar/`
- GET `/api/v1/contas-a-receber/`
- GET `/api/v1/dashboard/`

## Celery Worker
O worker é iniciado pelo serviço `worker` do docker-compose. As tarefas são enfileiradas via publisher Celery.

## Observações
- Em produção, configurar DEBUG=False, allowed hosts e secrets seguros.
- Ajuste os valores do `.env` para seu ambiente.

## Version fallback (roteamento de versões)

Este projeto inclui um middleware (`backend.middleware.ApiVersionFallbackMiddleware`) que permite redirecionar internamente chamadas de versões dentro de um intervalo para uma versão alvo.

Configuração (em `backend/settings.py`):

	API_VERSION_FALLBACKS = [
		{"range": (10, 20), "target": 10},
	]

Com isso, uma chamada para `/api/v15/contas-a-pagar/` será internamente reescrita para `/api/v10/contas-a-pagar/`.

Use isso quando quiser descontinuar mudanças entre versões intermediárias e apontar vários sub-versions para uma versão principal sem alterar clientes.
# gestao-notas
