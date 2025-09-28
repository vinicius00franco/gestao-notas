# Regras de Negócio - Sistema de Gestão de Notas Fiscais

## RN001 - Validação de Propriedade da Nota Fiscal
**Descrição:** Uma nota fiscal só pode ser processada se a empresa informada participar como remetente ou destinatário.
**Condição:** CNPJ da empresa deve corresponder ao remetente OU destinatário da nota
**Ação:** Se não corresponder, rejeitar processamento com erro
**Justificativa:** Garantir que apenas notas fiscais relacionadas à empresa sejam processadas

## RN002 - Classificação Automática de Tipo de Lançamento
**Descrição:** O tipo de lançamento financeiro é determinado automaticamente pela posição da empresa na nota fiscal.
**Regras:**
- Se empresa é DESTINATÁRIO: criar lançamento tipo PAGAR (conta a pagar)
- Se empresa é REMETENTE: criar lançamento tipo RECEBER (conta a receber)
**Justificativa:** Automatizar a classificação contábil baseada no fluxo comercial

## RN003 - Classificação Automática de Parceiros
**Descrição:** O tipo de parceiro é determinado automaticamente pelo tipo de lançamento gerado.
**Regras:**
- Se lançamento é PAGAR: parceiro é classificado como FORNECEDOR
- Se lançamento é RECEBER: parceiro é classificado como CLIENTE
**Justificativa:** Manter consistência entre relacionamento comercial e classificação contábil

## RN004 - Unicidade de CNPJ por Parceiro
**Descrição:** Cada CNPJ pode ter apenas um registro de parceiro no sistema.
**Regras:**
- CNPJ deve ser único na base de parceiros
- Se parceiro já existe, atualizar nome e tipo se necessário
- Não permitir duplicação de CNPJs
**Justificativa:** Evitar duplicação de dados e manter integridade referencial

## RN005 - Unicidade de CNPJ por Empresa
**Descrição:** Cada CNPJ pode ter apenas um registro de empresa no sistema.
**Regras:**
- CNPJ deve ser único na base de empresas
- Validar CNPJ antes de processar nota fiscal
**Justificativa:** Garantir identificação única das empresas no sistema

## RN006 - Status de Processamento Sequencial
**Descrição:** O processamento de jobs deve seguir uma sequência específica de status.
**Sequência:** PENDENTE → PROCESSANDO → CONCLUIDO/FALHA
**Regras:**
- Job inicia sempre como PENDENTE
- Muda para PROCESSANDO ao iniciar processamento
- Finaliza como CONCLUIDO (sucesso) ou FALHA (erro)
- Registrar data/hora de conclusão
**Justificativa:** Controlar o ciclo de vida do processamento e permitir rastreabilidade

## RN007 - Status de Lançamento Financeiro
**Descrição:** Lançamentos financeiros iniciam sempre como PENDENTE.
**Regras:**
- Todo lançamento criado automaticamente tem status PENDENTE
- Status pode evoluir para PAGO/RECEBIDO posteriormente
- Data de pagamento só é preenchida quando status muda
**Justificativa:** Controlar o ciclo de vida dos lançamentos financeiros

## RN008 - Relacionamento Obrigatório Nota-Lançamento
**Descrição:** Todo lançamento financeiro deve estar vinculado a uma nota fiscal.
**Regras:**
- Relacionamento OneToOne entre NotaFiscal e LancamentoFinanceiro
- Não permitir lançamentos órfãos
- Exclusão de nota fiscal deve ser protegida se houver lançamento
**Justificativa:** Manter rastreabilidade e origem dos lançamentos financeiros

## RN009 - Integridade de Valores
**Descrição:** O valor do lançamento financeiro deve corresponder ao valor total da nota fiscal.
**Regras:**
- Valor do lançamento = Valor total da nota fiscal
- Não permitir divergências entre valores
- Manter precisão decimal (2 casas)
**Justificativa:** Garantir consistência contábil e financeira

## RN010 - Proteção de Dados Relacionados
**Descrição:** Registros com relacionamentos não podem ser excluídos diretamente.
**Regras:**
- Parceiros com notas fiscais: PROTECT
- Empresas com jobs: PROTECT
- Classificadores em uso: PROTECT
- Jobs com notas fiscais: PROTECT
**Justificativa:** Manter integridade referencial e histórico de dados

## RN011 - Atualização Automática de Parceiros
**Descrição:** Dados de parceiros devem ser atualizados automaticamente quando houver divergência.
**Regras:**
- Se nome do parceiro mudou: atualizar automaticamente
- Se tipo do parceiro mudou: atualizar automaticamente
- Manter histórico através de auditoria
**Justificativa:** Manter dados atualizados sem intervenção manual

## RN012 - Segurança de Identificadores
**Descrição:** IDs internos não devem ser expostos publicamente.
**Regras:**
- APIs públicas usam UUID em vez de ID numérico
- IDs numéricos apenas para relacionamentos internos
- UUIDs únicos e não sequenciais
**Justificativa:** Aumentar segurança e evitar exposição de estrutura interna

## RN013 - Processamento Assíncrono Obrigatório
**Descrição:** Processamento de notas fiscais deve ser sempre assíncrono.
**Regras:**
- Upload retorna imediatamente com UUID do job
- Processamento real executado via Celery
- Cliente consulta status via UUID
**Justificativa:** Evitar timeouts e melhorar experiência do usuário

## RN014 - Filtros de Consulta Financeira
**Descrição:** Consultas financeiras devem filtrar apenas registros relevantes.
**Regras:**
- Contas a pagar: apenas TIPO_LANCAMENTO=PAGAR e STATUS=PENDENTE
- Contas a receber: apenas TIPO_LANCAMENTO=RECEBER e STATUS=PENDENTE
- Ordenar sempre por data de vencimento
**Justificativa:** Apresentar apenas informações úteis para gestão financeira

## RN015 - Transacionalidade de Processamento
**Descrição:** Processamento de nota fiscal deve ser atômico.
**Regras:**
- Usar transação de banco para todo o processamento
- Em caso de erro, reverter todas as operações
- Garantir consistência dos dados
**Justificativa:** Evitar estados inconsistentes em caso de falha