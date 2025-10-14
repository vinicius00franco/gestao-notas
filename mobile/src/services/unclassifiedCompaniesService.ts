import { api } from '../api/client';
import { endpoints } from '../api/endpoints';
import { UnclassifiedCompany } from '../types';

export const getUnclassifiedCompanies = async () => {
  const res = await api.get(endpoints.unclassifiedCompanies);
  return res.data as UnclassifiedCompany[];
}

export const updateUnclassifiedCompany = async (company: UnclassifiedCompany) => {
  const id = (company as any).uuid;
  const res = await api.put(endpoints.updateUnclassifiedCompany(id), company);
  return res.data;
};