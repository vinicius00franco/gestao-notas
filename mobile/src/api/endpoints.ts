export const endpoints = {
  processarNota: '/api/processar-nota/',
  jobStatus: (uuid: string) => `/api/jobs/${uuid}/`,
  listJobs: '/api/jobs/',
  contasAPagar: '/api/contas-a-pagar/',
  contasAReceber: '/api/contas-a-receber/',
  dashboard: '/api/dashboard/',
  unclassifiedCompanies: '/api/unclassified-companies/',
  updateUnclassifiedCompany: (id: number) => `/api/unclassified-companies/${id}/`,
};