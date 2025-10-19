# Diagramas de Sequência - Sistema de Gestão de Notas Fiscais

## 1. POST /api/processar-nota/ - Processamento de Nota Fiscal

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

    C->>V: POST /api/processar-nota/<br/>{arquivo, meu_cnpj}
    V->>S: serializer.is_valid()
    S-->>V: validated_data
    V->>E: MinhaEmpresa.objects.get(cnpj)
    E-->>V: empresa
    V->>CL: get_classifier('STATUS_JOB', 'PENDENTE')
    CL-->>V: status_pendente
    V->>J: JobProcessamento.objects.create()
    J-->>V: job
    V->>P: publish_processamento_nota(job.id)
    P->>Q: processar_nota_fiscal_task.delay()
    Q-->>P: task_id
    P-->>V: task enviada
    V-->>C: 202 ACCEPTED<br/>{uuid, status}
```

## 2. Processamento Assíncrono (Celery Task)

```mermaid
sequenceDiagram
    participant Q as RabbitMQ
    participant T as processar_nota_fiscal_task
    participant J as JobProcessamento
    participant CL as Classificador
    participant EX as SimulatedExtractor
    participant NS as NotaFiscalService
    participant P as Parceiro
    participant NF as NotaFiscal
    participant LF as LancamentoFinanceiro

    Q->>T: processar_nota_fiscal_task(job_id)
    T->>J: JobProcessamento.objects.get(pk=job_id)
    J-->>T: job
    T->>CL: get_classifier('STATUS_JOB', 'PROCESSANDO')
    CL-->>T: status_processando
    T->>J: job.status = status_processando
    T->>EX: extractor.extract(file_content, filename)
    EX-->>T: dados_extraidos
    T->>NS: service.processar_nota_fiscal_do_job(job)
    
    Note over NS: @transaction.atomic
    NS->>NS: validar propriedade da nota
    NS->>CL: get_classifier('TIPO_LANCAMENTO', tipo)
    CL-->>NS: tipo_lancamento
    NS->>CL: get_classifier('TIPO_PARCEIRO', tipo)
    CL-->>NS: tipo_parceiro
    NS->>P: get_or_create_parceiro()
    P-->>NS: parceiro
    NS->>NF: NotaFiscal.objects.create()
    NF-->>NS: nota_fiscal
    NS->>CL: get_classifier('STATUS_LANCAMENTO', 'PENDENTE')
    CL-->>NS: status_pendente
    NS->>LF: LancamentoFinanceiro.objects.create()
    LF-->>NS: lancamento
    NS-->>T: lancamento
    
    T->>CL: get_classifier('STATUS_JOB', 'CONCLUIDO')
    CL-->>T: status_concluido
    T->>J: job.status = status_concluido
    T->>J: job.dt_conclusao = now()
```

## 3. GET /api/jobs/<uuid>/ - Consulta Status do Job

```mermaid
sequenceDiagram
    participant C as Cliente
    participant V as JobStatusView
    participant J as JobProcessamento
    participant S as JobProcessamentoSerializer

    C->>V: GET /api/jobs/{uuid}/
    V->>J: JobProcessamento.objects.get(uuid=uuid)
    J-->>V: job
    V->>S: JobProcessamentoSerializer(job)
    S-->>V: serialized_data
    V-->>C: 200 OK<br/>{uuid, status, dt_criacao, dt_conclusao, mensagem_erro}
```

## 4. GET /api/contas-a-pagar/ - Listar Contas a Pagar

```mermaid
sequenceDiagram
    participant C as Cliente
    participant V as ContasAPagarListView
    participant CL as Classificador
    participant LF as LancamentoFinanceiro
    participant S as LancamentoFinanceiroSerializer

    C->>V: GET /api/contas-a-pagar/
    V->>CL: get_classifier('TIPO_LANCAMENTO', 'PAGAR')
    CL-->>V: tipo_pagar
    V->>CL: get_classifier('STATUS_LANCAMENTO', 'PENDENTE')
    CL-->>V: status_pendente
    V->>LF: filter(clf_tipo=tipo, clf_status=status)<br/>.select_related('nota_fiscal__parceiro')<br/>.order_by('data_vencimento')
    LF-->>V: queryset
    V->>S: LancamentoFinanceiroSerializer(queryset, many=True)
    S-->>V: serialized_data
    V-->>C: 200 OK<br/>[{lancamentos_a_pagar}]
```

## 5. GET /api/contas-a-receber/ - Listar Contas a Receber

```mermaid
sequenceDiagram
    participant C as Cliente
    participant V as ContasAReceberListView
    participant CL as Classificador
    participant LF as LancamentoFinanceiro
    participant S as LancamentoFinanceiroSerializer

    C->>V: GET /api/contas-a-receber/
    V->>CL: get_classifier('TIPO_LANCAMENTO', 'RECEBER')
    CL-->>V: tipo_receber
    V->>CL: get_classifier('STATUS_LANCAMENTO', 'PENDENTE')
    CL-->>V: status_pendente
    V->>LF: filter(clf_tipo=tipo, clf_status=status)<br/>.select_related('nota_fiscal__parceiro')<br/>.order_by('data_vencimento')
    LF-->>V: queryset
    V->>S: LancamentoFinanceiroSerializer(queryset, many=True)
    S-->>V: serialized_data
    V-->>C: 200 OK<br/>[{lancamentos_a_receber}]
```

## 6. GET /api/dashboard/ - Dashboard Gerencial

```mermaid
sequenceDiagram
    participant C as Cliente
    participant V as DashboardStatsView
    participant SEL as get_top_fornecedores_pendentes
    participant DB as Database

    C->>V: GET /api/dashboard/
    V->>SEL: get_top_fornecedores_pendentes()
    SEL->>DB: Raw SQL Query<br/>JOIN parceiros, notas_fiscais, lancamentos<br/>WHERE tipo=PAGAR AND status=PENDENTE<br/>GROUP BY parceiro<br/>ORDER BY total DESC LIMIT 5
    DB-->>SEL: result_rows
    SEL->>SEL: format as dict list
    SEL-->>V: top_5_fornecedores
    V-->>C: 200 OK<br/>{top_5_fornecedores_pendentes: [...]}
```

## 7. Fluxo de Erro - Processamento com Falha

```mermaid
sequenceDiagram
    participant Q as RabbitMQ
    participant T as processar_nota_fiscal_task
    participant J as JobProcessamento
    participant CL as Classificador
    participant NS as NotaFiscalService

    Q->>T: processar_nota_fiscal_task(job_id)
    T->>J: JobProcessamento.objects.get(pk=job_id)
    J-->>T: job
    T->>CL: get_classifier('STATUS_JOB', 'PROCESSANDO')
    CL-->>T: status_processando
    T->>J: job.status = status_processando
    T->>NS: service.processar_nota_fiscal_do_job(job)
    NS-->>T: Exception("Nota fiscal não pertence à sua empresa")
    T->>CL: get_classifier('STATUS_JOB', 'FALHA')
    CL-->>T: status_falha
    T->>J: job.status = status_falha
    T->>J: job.mensagem_erro = str(e)
    T->>J: job.dt_conclusao = now()
```

## 8. Middleware de Versionamento (Opcional)

```mermaid
sequenceDiagram
    participant C as Cliente
    participant M as ApiVersionFallbackMiddleware
    participant V as View

    C->>M: GET /api/v15/contas-a-pagar/
    M->>M: check version fallback rules<br/>v15 → v10
    M->>M: rewrite path to /api/v10/contas-a-pagar/
    M->>V: forward request
    V-->>M: response
    M-->>C: response
```

## Padrões de Interação Identificados

### 1. **Padrão Request-Response Síncrono**
- Usado em: consultas (jobs, contas, dashboard)
- Características: resposta imediata, operações de leitura

### 2. **Padrão Request-Acknowledge-Process Assíncrono**
- Usado em: processamento de notas fiscais
- Características: resposta imediata com UUID, processamento em background

### 3. **Padrão Repository com ORM**
- Usado em: todas as operações de dados
- Características: abstração de banco via Django ORM

### 4. **Padrão Publisher-Subscriber**
- Usado em: envio de tarefas para Celery
- Características: desacoplamento via fila de mensagens

### 5. **Padrão Transaction Script**
- Usado em: processamento completo da nota fiscal
- Características: operação atômica com rollback automático

### 6. **Padrão Strategy**
- Usado em: extração de dados (ExtractorInterface)
- Características: algoritmo plugável para diferentes tipos de arquivo