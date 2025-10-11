import { api } from '../client';
import { endpoints } from '../endpoints';
import { Lancamento } from '../../types';

export const getContasAPagar = async () => {
  const res = await api.get(endpoints.contasAPagar);
  return res.data as Lancamento[];
};

export const getContasAReceber = async () => {
  const res = await api.get(endpoints.contasAReceber);
  return res.data as Lancamento[];
};