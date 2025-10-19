import { JobStatus, PaginatedResponse, TopFornecedor } from '../types';
import { mockJobsDB, createMockJob, extractMockNotaData, STATUS_OPTIONS, createMockDashboardData } from '../data/mockData';
import { AxiosResponse } from 'axios';

const mockDelay = (ms: number) => new Promise(res => setTimeout(res, ms));

/**
 * Função auxiliar que simula o ciclo de vida de processamento de um job.
 * @param jobUuid O UUID do job a ser processado.
 */
const simulateJobProcessing = (jobUuid: string) => {
  // Simula o tempo até começar o processamento
  setTimeout(() => {
    const jobIndex = mockJobsDB.findIndex(j => j.uuid === jobUuid);
    if (jobIndex === -1) return;

    // 1. Muda para PROCESSANDO
    mockJobsDB[jobIndex].status = STATUS_OPTIONS.PROCESSANDO;

    // 2. Simula o tempo de processamento do LLM
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
    }, 2000 + Math.random() * 3000); // Duração de 2 a 5 segundos

  }, 1000 + Math.random() * 2000); // Duração de 1 a 3 segundos
};

// --- Mock Service Implementation ---

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
    if (!job) {
      throw new Error('Job não encontrado');
    }
    return job;
  },

  uploadNota: async (data: { file: { uri: string, name: string, type: string }, meu_cnpj?: string }): Promise<{ message: string; job_uuid: string; }> => {
    await mockDelay(1000); // Simula o tempo de upload

    const newJob = createMockJob();
    mockJobsDB.push(newJob);

    // Inicia a simulação
    simulateJobProcessing(newJob.uuid);

    return {
      message: 'Nota enviada para processamento!',
      job_uuid: newJob.uuid,
    };
  },

  deleteJob: async (uuid: string): Promise<AxiosResponse<any, any>> => {
    await mockDelay(500);
    const index = mockJobsDB.findIndex(j => j.uuid === uuid);
    if (index > -1) {
      mockJobsDB.splice(index, 1);
    }
    return { data: { message: 'Job deletado com sucesso (mock)' } } as AxiosResponse;
  },

  reprocessJob: async (uuid: string): Promise<AxiosResponse<any, any>> => {
    await mockDelay(500);
    const jobIndex = mockJobsDB.findIndex(j => j.uuid === uuid);
    if (jobIndex > -1) {
      // Reinicia o status e limpa o erro
      mockJobsDB[jobIndex].status = STATUS_OPTIONS.PENDENTE;
      mockJobsDB[jobIndex].erro = undefined;
      mockJobsDB[jobIndex].dt_conclusao = undefined;

      // Reinicia a simulação para este job
      simulateJobProcessing(uuid);
    }
    return { data: { message: 'Job reenviado para processamento (mock)' } } as AxiosResponse;
  },
};

export const MockDashboardService = {
  getDashboard: async (): Promise<{ top_5_fornecedores_pendentes: TopFornecedor[]; }> => {
    await mockDelay(500);
    const dashboardData = createMockDashboardData(mockJobsDB);
    return {
      top_5_fornecedores_pendentes: dashboardData.top_5_fornecedores_pendentes
    };
  },
};

// ... (Restante dos serviços mockados permanecem os mesmos)
export const MockContasService = {
  getContasAPagar: async (): Promise<any[]> => { await mockDelay(500); return []; },
  getContasAReceber: async (): Promise<any[]> => { await mockDelay(500); return []; },
};

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

export const MockCalendarService = {
    getCalendarResumo: async (params: { ano: number, mes: number }): Promise<any> => { await mockDelay(500); return { ano: params.ano, mes: params.mes, dias: [] }; },
    getCalendarDia: async (data: string): Promise<any> => { await mockDelay(500); return { data: data, detalhes: { contas_a_pagar: [], contas_a_receber: [] } }; }
};
