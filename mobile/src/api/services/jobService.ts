import { api } from '../client';
import { endpoints } from '../endpoints';
import { JobStatus } from '../../types';

export const uploadNota = async (
  vars: { file: { uri: string; name: string; type: string }; meu_cnpj?: string }
) => {
  const form = new FormData();
  // @ts-ignore RN FormData compat
  form.append('arquivo', { uri: vars.file.uri, name: vars.file.name, type: vars.file.type } as any);
  if (vars.meu_cnpj) {
    form.append('meu_cnpj', vars.meu_cnpj);
  }
  const res = await api.post(endpoints.processarNota, form);
  return res.data as { message: string; job_uuid: string };
};

export const getJobStatus = async (uuid: string) => {
  const res = await api.get(endpoints.jobStatus(uuid));
  return res.data as JobStatus;
};