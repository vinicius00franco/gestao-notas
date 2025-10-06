# Relatório Completo — Sistema de Gestão de Notas Fiscais

> Resumo executivo

Este relatório técnico detalhado descreve arquitetura, modelos de dados, endpoints, fluxos assíncronos, padrões aplicados (Observer/Strategy), jobs via Celery e instruções rápidas para executar a aplicação em ambiente de desenvolvimento.

---

## Sumário

- [1. Visão Geral da Arquitetura](#1-visão-geral-da-arquitetura)
- [2. Estrutura de Pastas (resumo útil)](#2-estrutura-de-pastas-resumo-útil)
- [3. Módulos e Responsabilidades](#3-módulos-e-responsabilidades)
- [4. Modelagem de Dados (principais entidades e relacionamentos)](#4-modelagem-de-dados-principais-entidades-e-relacionamentos)
- [5. Endpoints de API](#5-endpoints-de-api)
- [6. Fluxos de Negócio e Regras](#6-fluxos-de-negócio-e-regras)
- [7. Padrões de Projeto Aplicados](#7-padrões-de-projeto-aplicados)
- [8. Autenticação e Segurança](#8-autenticação-e-segurança)
- [9. Notificações Mobile (Polling)](#9-notificações-mobile-polling)
- [10. Infraestrutura e Execução](#10-infraestrutura-e-execução)
- [11. Diagrama de Domínio e Endpoints](#11-diagrama-de-domínio-e-endpoints)
- [12. Como Rodar (dev com Docker)](#12-como-rodar-dev-com-docker)
- [13. Rastreabilidade](#13-rastreabilidade)
- [Requisitos e Regras Analisados](#requisitos-e-regras-analisados)

---
---

Este documento apresenta uma visão abrangente do projeto: arquitetura, estrutura de pastas, principais módulos, modelos de dados, endpoints de API, fluxos de processamento, padrões aplicados (Observer/Strategy), jobs assíncronos, autenticação, notificações móveis e infraestrutura de execução.

## 1. Visão Geral da Arquitetura

- Backend: Django + Django REST Framework (DRF), ASGI (Uvicorn via Gunicorn)
- Autenticação: JWT (rest_framework_simplejwt) com autenticador customizado por Empresa (claims emp_uuid, emp_cnpj)
- Assíncrono: Celery + RabbitMQ para processamento de notas fiscais
- Banco de Dados: PostgreSQL
- Observabilidade: Logging JSON no console; stack Loki + Grafana + Promtail opcional no docker-compose
- CORS: liberado em DEBUG, configurável para produção
- Mobile: app React Native (Expo) consumindo endpoints (dashboard, contas, status de job, upload)

Diagrama de contexto (DFD Nível 0): ver `docs/diagramas-fluxo-dados.md`.

### Diagrama incorporado — Contexto (linhas retas)

```mermaid
%%{init: {'flowchart': {'curve': 'linear'}}}%%
graph TD
  Cliente[Cliente/Frontend] --> API[Sistema Gestão Notas]
  API --> Cliente
  API --> BD[(Base de Dados)]
  BD --> API
  API --> Celery[Fila Celery]
  Celery --> API
  API --> RabbitMQ[(RabbitMQ)]
  RabbitMQ --> API
```

## 2. Estrutura de Pastas (resumo útil)

- `backend/`
  - `settings.py`: apps instalados, DRF, JWT, CORS, DB, Celery, logging
  - `urls.py`: roteamento principal e healthcheck
  - `authentication.py`: `EmpresaJWTAuthentication` e principal `EmpresaPrincipal`
  - `middleware.py`: `ApiVersionFallbackMiddleware` (opcional)
  - `celery.py`, `asgi.py`, `wsgi.py`, `health.py`
- `apps/`
  - `empresa/`: login e setup de senha da empresa (`MinhaEmpresa`)
  - `parceiros/`: `Parceiro` (CLIENTE/FORNECEDOR)
  - `classificadores/`: `Classificador` e helper `get_classifier`
  - `processamento/`: `JobProcessamento`, serializers, publishers, tasks, views (upload e status)
  - `notas/`: modelos de nota, serviço `NotaFiscalService`, extratores (Strategy)
  - `financeiro/`: `LancamentoFinanceiro`, serializers, views (contas a pagar/receber), strategies
  - `dashboard/`: selectors (SQL agregada) e view `/api/dashboard/`
  - `notifications/`: `Device`, `Notification`, views para registro/poll/ack e Observer
  - `core/`: implementação genérica de Observer (Subject/Observer)
- `infra/`: Dockerfile, docker-compose, nginx, scripts
- `docs/`: requisitos, regras de negócio, DFDs, sequências, patterns (PUML e anotações)
- `mobile/`: app Expo/React Native (consome endpoints da API)

## 3. Módulos e Responsabilidades

- Empresa
  - Modelo `MinhaEmpresa` (UUID, CNPJ único, senha hash)
  - Endpoints:
    - POST `/api/auth/login/` — autentica por CNPJ/senha, emite JWT com claims da empresa
    - POST `/api/auth/setup-senha/` — define senha para um CNPJ
- Processamento
  - Modelo `JobProcessamento` (arquivo, empresa, status, timestamps)
  - Endpoints:
    - POST `/api/processar-nota/` — upload multipart com `arquivo` + `meu_cnpj`, cria Job status=PENDENTE, envia tarefa ao Celery
    - GET `/api/jobs/<uuid:uuid>/` — consulta status público por UUID
  - Tarefa Celery `processar_nota_fiscal_task(job_id)` — altera status (PROCESSANDO→CONCLUIDO/FALHA), chama serviço
- Notas Fiscais
  - Modelos `NotaFiscal` e `NotaFiscalItem`
  - Serviço `NotaFiscalService` (Subject do Observer):
    - Extrai dados via `ExtractorFactory` (PDF/XML/Imagem/Simulado)
    - Determina tipo e parceiro via `TipoLancamentoContext` (Strategy)
    - Gera `NotaFiscal` e `LancamentoFinanceiro` atômicos (transaction.atomic)
    - Notifica observers: vencimento, métricas, validação CNPJ, criação de notificações
- Financeiro
  - Modelo `LancamentoFinanceiro` (OneToOne com Nota)
  - Endpoints:
    - GET `/api/contas-a-pagar/`
    - GET `/api/contas-a-receber/`
  - Strategies: `NotaCompraStrategy`, `NotaVendaStrategy`
  - Observer: `AlertaVencimentoObserver`
- Dashboard
  - Selector `get_top_fornecedores_pendentes()` com SQL agregada
  - Endpoint: GET `/api/dashboard/`
- Parceiros
  - Modelo `Parceiro` (UUID, CNPJ único, tipo via Classificador)
  - Observer: `ValidacaoCNPJObserver` valida DV do CNPJ
- Classificadores
  - `Classificador` (tipo, código, descrição) com unicidade (tipo, código)
  - Usado para STATUS_JOB, TIPO_PARCEIRO, TIPO_LANCAMENTO, STATUS_LANCAMENTO
- Notifications
  - Modelos `Device` e `Notification`
  - Endpoints sob `/api/notifications/`:
    - POST `register-device/`
    - GET `pending/` (autenticado) — lista pendentes por usuário
    - POST `ack/` — confirma entrega
  - Observer: `PushStoreObserver` cria `Notification` por usuário ligado a devices da empresa

## 4. Modelagem de Dados (principais entidades e relacionamentos)

- Empresa (`MinhaEmpresa`) 1:N Jobs (`JobProcessamento`)
- Job 1:N Notas Fiscais (`NotaFiscal`)
- Nota 1:1 Lançamento (`LancamentoFinanceiro`)
- Parceiro 1:N Notas
- Classificador 1:N (Jobs.status, Parceiro.clf_tipo, Lançamento.clf_tipo / clf_status)

Tabelas e colunas utilizam prefixos e nomes customizados (db_table), com UUIDs públicos.

### Diagrama — Modelagem de Dados (Visão de Domínio, linhas retas)

```mermaid
%%{init: {'flowchart': {'curve': 'linear'}}}%%
flowchart LR
  ME["MinhaEmpresa<br/>(uuid, cnpj, nome)"]
  JP["JobProcessamento<br/>(uuid, arquivo_original, status, dt_criacao, dt_conclusao)"]
  NF["NotaFiscal<br/>(uuid, numero, data_emissao, valor_total)"]
  NFI["NotaFiscalItem<br/>(uuid, descricao, quantidade, valor_unitario, valor_total)"]
  LF["LancamentoFinanceiro<br/>(uuid, descricao, valor, data_vencimento, data_pagamento, clf_tipo, clf_status)"]
  P["Parceiro<br/>(uuid, nome, cnpj, clf_tipo)"]
  C["Classificador<br/>(tipo, codigo, descricao)"]

    ME -->|1..*| JP
    JP -->|1..*| NF
    NF -->|1..1| LF
    NF -->|0..*| NFI
    P -->|0..*| NF
    C -->|0..*| P
    C -->|0..*| JP
    C -->|0..*| LF
```

## 5. Endpoints de API

Prefixos principais em `backend/urls.py`:
- `/api/` inclui: processamento, financeiro, dashboard, empresa
- `/api/notifications/` inclui: registro e polling/ack

Endpoints e métodos:
- POST `/api/auth/login/` (empresa): body `{cnpj, senha}` → `{access, refresh, empresa}`
- POST `/api/auth/setup-senha/`: body `{cnpj, senha}` → `{ok, empresa}`
- POST `/api/processar-nota/`: multipart `{arquivo, meu_cnpj}` → `202 {uuid, status}`
- GET `/api/jobs/<uuid>/`: → `{uuid, status, dt_criacao, dt_conclusao, mensagem_erro}`
- GET `/api/contas-a-pagar/` → `[LancamentoFinanceiro]` (depth=2 inclui parceiro)
- GET `/api/contas-a-receber/` → `[LancamentoFinanceiro]`
- GET `/api/dashboard/` → `{top_5_fornecedores_pendentes: [...]}`
- POST `/api/notifications/register-device/` → `{id, token, platform, ...}`
- GET `/api/notifications/pending/` → `[{Notification}]`
- POST `/api/notifications/ack/` → `{ok: true}`
- GET `/healthz` — healthcheck (DB)

Permissões/Autenticação:
- DRF default AllowAny, mas endpoints de notifications pending/ack exigem IsAuthenticated
- Autenticação aceita JWT padrão e JWT com claims de empresa via `EmpresaJWTAuthentication`

## 6. Fluxos de Negócio e Regras

Referências diretas:
- `docs/requisitos-funcionais.md`
- `docs/regras-negocio.md`

Principais fluxos (diagramas): ver `docs/diagramas-fluxo-dados.md` e `docs/diagramas-sequencia.md`.

Destaques:
- Upload assíncrono RF001/RN013 com Celery
- Extração por Strategy `ExtractorFactory` (PDF/XML/OCR/Simulado) RF002
- Classificação automática e validações RN001–RN015
- Geração de lançamentos com OneToOne com nota e status PENDENTE RN007–RN009
- Dashboard com top 5 fornecedores RN014/RF008

### Diagrama de Sequência — POST /api/processar-nota/

```mermaid
sequenceDiagram
  participant C as Cliente
  participant V as ProcessarNotaFiscalView
  participant S as UploadNotaFiscalSerializer
  participant E as MinhaEmpresa
  participant CL as Classificador
  participant J as JobProcessamento
  participant P as CeleryTaskPublisher
  participant Q as RabbitMQ

  C->>V: POST /api/processar-nota/ {arquivo, meu_cnpj}
  V->>S: serializer.is_valid()
  S-->>V: validated_data
  V->>E: MinhaEmpresa.objects.get(cnpj)
  E-->>V: empresa
  V->>CL: get_classifier('STATUS_JOB','PENDENTE')
  CL-->>V: status_pendente
  V->>J: JobProcessamento.objects.create()
  J-->>V: job
  V->>P: publish_processamento_nota(job.id)
  P->>Q: processar_nota_fiscal_task.delay()
  Q-->>P: task_id
  V-->>C: 202 Accepted {uuid, status}
```

## 7. Padrões de Projeto Aplicados

- Strategy: determinação de tipo de lançamento e extração de dados
- Observer: notificação pós-criação de lançamento e parceiro
- Publisher-Subscriber: Celery Publisher → Task Worker
- Transaction Script: orquestração atômica no `NotaFiscalService`

PUMLs em `docs/patterns/observer/` e `docs/patterns/strategy/`.

Imagens:

![Observer Pattern](patterns/observer/Observer%20Pattern%20Implementation.png)

![Strategy Pattern](patterns/strategy/Strategy%20Pattern%20Implementation.png)

## 8. Autenticação e Segurança

- JWT com claims customizadas (`emp_uuid`, `emp_cnpj`)
- Autenticador `EmpresaJWTAuthentication` converte token em `EmpresaPrincipal` (is_authenticated=True)
- IDs públicos via UUIDs em endpoints (RN012)
- CORS sob controle, CSRF trusted para dev

## 9. Notificações Mobile (Polling)

- Dispositivo se registra via `/api/notifications/register-device/` (token Expo/FCM, plataforma)
- App realiza GET `/api/notifications/pending/` autenticado; servidor retorna não-entregues
- App envia POST `/api/notifications/ack/` para confirmar entrega
- Geração de `Notification` gatilhada por evento `lancamento_created` (Observer)

## 10. Infraestrutura e Execução

- Docker Compose: serviços `db` (Postgres), `rabbitmq`, `web` (Django ASGI), `worker` (Celery), `nginx`, `loki`, `grafana`, `promtail`
- Dockerfile: Python 3.10 slim, requirements, Gunicorn + UvicornWorker
- Healthcheck: `/healthz` verifica DB

### Variáveis de Ambiente (resumo)
- DB: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- Django: `DJANGO_SECRET_KEY`
- Celery: `CELERY_BROKER_URL` (padrão `amqp://guest:guest@rabbitmq:5672/`)

## 11. Diagrama de Domínio e Endpoints

- Diagrama de modelos: `docs/diagrams/models.puml`
- Endpoints específicos: `docs/diagrams/endpoint_*.puml`
  - `endpoint_processar_nota.puml`
  - `endpoint_job_status.puml`
  - `endpoint_contas_a_pagar.puml`
  - `endpoint_contas_a_receber.puml`
  - `endpoint_dashboard_stats.puml`
- Arquitetura de Observers: `docs/diagrams/observers_arch.puml`

## 12. Como Rodar (dev com Docker)

1) Configure arquivos `.env.common`, `.env.web`, `.env.db`, `.env.rabbitmq` (exemplos conforme variáveis acima)
2) Suba a stack Docker Compose
3) Acesse `http://localhost/healthz` e `http://localhost/api/...`

Opcionalmente, sem Docker, instale `requirements.txt`, configure Postgres e RabbitMQ e rode `celery -A backend worker -l info` em terminal separado.

## 13. Rastreabilidade

- RF001–RF015 cobertos por módulos e endpoints destacados
- RN001–RN015 implementados em services, strategies, observers e constraints de modelos
- Diagrams e código mantêm vínculo lógico nos nomes e caminhos de arquivos

---

## Requisitos e Regras Analisados

Resumo dos requisitos funcionais (RF) e regras de negócio (RN) extraídos dos documentos em `docs/` e mapeados para o código:

- RF001 Processamento de Notas Fiscais — Implementado em `apps.processamento.views.ProcessarNotaFiscalView`, `apps.processamento.tasks.processar_nota_fiscal_task` e `apps.notas.services.NotaFiscalService`.
- RF002 Extração de Dados — Implementado em `apps.notas.extractors` (PDF/XML/Image/Simulado) e usado por `NotaFiscalService`.
- RF003 Classificação Automática — Implementado em `apps.financeiro.strategies.TipoLancamentoContext` e `apps.financeiro.strategies.*Strategy`.
- RF004 Gestão de Parceiros — Implementado em `apps.parceiros.models.Parceiro` e `_get_or_create_parceiro` no `NotaFiscalService`.
- RF005 Consulta Status Job — Implementado em `apps.processamento.views.JobStatusView` e `apps.processamento.serializers.JobProcessamentoSerializer`.
- RF006 Listagem Contas a Pagar/Receber — Implementado em `apps.financeiro.views.ContasAPagarListView` e `ContasAReceberListView`.
- RF007 Dashboard Gerencial — Implementado em `apps.dashboard.selectors.get_top_fornecedores_pendentes` e `apps.dashboard.views.DashboardStatsView`.
- RF008 Auditoria e campos de auditoria — Implementado em modelos (campos dt_criacao, dt_alteracao, usr_criacao).
- RF009 Notificações Mobile (Polling) — Implementado em `apps.notifications.views` e `apps.notifications.models` (Device, Notification), e `PushStoreObserver`.


### Matriz de Rastreabilidade (completa)

A tabela abaixo lista, item a item, os Requisitos Funcionais (RF001–RF010) e as Regras de Negócio (RN001–RN015) com o mapeamento para os módulos/arquivos responsáveis e os endpoints ou locais do código onde a implementação pode ser verificada.

| Requisito / Regra | Implementação (módulos/arquivos) | Endpoints / Locais |
|---|---|---|
| RF001 - Processamento de Notas Fiscais | `apps.processamento.views.ProcessarNotaFiscalView`, `apps.processamento.serializers.UploadNotaFiscalSerializer`, `apps.processamento.models.JobProcessamento`, `apps.processamento.publishers`, `apps.processamento.tasks.processar_nota_fiscal_task`, `apps.notas.services.NotaFiscalService` | POST `/api/processar-nota/` (view `ProcessarNotaFiscalView`) → cria `JobProcessamento` (UUID) e enfileira `processar_nota_fiscal_task` no Celery; status gravado em `JobProcessamento` |
| RF002 - Extração de Dados da Nota Fiscal | `apps.notas.extractors` (módulos: pdf, xml, image, simulated), `apps.notas.extractors.ExtractorFactory`, `apps.notas.services.NotaFiscalService` | Extração invocada por `NotaFiscalService.processar_nota_fiscal_do_job` executado pelo worker Celery; ver classes de extratores e testes (se presentes) |
| RF003 - Classificação Automática de Lançamentos | `apps.financeiro.strategies.TipoLancamentoContext`, `apps.financeiro.strategies.NotaCompraStrategy`, `apps.financeiro.strategies.NotaVendaStrategy`, integração em `apps.notas.services.NotaFiscalService` | Determinação de TIPO_LANCAMENTO (PAGAR/RECEBER) durante processamento; lógica aplicada antes de criar `LancamentoFinanceiro` (interno ao serviço) |
| RF004 - Gestão de Parceiros | `apps.parceiros.models.Parceiro`, `apps.parceiros.admin`, `apps.notas.services.NotaFiscalService._get_or_create_parceiro` | `_get_or_create_parceiro` cria ou atualiza `Parceiro` com CNPJ/nome; ver persistência no processamento de nota (serviço) |
| RF005 - Consulta de Status de Processamento | `apps.processamento.views.JobStatusView`, `apps.processamento.serializers.JobProcessamentoSerializer`, `apps.processamento.models.JobProcessamento` | GET `/api/jobs/<uuid>/` — retorna `{uuid, status, dt_criacao, dt_conclusao, mensagem_erro}` |
| RF006 - Listagem de Contas a Pagar | `apps.financeiro.views.ContasAPagarListView`, `apps.financeiro.serializers`, possíveis selectors em `apps.financeiro` | GET `/api/contas-a-pagar/` — filtra TIPO_LANCAMENTO=PAGAR e STATUS=PENDENTE; ordena por data de vencimento; inclui dados do parceiro |
| RF007 - Listagem de Contas a Receber | `apps.financeiro.views.ContasAReceberListView`, `apps.financeiro.serializers` | GET `/api/contas-a-receber/` — filtra TIPO_LANCAMENTO=RECEBER e STATUS=PENDENTE; ordena por data de vencimento |
| RF008 - Dashboard Gerencial | `apps.dashboard.selectors.get_top_fornecedores_pendentes`, `apps.dashboard.views.DashboardStatsView`, consultas SQL/ORM agregadas | GET `/api/dashboard/` — retorna `top_5_fornecedores_pendentes` e métricas consolidadas; ver selector para regra de ordenação/filtragem |
| RF009 - Auditoria de Operações | Mixins/fields de auditoria presentes em modelos (`dt_criacao`, `dt_alteracao`, `usr_criacao`), implementações em `apps.*.models` | Campos de auditoria salvos nas tabelas; visíveis no admin e consultáveis via ORM; revisar `models` para campos exatos |
| RF010 - Versionamento de API | `backend.middleware.ApiVersionFallbackMiddleware`, rotas em `backend/urls.py`, configuração em `backend/settings.py` | Suporte a headers/version param; fallback implementado pelo middleware e roteamento condicional nas urls |

| RN001 - Validação de Propriedade da Nota Fiscal | `apps.notas.services.NotaFiscalService` (validação de remetente/destinatário), `apps.notas.extractors` (detecção de CNPJs) | `NotaFiscalService` verifica se `meu_cnpj` corresponde a remetente OU destinatário; caso contrário, lança erro e marca `JobProcessamento` como FALHA (mensagem de erro armazenada) |
| RN002 - Classificação Automática de Tipo de Lançamento | `apps.financeiro.strategies` (`TipoLancamentoContext`), invocado por `apps.notas.services.NotaFiscalService` | Regra aplicada durante processamento para definir PAGAR vs RECEBER; ver implementação das Strategies para critérios específicos |
| RN003 - Classificação Automática de Parceiros | `apps.financeiro.strategies`, `apps.parceiros.models`, `apps.notas.services.NotaFiscalService._get_or_create_parceiro` | Após determinar tipo de lançamento, parceiro é classificado como FORNECEDOR ou CLIENTE; atualização persistida no `Parceiro` |
| RN004 - Unicidade de CNPJ por Parceiro | `apps.parceiros.models.Parceiro` (campo `cnpj` com constraint de unicidade / índice único), validações no service | Persistência impede duplicação; `_get_or_create_parceiro` usa busca por CNPJ e atualiza registro existente quando apropriado |
| RN005 - Unicidade de CNPJ por Empresa | `apps.empresa.models.MinhaEmpresa` (campo `cnpj` único), validações em `apps.empresa` e checagem em `apps.processamento.views` | Cadastro e autenticação por CNPJ; validação antes de criar `JobProcessamento` (rejeita CNPJ inválido/duplicado) |
| RN006 - Status de Processamento Sequencial | `apps.processamento.models.JobProcessamento` (campo `status`), `apps.classificadores.models` (valores de status), transições em `apps.processamento.tasks.processar_nota_fiscal_task` e publishers | Sequência PENDENTE → PROCESSANDO → CONCLUIDO/FALHA; timestamps `dt_criacao`/`dt_conclusao` registrados; transições ocorrem no fluxo do task worker |
| RN007 - Status de Lançamento Financeiro | `apps.financeiro.models.LancamentoFinanceiro`, `apps.classificadores` (statuses) | Lançamentos criados automaticamente com status PENDENTE; atualização de status (PAGO/RECEBIDO) realizada por processos externos ou rotinas manuais |
| RN008 - Relacionamento Obrigatório Nota-Lançamento | `apps.financeiro.models.LancamentoFinanceiro` (OneToOneField -> `NotaFiscal`), validações em `apps.notas.services.NotaFiscalService` | OneToOne garantido na modelagem; criação atômica no serviço; `on_delete=PROTECT` para evitar orfandade |
| RN009 - Integridade de Valores | Validações em `apps.notas.services.NotaFiscalService`, `apps.financeiro.serializers` e constraints de DB (quando aplicável) | Confirma `LancamentoFinanceiro.valor == NotaFiscal.valor_total` antes de commit; erros abortam transação e marcam job como FALHA |
| RN010 - Proteção de Dados Relacionados (PROTECT) | `on_delete=PROTECT` em FKs (`parceiros`, `empresas`, `classificadores`, `jobs`), definido nas models/migrations | Impede exclusões que quebrariam integridade; aplicar restrições no nível do modelo e DB |
| RN011 - Atualização Automática de Parceiros | `apps.notas.services.NotaFiscalService._get_or_create_parceiro`, `apps.parceiros.models`, auditoria nos campos de histórico | Se houver divergência no nome/tipo do parceiro, o serviço atualiza o registro existente e registra meta-informação de alteração (campo de auditoria) |
| RN012 - Segurança de Identificadores | Uso de `UUIDField` em modelos (`MinhaEmpresa`, `JobProcessamento`, `NotaFiscal`, `LancamentoFinanceiro`) e exposições controladas por serializers | Endpoints públicos expõem UUIDs; IDs numéricos internos mantidos privados; ver `models` e `serializers` para detalhes |
| RN013 - Processamento Assíncrono Obrigatório | `apps.processamento.views.ProcessarNotaFiscalView`, `apps.processamento.publishers`, Celery config (`backend/celery.py`), tasks (`apps.processamento.tasks`) | Upload responde com 202 e UUID; processamento real realizado pelo worker Celery; cliente consulta por GET `/api/jobs/<uuid>/` |
| RN014 - Filtros de Consulta Financeira | `apps.financeiro.views` (ListViews), filtros/queries em selectors (`apps.financeiro.selectors` ou dentro das views), `apps.financeiro.serializers` | Endpoints `/api/contas-a-pagar/` e `/api/contas-a-receber/` aplicam filtros (TIPO_LANCAMENTO e STATUS) e ordenação por `data_vencimento` |
| RN015 - Transacionalidade de Processamento | `apps.notas.services.NotaFiscalService` (uso de `transaction.atomic`), tratamento de exceções nas tasks Celery (`processar_nota_fiscal_task`) | Toda operação de criação de `NotaFiscal` + `LancamentoFinanceiro` é executada dentro de uma transação; em caso de erro, rollback é executado e job marcado como FALHA |

Anexos e referências detalhadas: consulte os arquivos em `docs/` mencionados ao longo do relatório.
