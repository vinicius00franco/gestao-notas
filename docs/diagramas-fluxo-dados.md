# Diagramas de Fluxo de Dados - Sistema de Gestão de Notas Fiscais

## DFD Nível 0 - Contexto Geral

```mermaid
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

## DFD Nível 1 - Processos Principais

```mermaid
graph TD
    Cliente[Cliente] --> P1[1.0 Processar Nota Fiscal]
    Cliente --> P2[2.0 Consultar Status Job]
    Cliente --> P3[3.0 Listar Contas a Pagar]
    Cliente --> P4[4.0 Listar Contas a Receber]
    Cliente --> P5[5.0 Dashboard]
    
    P1 --> D1[(D1: Jobs)]
    P1 --> D2[(D2: Empresas)]
    P1 --> Fila[Fila Processamento]
    
    P2 --> D1
    P3 --> D3[(D3: Lançamentos)]
    P4 --> D3
    P5 --> D3
    P5 --> D4[(D4: Parceiros)]
    
    Fila --> P6[6.0 Processar Assíncrono]
    P6 --> D1
    P6 --> D5[(D5: Notas Fiscais)]
    P6 --> D3
    P6 --> D4
```

## DFD Nível 2 - Detalhamento por Funcionalidade

### 1.0 Processar Nota Fiscal

```mermaid
graph TD
    Cliente[Cliente] -->|arquivo + CNPJ| P11[1.1 Validar Upload]
    P11 -->|dados válidos| P12[1.2 Buscar Empresa]
    P12 -->|empresa encontrada| P13[1.3 Criar Job]
    P13 -->|job criado| P14[1.4 Enviar para Fila]
    P14 -->|UUID + status| Cliente
    
    P12 --> D2[(D2: Empresas)]
    P13 --> D1[(D1: Jobs)]
    P14 --> Fila[Fila Celery]
```

### 6.0 Processar Assíncrono

```mermaid
graph TD
    Fila[Fila Celery] -->|job_id| P61[6.1 Extrair Dados]
    P61 -->|dados extraídos| P62[6.2 Validar Propriedade]
    P62 -->|válido| P63[6.3 Classificar Tipo]
    P63 -->|tipo definido| P64[6.4 Gerenciar Parceiro]
    P64 -->|parceiro| P65[6.5 Criar Nota Fiscal]
    P65 -->|nota criada| P66[6.6 Criar Lançamento]
    P66 -->|lançamento criado| P67[6.7 Atualizar Status Job]
    
    P64 --> D4[(D4: Parceiros)]
    P65 --> D5[(D5: Notas Fiscais)]
    P66 --> D3[(D3: Lançamentos)]
    P67 --> D1[(D1: Jobs)]
```

### 2.0 Consultar Status Job

```mermaid
graph TD
    Cliente[Cliente] -->|UUID| P21[2.1 Buscar Job]
    P21 -->|job encontrado| P22[2.2 Serializar Dados]
    P22 -->|dados serializados| Cliente
    
    P21 --> D1[(D1: Jobs)]
```

### 3.0 Listar Contas a Pagar

```mermaid
graph TD
    Cliente[Cliente] -->|requisição| P31[3.1 Filtrar Lançamentos]
    P31 -->|TIPO=PAGAR, STATUS=PENDENTE| P32[3.2 Ordenar por Vencimento]
    P32 -->|lista ordenada| P33[3.3 Serializar com Parceiros]
    P33 -->|dados serializados| Cliente
    
    P31 --> D3[(D3: Lançamentos)]
    P33 --> D4[(D4: Parceiros)]
```

### 4.0 Listar Contas a Receber

```mermaid
graph TD
    Cliente[Cliente] -->|requisição| P41[4.1 Filtrar Lançamentos]
    P41 -->|TIPO=RECEBER, STATUS=PENDENTE| P42[4.2 Ordenar por Vencimento]
    P42 -->|lista ordenada| P43[4.3 Serializar com Parceiros]
    P43 -->|dados serializados| Cliente
    
    P41 --> D3[(D3: Lançamentos)]
    P43 --> D4[(D4: Parceiros)]
```

### 5.0 Dashboard

```mermaid
graph TD
    Cliente[Cliente] -->|requisição| P51[5.1 Consulta SQL Agregada]
    P51 -->|dados agregados| P52[5.2 Formatar Top 5]
    P52 -->|top 5 fornecedores| Cliente
    
    P51 --> D3[(D3: Lançamentos)]
    P51 --> D4[(D4: Parceiros)]
```

## Fluxo de Dados Detalhado

### Estruturas de Dados

**Upload Request:**
```
{
  arquivo: File,
  meu_cnpj: String
}
```

**Job Response:**
```
{
  uuid: UUID,
  status: {codigo: String, descricao: String}
}
```

**Job Status Response:**
```
{
  uuid: UUID,
  status: String,
  dt_criacao: DateTime,
  dt_conclusao: DateTime,
  mensagem_erro: String
}
```

**Lançamento Response:**
```
{
  uuid: UUID,
  descricao: String,
  valor: Decimal,
  data_vencimento: Date,
  data_pagamento: Date,
  clf_tipo: {codigo: String, descricao: String},
  clf_status: {codigo: String, descricao: String},
  dt_criacao: DateTime,
  dt_alteracao: DateTime
}
```

**Dashboard Response:**
```
{
  top_5_fornecedores_pendentes: [
    {
      nome: String,
      cnpj: String,
      total_a_pagar: Decimal
    }
  ]
}
```

## Armazenamento de Dados

### Entidades Principais
- **Jobs:** Controle de processamento
- **Empresas:** Cadastro da empresa usuária
- **Parceiros:** Fornecedores e clientes
- **Notas Fiscais:** Documentos processados
- **Lançamentos:** Movimentações financeiras
- **Classificadores:** Tipos e status padronizados

### Relacionamentos
- Job 1:N Notas Fiscais
- Nota Fiscal 1:1 Lançamento Financeiro
- Parceiro 1:N Notas Fiscais
- Empresa 1:N Jobs
- Classificador 1:N (Jobs, Lançamentos, Parceiros)