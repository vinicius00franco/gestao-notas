export type JobStatus = {
  uuid: string;
  status: { codigo: string; descricao: string };
  dt_conclusao?: string | null;
  erro?: string | null;
};

export type Lancamento = {
  uuid: string;
  descricao: string;
  valor: number;
  data_vencimento: string;
  data_pagamento: string | null;
  clf_tipo: any;
  clf_status: any;
  dt_criacao: string;
  dt_alteracao: string;
};

export type TopFornecedor = { nome: string; cnpj: string; total_a_pagar: number };

export type UnclassifiedCompany = {
  id: number;
  nome_fantasia: string;
  razao_social: string;
  cnpj: string;
  logradouro: string;
  numero: string;
  bairro: string;
  cidade: string;
  uf: string;
  cep: string;
  telefone: string;
  email: string;
  classification: string;
};

export type NotaFiscal = {
  id: string;
  numero: string;
  valor: number;
  cnpj_emitente: string;
  nome_emitente: string;
  classificacao_id: string;
};

export type Classificacao = {
  id: string;
  nome: string;
};