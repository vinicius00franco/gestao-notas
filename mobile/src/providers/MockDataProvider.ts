import { JobStatus, PaginatedResponse, TopFornecedor, Lancamento } from '../types';
import { mockJobsDB, createMockJob, extractMockNotaData, STATUS_OPTIONS, createMockDashboardData, mockLancamentosDB } from '../data/mockData';
import { AxiosResponse } from 'axios';
import { CalendarDiaResponse, CalendarResumoResponse, CalendarResumoDia, CalendarDiaItem } from '../api/services/calendarService';

const mockDelay = (ms: number) => new Promise(res => setTimeout(res, ms));

const simulateJobProcessing = (jobUuid: string) => {
  setTimeout(() => {
    const jobIndex = mockJobsDB.findIndex(j => j.uuid === jobUuid);
    if (jobIndex === -1) return;
    mockJobsDB[jobIndex].status = STATUS_OPTIONS.PROCESSANDO;

    setTimeout(() => {
      const extractionResult = extractMockNotaData();
      const finalJobIndex = mockJobsDB.findIndex(j => j.uuid === jobUuid);
      if (finalJobIndex === -1) return;

      if (extractionResult.success) {
        mockJobsDB[finalJobIndex].status = STATUS_OPTIONS.CONCLUIDO;
        mockJobsDB[finalJobIndex].numero_nota = extractionResult.numero;
      } else {
        mockJobsDB[finalJobIndex].status = STATUS_OPTIONS.ERRO;
        mockJobsDB[finalJobIndex].erro = extractionResult.error;
      }
      mockJobsDB[finalJobIndex].dt_conclusao = new Date().toISOString();
    }, 2000 + Math.random() * 3000);
  }, 1000 + Math.random() * 2000);
};

// --- Mock Service Implementations ---

export const MockJobService = {
  listJobs: async (): Promise<JobStatus[]> => {
    await mockDelay(300);
    return [...mockJobsDB].reverse();
  },
  listJobsPendentes: async (params: { page: number }): Promise<PaginatedResponse<JobStatus>> => {
    await mockDelay(300);
    const pendentes = mockJobsDB.filter(j => j.status.codigo === 'PENDENTE');
    return { results: pendentes, next: null, previous: null, count: pendentes.length };
  },
  listJobsConcluidos: async (params: { page: number }): Promise<PaginatedResponse<JobStatus>> => {
    await mockDelay(300);
    const concluidos = mockJobsDB.filter(j => j.status.codigo === 'CONCLUIDO');
    return { results: concluidos, next: null, previous: null, count: concluidos.length };
  },
  listJobsErros: async (params: { page: number }): Promise<PaginatedResponse<JobStatus>> => {
    await mockDelay(300);
    const erros = mockJobsDB.filter(j => j.status.codigo === 'ERRO');
    return { results: erros, next: null, previous: null, count: erros.length };
  },
  getJobStatus: async (uuid: string): Promise<JobStatus> => {
    await mockDelay(300);
    const job = mockJobsDB.find(j => j.uuid === uuid);
    if (!job) throw new Error('Job não encontrado');
    return job;
  },
  uploadNota: async (data: any): Promise<{ message: string; job_uuid: string; }> => {
    await mockDelay(1000);
    const newJob = createMockJob();
    mockJobsDB.push(newJob);
    simulateJobProcessing(newJob.uuid);
    return { message: 'Nota enviada para processamento!', job_uuid: newJob.uuid };
  },
  deleteJob: async (uuid: string): Promise<AxiosResponse> => {
    await mockDelay(500);
    const index = mockJobsDB.findIndex(j => j.uuid === uuid);
    if (index > -1) mockJobsDB.splice(index, 1);
    return { data: { message: 'Job deletado com sucesso (mock)' } } as AxiosResponse;
  },
  reprocessJob: async (uuid: string): Promise<AxiosResponse> => {
    await mockDelay(500);
    const jobIndex = mockJobsDB.findIndex(j => j.uuid === uuid);
    if (jobIndex > -1) {
      mockJobsDB[jobIndex].status = STATUS_OPTIONS.PENDENTE;
      mockJobsDB[jobIndex].erro = undefined;
      mockJobsDB[jobIndex].dt_conclusao = undefined;
      simulateJobProcessing(uuid);
    }
    return { data: { message: 'Job reenviado para processamento (mock)' } } as AxiosResponse;
  },
};

export const MockDashboardService = {
  getDashboard: async (): Promise<{ top_5_fornecedores_pendentes: TopFornecedor[]; }> => {
    await mockDelay(500);
    const dashboardData = createMockDashboardData(mockJobsDB);
    return { top_5_fornecedores_pendentes: dashboardData.top_5_fornecedores_pendentes };
  },
};

export const MockContasService = {
  getContasAPagar: async (): Promise<Lancamento[]> => {
    await mockDelay(300);
    return mockLancamentosDB.filter(l => l.clf_tipo.nome === 'A Pagar');
  },
  getContasAReceber: async (): Promise<Lancamento[]> => {
    await mockDelay(300);
    return mockLancamentosDB.filter(l => l.clf_tipo.nome === 'A Receber');
  },
};

export const MockCalendarService = {
    getCalendarResumo: async (params: { ano: number, mes: number }): Promise<CalendarResumoResponse> => {
        await mockDelay(400);
        const saldosDiarios: { [dateString: string]: { pagar: number, receber: number } } = {};
        mockLancamentosDB
            .filter(l => {
                const dataVenc = new Date(l.data_vencimento);
                return dataVenc.getFullYear() === params.ano && dataVenc.getMonth() + 1 === params.mes;
            })
            .forEach(l => {
                const dateString = l.data_vencimento;
                if (!saldosDiarios[dateString]) saldosDiarios[dateString] = { pagar: 0, receber: 0 };
                if (l.clf_tipo.nome === 'A Pagar') {
                    saldosDiarios[dateString].pagar += l.valor;
                } else {
                    saldosDiarios[dateString].receber += l.valor;
                }
            });
        const dias: CalendarResumoDia[] = Object.entries(saldosDiarios).map(([dateString, saldos]) => ({
            data: dateString,
            valor_pagar: saldos.pagar,
            valor_receber: saldos.receber,
        }));
        return { ano: params.ano, mes: params.mes, dias };
    },
    getCalendarDia: async (data: string): Promise<CalendarDiaResponse> => {
        await mockDelay(300);
        const lancamentosDoDia = mockLancamentosDB.filter(l => l.data_vencimento === data);
        const detalhes: CalendarDiaItem[] = lancamentosDoDia.map(l => ({
            nome_fantasia: l.descricao,
            cnpj: 'N/A', // Mock data doesn't have this
            valor: l.valor,
            data: l.data_vencimento,
            tipo: l.clf_tipo.nome === 'A Pagar' ? 'PAGAR' : 'RECEBER',
        }));
        return { data, detalhes };
    },
};

// Stubs for other services
export const MockUnclassifiedCompaniesService = {
  getUnclassifiedCompanies: async (): Promise<any[]> => { await mockDelay(500); return []; },
  updateUnclassifiedCompany: async (company: any): Promise<any> => { await mockDelay(500); return company; }
};
export const MockNotaFiscalService = {
  getNotasFiscais: async (): Promise<any[]> => { await mockDelay(500); return []; },
  getClassificacoes: async (): Promise<any[]> => { await mockDelay(500); return []; },
  updateNotaFiscalClassificacao: async (notaId: string, classId: string): Promise<any> => { await mockDelay(500); return {}; },
  deleteNotaFiscal: async (notaId: string): Promise<void> => { await mockDelay(500); return; }
};
