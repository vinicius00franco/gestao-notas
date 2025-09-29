# Gestão de Notas - API

## Como subir a API

```bash
cd infra
docker compose up --build -d
./scripts/create_db_user.sh
./scripts/start.sh
```

Acesse: http://localhost:18080

Se a porta 80 estiver em uso por outros projetos na sua máquina, o compose
permite sobrescrever a porta do Nginx através da variável de ambiente
`HOST_NGINX_PORT`. Exemplo para subir em 18080 (evita conflitos):

```bash
cd infra
HOST_NGINX_PORT=18080 docker compose up --build -d
```

O endpoint de health da API estará disponível em:

```
http://localhost:18080/healthz
```

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
