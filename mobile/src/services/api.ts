import axios from 'axios';
import Constants from 'expo-constants';
import { Platform } from 'react-native';

// Resolve API base URL with priority:
// 1. API_BASE_URL from Expo config (via .env)
// 2. Fallback to a sensible default for local dev
const apiBaseUrl =
  (Constants.expoConfig?.extra?.apiBaseUrl as string) || 'http://localhost:8080';

export const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 15000,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
});

export function setAuthToken(token?: string) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete (api.defaults.headers.common as any)['Authorization'];
  }
}

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

export const endpoints = {
  processarNota: '/api/processar-nota/',
  jobStatus: (uuid: string) => `/api/jobs/${uuid}/`,
  contasAPagar: '/api/contas-a-pagar/',
  contasAReceber: '/api/contas-a-receber/',
  dashboard: '/api/dashboard/',
  unclassifiedCompanies: '/api/unclassified-companies/',
  updateUnclassifiedCompany: (id: number) => `/api/unclassified-companies/${id}/`,
};

export const uploadNota = async (
  vars: { file: { uri: string; name: string; type: string }; meu_cnpj: string }
) => {
  if (process.env.NODE_ENV === 'development') {
    return Promise.resolve({
      message: 'Upload successful',
      job_uuid: 'mock-uuid',
    });
  }
  const form = new FormData();
  // @ts-ignore RN FormData compat
  form.append('arquivo', { uri: vars.file.uri, name: vars.file.name, type: vars.file.type } as any);
  form.append('meu_cnpj', vars.meu_cnpj);
  const res = await api.post(endpoints.processarNota, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data as { message: string; job_uuid: string };
};

export const getJobStatus = async (uuid: string) => {
  if (process.env.NODE_ENV === 'development' && uuid === 'mock-uuid') {
    return Promise.resolve({
      uuid: 'mock-uuid',
      status: { codigo: 'PROCESSANDO', descricao: 'Em processamento' },
    });
  }
  const res = await api.get(endpoints.jobStatus(uuid));
  return res.data as JobStatus;
};

export const getContasAPagar = async () => {
  const res = await api.get(endpoints.contasAPagar);
  return res.data as Lancamento[];
};

export const getContasAReceber = async () => {
  const res = await api.get(endpoints.contasAReceber);
  return res.data as Lancamento[];
};

export const getDashboard = async () => {
  const res = await api.get(endpoints.dashboard);
  return res.data as { top_5_fornecedores_pendentes: TopFornecedor[] };
};
