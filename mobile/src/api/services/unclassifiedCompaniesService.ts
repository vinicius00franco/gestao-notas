import { api } from '../client';
import { endpoints } from '../endpoints';
import { UnclassifiedCompany } from '../../types';

export const getUnclassifiedCompanies = async () => {
  const res = await api.get(endpoints.unclassifiedCompanies);
  return res.data as UnclassifiedCompany[];
}

export const updateUnclassifiedCompany = async (company: UnclassifiedCompany) => {
  const res = await api.put(endpoints.updateUnclassifiedCompany(company.id), company);
  return res.data;
};