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
- `/api/` inclui: processamento, financeiro, dashboard, empresa, notas, etc.
- `/api/notifications/` inclui: registro e polling/ack

Endpoints e métodos:

### Autenticação e Empresa
- POST `/api/auth/login/` (empresa): body `{cnpj, senha}` → `{access, refresh, empresa}`
- POST `/api/auth/setup-senha/`: body `{cnpj, senha}` → `{ok, empresa}`
- GET `/api/unclassified-companies/`: → Lista de empresas não classificadas.

### Processamento de Notas e Jobs
- POST `/api/processar-nota/`: multipart `{arquivo, meu_cnpj}` → `202 {uuid, status}`
- GET `/api/jobs/`: → Lista de todos os jobs de processamento.
- GET `/api/jobs/pendentes/`: → Lista de jobs com status PENDENTE.
- GET `/api/jobs/concluidos/`: → Lista de jobs com status CONCLUIDO.
- GET `/api/jobs/erros/`: → Lista de jobs com status FALHA.
- GET `/api/jobs/<uuid>/`: → `{uuid, status, dt_criacao, dt_conclusao, mensagem_erro}`
- POST `/api/jobs/<uuid>/`: → Reprocessa um job específico.
- DELETE `/api/jobs/<uuid>/`: → Deleta um job específico.

### Financeiro e Calendário
- GET `/api/contas-a-pagar/` → `[LancamentoFinanceiro]` (depth=2 inclui parceiro)
- GET `/api/contas-a-receber/` → `[LancamentoFinanceiro]`
- GET `/api/calendar-resumo/`: → Resumo financeiro mensal.
- GET `/api/calendar-dia/`: → Detalhes financeiros de um dia específico.

### Gestão de Notas Fiscais (CRUD)
- GET `/api/notas-fiscais/`: → Lista de todas as notas fiscais.
- POST `/api/notas-fiscais/`: → Cria uma nova nota fiscal.
- PUT `/api/notas-fiscais/<id>/`: → Atualiza uma nota fiscal existente.
- DELETE `/api/notas-fiscais/<id>/`: → Deleta uma nota fiscal.

### Dashboard e Notificações
- GET `/api/dashboard/` → `{top_5_fornecedores_pendentes: [...]}`
- POST `/api/notifications/register-device/` → `{id, token, platform, ...}`
- GET `/api/notifications/pending/` → `[{Notification}]`
- POST `/api/notifications/ack/` → `{ok: true}`

### Healthcheck
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

| RN001 - Validação de Propriedade da Nota Fiscal |
| **Implementação**: `apps.notas.services.NotaFiscalService` (validação de remetente/destinatário)<br/>`apps.notas.extractors` (detecção de CNPJs) |
| **O que faz / local**: Verifica se `meu_cnpj` corresponde ao remetente OU destinatário. Se NÃO, o serviço lança exceção e o `JobProcessamento` é marcado como **FALHA** (mensagem de erro armazenada no job). |

| RN002 - Classificação Automática de Tipo de Lançamento |
| **Implementação**: `apps.financeiro.strategies` (`TipoLancamentoContext`) → invocado por `apps.notas.services.NotaFiscalService` |
| **O que faz / observações**: Define `TIPO_LANCAMENTO` como `PAGAR` ou `RECEBER` com base na posição da empresa na nota. Conferir implementações das Strategies para regras específicas. |

| RN003 - Classificação Automática de Parceiros |
| **Implementação**: `apps.financeiro.strategies`, `apps.parceiros.models`, `apps.notas.services.NotaFiscalService._get_or_create_parceiro` |
| **O que faz / observações**: Após determinar o tipo do lançamento, o parceiro é classificado como **FORNECEDOR** ou **CLIENTE**; atualização é persistida no registro de `Parceiro`. |

| RN004 - Unicidade de CNPJ por Parceiro |
| **Implementação**: `apps.parceiros.models.Parceiro` (campo `cnpj` com constraint de unicidade / índice único) |
| **O que faz / observações**: Persistência e validações no service impedem duplicação; `_get_or_create_parceiro` busca por CNPJ e atualiza registro existente quando apropriado. |

| RN005 - Unicidade de CNPJ por Empresa |
| **Implementação**: `apps.empresa.models.MinhaEmpresa` (campo `cnpj` único), validações em `apps.empresa` e checagem em `apps.processamento.views` |
| **O que faz / observações**: Cadastro e autenticação por CNPJ; validação evita criação de jobs com CNPJ inválido ou duplicado. |

| RN006 - Status de Processamento Sequencial |
| **Implementação**: `apps.processamento.models.JobProcessamento` (campo `status`), `apps.classificadores.models` (valores de status), transições em `apps.processamento.tasks.processar_nota_fiscal_task` |
| **O que faz / observações**: Sequência: **PENDENTE → PROCESSANDO → CONCLUIDO / FALHA**; timestamps `dt_criacao`/`dt_conclusao` atualizados; transições realizadas no worker Celery. |

| RN007 - Status de Lançamento Financeiro |
| **Implementação**: `apps.financeiro.models.LancamentoFinanceiro`, `apps.classificadores` (statuses) |
| **O que faz / observações**: Lançamentos criados automaticamente iniciam com status **PENDENTE**; mudanças para `PAGO`/`RECEBIDO` ocorrem por processos financeiros/rotinas manuais. |

| RN008 - Relacionamento Obrigatório Nota-Lançamento |
| **Implementação**: `apps.financeiro.models.LancamentoFinanceiro` (OneToOneField -> `NotaFiscal`), validações em `apps.notas.services.NotaFiscalService` |
| **O que faz / observações**: Relação OneToOne exigida; criação ocorre de forma atômica no serviço; `on_delete=PROTECT` evita lançamentos órfãos. |

| RN009 - Integridade de Valores |
| **Implementação**: Validações em `apps.notas.services.NotaFiscalService`, `apps.financeiro.serializers`, e constraints de DB quando aplicáveis |
| **O que faz / observações**: Garante `LancamentoFinanceiro.valor == NotaFiscal.valor_total` antes do commit; divergências abortam a transação e marcam o job como FALHA. |

| RN010 - Proteção de Dados Relacionados (PROTECT) |
| **Implementação**: `on_delete=PROTECT` em FKs (`parceiros`, `empresas`, `classificadores`, `jobs`) definido nas models/migrations |
| **O que faz / observações**: Impede exclusões que quebrarem a integridade referencial; restrições aplicadas no modelo e no banco. |

| RN011 - Atualização Automática de Parceiros |
| **Implementação**: `apps.notas.services.NotaFiscalService._get_or_create_parceiro`, `apps.parceiros.models` (auditoria) |
| **O que faz / observações**: Quando detectada divergência (nome/tipo), o serviço atualiza o `Parceiro` existente e registra metadados de auditoria. |

| RN012 - Segurança de Identificadores |
| **Implementação**: Uso de `UUIDField` em modelos (`MinhaEmpresa`, `JobProcessamento`, `NotaFiscal`, `LancamentoFinanceiro`) e serializers controlando exposição |
| **O que faz / observações**: Endpoints públicos expõem UUIDs; IDs numéricos internos mantidos privados. Conferir `models` e `serializers` para detalhes. |

| RN013 - Processamento Assíncrono Obrigatório |
| **Implementação**: `apps.processamento.views.ProcessarNotaFiscalView`, `apps.processamento.publishers`, Celery config em `backend/celery.py`, tasks em `apps.processamento.tasks` |
| **O que faz / observações**: Upload retorna `202` com UUID; processamento é realizado por worker Celery; cliente consulta status via `GET /api/jobs/<uuid>/`. |

| RN014 - Filtros de Consulta Financeira |
| **Implementação**: `apps.financeiro.views` (ListViews), filtros/queries em selectors (`apps.financeiro.selectors`) e `apps.financeiro.serializers` |
| **O que faz / observações**: `/api/contas-a-pagar/` e `/api/contas-a-receber/` aplicam filtros (TIPO_LANCAMENTO, STATUS) e ordenação por `data_vencimento`. |

| RN015 - Transacionalidade de Processamento |
| **Implementação**: `apps.notas.services.NotaFiscalService` (uso de `transaction.atomic`), tratamento de exceções nas tasks Celery (`processar_nota_fiscal_task`) |
| **O que faz /observações**: Toda criação de `NotaFiscal` + `LancamentoFinanceiro` é executada dentro de uma transação; em caso de erro, é executado rollback e o job é marcado como FALHA. |

Anexos e referências detalhadas: consulte os arquivos em `docs/` mencionados ao longo do relatório.
