import axios from 'axios';
import Constants from 'expo-constants';
import { Platform } from 'react-native';

// Resolve API base URL with the following priority:
// 1) API_BASE_URL provided via app.config extra (from mobile/.env)
// 2) If running on device (not web), derive LAN IP from Expo host and use port 80 (nginx) by default
// 3) Fallback to localhost:8000 (useful for web)
const extraApiBase =
  (Constants as any)?.expoConfig?.extra?.apiBaseUrl ||
  (Constants as any)?.manifest?.extra?.apiBaseUrl;

let derivedDefault = 'http://localhost:8000';
if (Platform.OS !== 'web') {
  const hostUri = (Constants as any)?.expoConfig?.hostUri || (Constants as any)?.manifest?.debuggerHost;
  const host = hostUri?.split(':')?.[0];
  if (host) {
    // docker-compose exposes nginx on host port 80 by default
    derivedDefault = `http://${host}:80`;
  }
}

const apiBaseUrl = extraApiBase || derivedDefault;

export const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 15000,
});

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
};

export const uploadNota = async (
  vars: { file: { uri: string; name: string; type: string }; meu_cnpj: string }
) => {
  const form = new FormData();
  // @ts-ignore RN FormData compat
  form.append('arquivo', { uri: vars.file.uri, name: vars.file.name, type: vars.file.type } as any);
  form.append('meu_cnpj', vars.meu_cnpj);
  const res = await api.post(endpoints.processarNota, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data as { uuid: string; status: { codigo: string; descricao: string } };
};

export const getJobStatus = async (uuid: string) => {
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
