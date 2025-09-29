# Gestão de Notas - API

## Como subir a API

```bash
cd infra
docker compose up --build -d
./scripts/create_db_user.sh
./scripts/start.sh
```

Acesse: http://localhost

## Dashboard de Logs

Acesse o Grafana: http://localhost:3000
- Usuário: admin
- Senha: admin

### Queries úteis no Grafana:

**Logs por container:**
```
{container_name="django_api"}
{container_name="postgres_db"}
{container_name="celery_worker"}
```

**Logs por rota:**
```
{container_name="django_api"} |= "GET /api/notas"
{container_name="django_api"} |= "POST /api/financeiro"
```

**Logs de erro:**
```
{container_name="django_api"} |= "ERROR"
{container_name="django_api"} |= "level": "ERROR"
```
