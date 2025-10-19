# Requisitos Funcionais - Sistema de Gestão de Notas Fiscais

## RF001 - Processamento de Notas Fiscais
**Descrição:** O sistema deve permitir o upload e processamento assíncrono de arquivos de notas fiscais.
**Entrada:** Arquivo da nota fiscal + CNPJ da empresa
**Saída:** UUID do job de processamento + status inicial
**Prioridade:** Alta
**Critérios de Aceitação:**
- Aceitar upload de arquivos via multipart/form-data
- Validar CNPJ da empresa informada
- Criar job de processamento com status PENDENTE
- Retornar UUID único para acompanhamento
- Processar de forma assíncrona via Celery

## RF002 - Extração de Dados da Nota Fiscal
**Descrição:** O sistema deve extrair automaticamente dados estruturados das notas fiscais.
**Entrada:** Arquivo da nota fiscal
**Saída:** Dados estruturados (número, CNPJs, valores, datas)
**Prioridade:** Alta
**Critérios de Aceitação:**
- Extrair número da nota fiscal
- Identificar remetente (CNPJ e nome)
- Identificar destinatário (CNPJ e nome)
- Extrair valor total
- Extrair data de emissão e vencimento
- Suportar diferentes formatos de arquivo

## RF003 - Classificação Automática de Lançamentos
**Descrição:** O sistema deve classificar automaticamente os lançamentos financeiros baseado no CNPJ da empresa.
**Entrada:** Dados da nota fiscal + CNPJ da empresa
**Saída:** Lançamento classificado (PAGAR ou RECEBER)
**Prioridade:** Alta
**Critérios de Aceitação:**
- Se empresa é destinatário: criar conta A PAGAR
- Se empresa é remetente: criar conta A RECEBER
- Rejeitar notas onde empresa não participa
- Classificar parceiro como FORNECEDOR ou CLIENTE

## RF004 - Gestão de Parceiros
**Descrição:** O sistema deve gerenciar automaticamente o cadastro de parceiros comerciais.
**Entrada:** CNPJ e nome do parceiro
**Saída:** Parceiro cadastrado ou atualizado
**Prioridade:** Média
**Critérios de Aceitação:**
- Criar parceiro se não existir
- Atualizar dados se parceiro já existe
- Classificar como FORNECEDOR ou CLIENTE
- Manter histórico de relacionamento

## RF005 - Consulta de Status de Processamento
**Descrição:** O sistema deve permitir consultar o status de processamento de um job.
**Entrada:** UUID do job
**Saída:** Status atual e detalhes do processamento
**Prioridade:** Alta
**Critérios de Aceitação:**
- Consultar por UUID público
- Retornar status (PENDENTE, PROCESSANDO, CONCLUIDO, FALHA)
- Exibir mensagem de erro em caso de falha
- Mostrar data de conclusão quando aplicável

## RF006 - Listagem de Contas a Pagar
**Descrição:** O sistema deve listar todas as contas a pagar pendentes.
**Entrada:** Requisição de listagem
**Saída:** Lista de lançamentos a pagar ordenada por vencimento
**Prioridade:** Alta
**Critérios de Aceitação:**
- Filtrar apenas lançamentos tipo PAGAR
- Filtrar apenas status PENDENTE
- Ordenar por data de vencimento
- Incluir dados do parceiro (fornecedor)

## RF007 - Listagem de Contas a Receber
**Descrição:** O sistema deve listar todas as contas a receber pendentes.
**Entrada:** Requisição de listagem
**Saída:** Lista de lançamentos a receber ordenada por vencimento
**Prioridade:** Alta
**Critérios de Aceitação:**
- Filtrar apenas lançamentos tipo RECEBER
- Filtrar apenas status PENDENTE
- Ordenar por data de vencimento
- Incluir dados do parceiro (cliente)

## RF008 - Dashboard Gerencial
**Descrição:** O sistema deve fornecer informações consolidadas para gestão.
**Entrada:** Requisição de dashboard
**Saída:** Métricas e indicadores financeiros
**Prioridade:** Média
**Critérios de Aceitação:**
- Exibir top 5 fornecedores com maior valor pendente
- Consolidar valores por parceiro
- Ordenar por valor total pendente

## RF009 - Auditoria de Operações
**Descrição:** O sistema deve registrar informações de auditoria nas operações.
**Entrada:** Operação realizada
**Saída:** Log de auditoria
**Prioridade:** Baixa
**Critérios de Aceitação:**
- Registrar data/hora de criação
- Registrar data/hora de alteração
- Registrar usuário responsável
- Manter histórico de exclusões lógicas

## RF010 - Versionamento de API
**Descrição:** O sistema deve suportar versionamento de API com fallback.
**Entrada:** Requisição com versão específica
**Saída:** Resposta da versão apropriada
**Prioridade:** Baixa
**Critérios de Aceitação:**
- Suportar múltiplas versões simultaneamente
- Implementar fallback para versões intermediárias
- Manter compatibilidade com versões anteriores

## RF011 - Calendário Financeiro
**Descrição:** O sistema deve fornecer uma visão de calendário para os lançamentos financeiros.
**Entrada:** Requisição de resumo mensal ou diário
**Saída:** Dados agregados por mês ou detalhados por dia
**Prioridade:** Média
**Critérios de Aceitação:**
- Fornecer um resumo mensal de contas a pagar e a receber.
- Fornecer uma lista detalhada de lançamentos para um dia específico.