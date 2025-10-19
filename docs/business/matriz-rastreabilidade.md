# Matriz de Rastreabilidade - Sistema de Gestão de Notas Fiscais

## Mapeamento Requisitos → Regras de Negócio → Implementação

| Requisito | Regras de Negócio | Endpoints | Arquivos | Testes |
|-----------|-------------------|-----------|----------|---------|
| **RF001** - Processamento de Notas Fiscais | RN006, RN013 | `POST /api/processar-nota/` | `apps/processamento/views.py`, `apps/processamento/publishers.py` | - |
| **RF002** - Extração de Dados | - | `POST /api/processar-nota/` (interno) | `apps/notas/extractors.py` | - |
| **RF003** - Classificação Automática | RN002, RN003 | `POST /api/processar-nota/` (interno) | `apps/notas/services.py` | - |
| **RF004** - Gestão de Parceiros | RN004, RN011 | `POST /api/processar-nota/` (interno) | `apps/notas/services.py`, `apps/parceiros/models.py` | - |
| **RF005** - Consulta Status | RN012 | `GET /api/jobs/<uuid>/` | `apps/processamento/views.py`, `apps/processamento/models.py` | - |
| **RF006** - Contas a Pagar | RN014 | `GET /api/contas-a-pagar/` | `apps/financeiro/views.py` | - |
| **RF007** - Contas a Receber | RN014 | `GET /api/contas-a-receber/` | `apps/financeiro/views.py` | - |
| **RF008** - Dashboard | - | `GET /api/dashboard/` | `apps/dashboard/views.py`, `apps/dashboard/selectors.py` | - |
| **RF009** - Auditoria | - | Todos os endpoints (campos automáticos) | `apps/*/models.py` | - |
| **RF010** - Versionamento API | - | Middleware para `/api/v*/` → `/api/` | `backend/middleware.py` | - |
| **RF011** - Calendário Financeiro | - | `GET /api/calendar-resumo/`, `GET /api/calendar-dia/` | `apps/financeiro/views.py` | - |

## Mapeamento Regras de Negócio → Implementação Detalhada

### RN001 - Validação de Propriedade da Nota Fiscal
- **Implementação:** `NotaFiscalService.processar_nota_fiscal_do_job()`
- **Localização:** `apps/notas/services.py:25-30`
- **Lógica:** Verifica se `dados_extraidos.destinatario_cnpj == minha_empresa.cnpj` ou `dados_extraidos.remetente_cnpj == minha_empresa.cnpj`
- **Exceção:** `ValueError("Nota fiscal não pertence à sua empresa")`

### RN002 - Classificação Automática de Tipo de Lançamento
- **Implementação:** `NotaFiscalService.processar_nota_fiscal_do_job()`
- **Localização:** `apps/notas/services.py:25-35`
- **Lógica:** 
  - Destinatário = empresa → `get_classifier('TIPO_LANCAMENTO', 'PAGAR')`
  - Remetente = empresa → `get_classifier('TIPO_LANCAMENTO', 'RECEBER')`

### RN003 - Classificação Automática de Parceiros
- **Implementação:** `NotaFiscalService.processar_nota_fiscal_do_job()`
- **Localização:** `apps/notas/services.py:26-34`
- **Lógica:**
  - PAGAR → `get_classifier('TIPO_PARCEIRO', 'FORNECEDOR')`
  - RECEBER → `get_classifier('TIPO_PARCEIRO', 'CLIENTE')`

### RN004 - Unicidade de CNPJ por Parceiro
- **Implementação:** `Parceiro.cnpj` (unique=True)
- **Localização:** `apps/parceiros/models.py:8`
- **Constraint:** Database unique constraint

### RN005 - Unicidade de CNPJ por Empresa
- **Implementação:** `MinhaEmpresa.cnpj` (unique=True)
- **Localização:** `apps/empresa/models.py:8`
- **Constraint:** Database unique constraint

### RN006 - Status de Processamento Sequencial
- **Implementação:** `processar_nota_fiscal_task()`
- **Localização:** `apps/processamento/tasks.py:9-25`
- **Fluxo:**
  1. PENDENTE (criação) → `ProcessarNotaFiscalView.post()`
  2. PROCESSANDO → `job.status = get_classifier('STATUS_JOB', 'PROCESSANDO')`
  3. CONCLUIDO/FALHA → `job.status = get_classifier('STATUS_JOB', 'CONCLUIDO/FALHA')`

### RN007 - Status de Lançamento Financeiro
- **Implementação:** `LancamentoFinanceiro.objects.create()`
- **Localização:** `apps/notas/services.py:50-57`
- **Default:** `status_pendente = get_classifier('STATUS_LANCAMENTO', 'PENDENTE')`

### RN008 - Relacionamento Obrigatório Nota-Lançamento
- **Implementação:** `LancamentoFinanceiro.nota_fiscal` (OneToOneField)
- **Localização:** `apps/financeiro/models.py:8`
- **Constraint:** Database foreign key constraint

### RN009 - Integridade de Valores
- **Implementação:** `LancamentoFinanceiro.valor = nota_fiscal.valor_total`
- **Localização:** `apps/notas/services.py:54`
- **Validação:** Valor copiado diretamente da nota fiscal

### RN010 - Proteção de Dados Relacionados
- **Implementação:** `on_delete=models.PROTECT` em ForeignKeys
- **Localização:** Todos os models com relacionamentos
- **Exemplos:**
  - `apps/notas/models.py:8` - `job_origem = models.ForeignKey(..., on_delete=models.PROTECT)`
  - `apps/financeiro/models.py:10` - `clf_tipo = models.ForeignKey(..., on_delete=models.PROTECT)`

### RN011 - Atualização Automática de Parceiros
- **Implementação:** `NotaFiscalService._get_or_create_parceiro()`
- **Localização:** `apps/notas/services.py:59-74`
- **Lógica:** `get_or_create()` + atualização condicional de nome e tipo

### RN012 - Segurança de Identificadores
- **Implementação:** Campos `uuid` em todos os models + `lookup_field = 'uuid'`
- **Localização:** 
  - Models: `apps/*/models.py` (campo `uuid`)
  - Views: `apps/processamento/views.py:25` (`lookup_field = 'uuid'`)

### RN013 - Processamento Assíncrono Obrigatório
- **Implementação:** `CeleryTaskPublisher.publish_processamento_nota()`
- **Localização:** `apps/processamento/views.py:19`
- **Task:** `@shared_task processar_nota_fiscal_task()`

### RN014 - Filtros de Consulta Financeira
- **Implementação:** `get_queryset()` nas views financeiras
- **Localização:** 
  - `apps/financeiro/views.py:6-14` (ContasAPagarListView)
  - `apps/financeiro/views.py:16-24` (ContasAReceberListView)
- **Filtros:** `filter(clf_tipo=tipo, clf_status=status).order_by('data_vencimento')`

### RN015 - Transacionalidade de Processamento
- **Implementação:** `@transaction.atomic`
- **Localização:** `apps/notas/services.py:15`
- **Escopo:** Todo o método `processar_nota_fiscal_do_job()`

## Cobertura de Testes

| Componente | Testes Unitários | Testes Integração | Cobertura |
|------------|------------------|-------------------|-----------|
| Models | ❌ | ❌ | 0% |
| Services | ❌ | ❌ | 0% |
| Views | ❌ | ❌ | 0% |
| Tasks | ❌ | ❌ | 0% |
| Extractors | ❌ | ❌ | 0% |

**Status:** Sistema sem cobertura de testes automatizados.

## Endpoints vs Requisitos

| Endpoint | Método | Requisito | Status |
|----------|--------|-----------|--------|
| `/api/processar-nota/` | POST | RF001 | ✅ Implementado |
| `/api/jobs/` | GET | RF005 | ✅ Implementado |
| `/api/jobs/<uuid>/` | GET, POST, DELETE | RF005 | ✅ Implementado |
| `/api/contas-a-pagar/` | GET | RF006 | ✅ Implementado |
| `/api/contas-a-receber/` | GET | RF007 | ✅ Implementado |
| `/api/dashboard/` | GET | RF008 | ✅ Implementado |
| `/api/calendar-resumo/` | GET | RF011 | ✅ Implementado |
| `/api/calendar-dia/` | GET | RF011 | ✅ Implementado |
| `/api/notas-fiscais/` | GET, POST, PUT, DELETE | - | ✅ Implementado |
| `/api/unclassified-companies/` | GET | - | ✅ Implementado |
| `/api/auth/login/` | POST | - | ✅ Implementado |
| `/api/auth/setup-senha/` | POST | - | ✅ Implementado |
| `/api/notifications/register-device/` | POST | - | ✅ Implementado |
| `/api/notifications/pending/` | GET | - | ✅ Implementado |
| `/api/notifications/ack/` | POST | - | ✅ Implementado |

## Dependências Externas

| Componente | Dependência | Propósito | Criticidade |
|------------|-------------|-----------|-------------|
| Celery | RabbitMQ | Processamento assíncrono | Alta |
| Django ORM | PostgreSQL | Persistência de dados | Alta |
| Extractor | Simulado | Extração de dados (placeholder) | Alta |
| Docker | Compose | Orquestração de containers | Média |

## Pontos de Atenção

1. **Extrator Simulado:** Implementação atual usa dados mockados
2. **Ausência de Testes:** Sistema sem cobertura de testes
3. **Validação de CNPJ:** Não há validação de formato de CNPJ
4. **Tratamento de Erros:** Limitado a try/catch básico
5. **Logs:** Ausência de logging estruturado
6. **Monitoramento:** Sem métricas de performance ou saúde