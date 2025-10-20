# Diagramas IDEF0 e IDEF1 - Sistema de Gestão de Notas Fiscais

## Visão Geral

Este documento apresenta os diagramas IDEF0 (Function Modeling) e IDEF1 (Information Modeling) do Sistema de Gestão de Notas Fiscais, seguindo as melhores práticas de modelagem de processos de negócio.

## Diagramas IDEF0 (Modelagem Funcional)

### 1. IDEF0 - Nível A0 (Contexto Geral)
**Arquivo:** `idef0_gestao_notas.puml`

Representa a visão de mais alto nível do sistema, mostrando:
- **Entradas:** Arquivos de notas fiscais, CNPJ da empresa, dados de classificação
- **Controles:** Regras de negócio, políticas de validação, configurações
- **Saídas:** Notas processadas, lançamentos financeiros, relatórios, notificações
- **Mecanismos:** Django, PostgreSQL, Celery, LLM/OCR, RabbitMQ, Nginx, Grafana

### 2. IDEF0 - Nível A1 (Decomposição Principal)
**Arquivo:** `idef0_gestao_notas_a1.puml`

Decompõe o processo principal em 5 subprocessos:
- **A1:** Receber e Validar Notas Fiscais
- **A2:** Extrair Dados das Notas
- **A3:** Classificar e Persistir Dados
- **A4:** Gerar Lançamentos Financeiros
- **A5:** Gerar Relatórios e Dashboards

### 3. IDEF0 - Nível A2 (Processamento Detalhado)
**Arquivo:** `idef0_processamento_detalhado.puml`

Detalha o processo de extração de dados (A2) em 6 subprocessos:
- **A2.1:** Upload e Validação Inicial
- **A2.2:** Detectar Duplicatas
- **A2.3:** Extrair Dados por Estratégia
- **A2.4:** Validar Dados Extraídos
- **A2.5:** Criar Job Processamento
- **A2.6:** Processar Assíncrono

## Diagramas IDEF1 (Modelagem de Informação)

### 1. IDEF1 - Modelo de Dados Principal
**Arquivo:** `idef1_gestao_notas.puml`

Apresenta o modelo de dados completo com as principais entidades:
- **MinhaEmpresa:** Empresas do usuário do sistema
- **EmpresaNaoClassificada:** Empresas identificadas mas não classificadas
- **JobProcessamento:** Jobs de processamento de notas
- **Parceiro:** Fornecedores e clientes
- **NotaFiscal:** Notas fiscais processadas
- **NotaFiscalItem:** Itens das notas fiscais
- **LancamentoFinanceiro:** Lançamentos financeiros gerados
- **Classificador:** Tabela de domínio para classificações
- **Notification:** Sistema de notificações

### 2. IDEF1 - Fluxo de Dados
**Arquivo:** `idef1_fluxo_dados.puml`

Mostra o fluxo detalhado de dados entre:
- **Armazenamentos (D1-D8):** Arquivos, Jobs, Notas, Parceiros, Lançamentos, etc.
- **Processos (P1-P7):** Upload, Validação, Extração, Classificação, etc.
- **Entidades Externas:** Usuário, Celery Worker, LLM Service, Sistema de Notificação

## Características dos Diagramas

### Conformidade com Padrões IDEF
- **IDEF0:** Foco em funções e atividades com notação ICOMs (Input, Control, Output, Mechanism)
- **IDEF1:** Foco em dados e informações com entidades, relacionamentos e fluxos

### Boas Práticas Aplicadas
1. **Hierarquia Clara:** Decomposição top-down do A0 para níveis mais detalhados
2. **Numeração Consistente:** A0 → A1-A5 → A2.1-A2.6
3. **ICOMs Bem Definidos:** Separação clara entre entradas, controles, saídas e mecanismos
4. **Rastreabilidade:** Conexão entre processos e dados
5. **Abstração Adequada:** Cada nível com o nível de detalhe apropriado

### Elementos Técnicos Mapeados
- **Arquitetura Django:** Apps, models, views, services
- **Padrões de Design:** Strategy, Observer, Repository
- **Tecnologias:** PostgreSQL, Celery, RabbitMQ, LLM
- **Fluxos Assíncronos:** Jobs, tasks, workers
- **Validações:** Duplicidade, CNPJ, formatos de arquivo

## Como Usar os Diagramas

### Para Desenvolvedores
- Entender a arquitetura geral do sistema
- Identificar pontos de integração entre componentes
- Mapear fluxos de dados e dependências

### Para Analistas de Negócio
- Compreender os processos de negócio
- Identificar regras e controles aplicados
- Validar requisitos funcionais

### Para Arquitetos de Sistema
- Avaliar a estrutura de dados
- Identificar gargalos e pontos de otimização
- Planejar evoluções do sistema

## Ferramentas de Visualização

Os diagramas estão em formato PlantUML (.puml) e podem ser visualizados usando:
- **VS Code:** Extensão PlantUML
- **IntelliJ IDEA:** Plugin PlantUML
- **Online:** plantuml.com
- **CLI:** plantuml.jar

## Manutenção dos Diagramas

Os diagramas devem ser atualizados quando:
- Novos processos forem adicionados
- Estrutura de dados for modificada
- Fluxos de integração mudarem
- Novas tecnologias forem incorporadas

---

**Versão:** 1.0  
**Data:** 2024  
**Autor:** Sistema de Gestão de Notas Fiscais