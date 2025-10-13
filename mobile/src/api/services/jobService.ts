import { api } from '../client';
import { endpoints } from '../endpoints';
import { JobStatus } from '../../types';
import { Platform } from 'react-native';

export const uploadNota = async (
  vars: { file: { uri: string; name: string; type: string }; meu_cnpj?: string }
) => {
  const form = new FormData();
  if (Platform.OS === 'web') {
    // In web, axios/XHR expects a Blob/File, not RN's { uri, name, type }
    const res = await fetch(vars.file.uri);
    const blob = await res.blob();
    form.append('arquivo', blob, vars.file.name);
  } else {
    // Native (iOS/Android) accepts RN file descriptor
    // @ts-ignore RN FormData compat
    form.append('arquivo', { uri: vars.file.uri, name: vars.file.name, type: vars.file.type } as any);
  }
  if (vars.meu_cnpj) {
    form.append('meu_cnpj', vars.meu_cnpj);
  }
  const res = await api.post(endpoints.processarNota, form);
  const data: any = res.data || {};
  const job_uuid: string = data.job_uuid || data.uuid;
  const message: string = data.message || 'Arquivo enviado. Processamento iniciado.';
  return { message, job_uuid } as { message: string; job_uuid: string };
};

export const getJobStatus = async (uuid: string) => {
  const res = await api.get(endpoints.jobStatus(uuid));
  const raw: any = res.data || {};

  const statusCodigo: string = typeof raw.status === 'string' ? raw.status : raw.status?.codigo;
  const statusDescricao: string | undefined =
    typeof raw.status === 'string' ? raw.status : raw.status?.descricao;

  const normalized: JobStatus = {
    uuid: raw.uuid,
    status: { codigo: statusCodigo, descricao: statusDescricao ?? statusCodigo },
    dt_conclusao: raw.dt_conclusao ?? null,
    erro: raw.erro ?? raw.mensagem_erro ?? null,
  };

  return normalized;
};

export const reprocessJob = async (uuid: string) => {
  // POST to the jobStatus URL triggers processing for that job (backend accepts POST on the same resource)
  const res = await api.post(endpoints.jobStatus(uuid));
  return res.data || {};
};

export const deleteJob = async (uuid: string) => {
  const res = await api.delete(endpoints.jobStatus(uuid));
  return res;
};

export const listJobs = async () => {
  const res = await api.get(endpoints.listJobs);
  return res.data as JobStatus[];
};