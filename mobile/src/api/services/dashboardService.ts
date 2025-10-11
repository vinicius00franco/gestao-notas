import { api } from '../client';
import { endpoints } from '../endpoints';
import { TopFornecedor } from '../../types';

export const getDashboard = async () => {
  const res = await api.get(endpoints.dashboard);
  return res.data as { top_5_fornecedores_pendentes: TopFornecedor[] };
};