import Constants from 'expo-constants';
import * as realJobService from '../api/services/jobService';
import * as realDashboardService from '../api/services/dashboardService';
import * as realContasService from '../api/services/contasService';
import * as realUnclassifiedCompaniesService from '../services/unclassifiedCompaniesService';
import * as realNotaFiscalService from '../services/notaFiscalService';
import * as realCalendarService from '../api/services/calendarService';

import jobs from '../mocks/jobs.json';
import jobDetails from '../mocks/jobDetails.json';
import dashboard from '../mocks/dashboard.json';
import contas from '../mocks/contas.json';
import uploadResponse from '../mocks/uploadResponse.json';
import { JobStatus, PaginatedResponse, Lancamento, TopFornecedor, UnclassifiedCompany, NotaFiscal, Classificacao } from '../types';
import { CalendarDiaResponse, CalendarResumoResponse } from '../api/services/calendarService';
import { AxiosResponse } from 'axios';

const appMode = Constants.expoConfig?.extra?.appMode || 'real';

const mockDelay = (ms: number) => new Promise(res => setTimeout(res, ms));

const mockJobService = {
  listJobs: async (): Promise<JobStatus[]> => {
    await mockDelay(500);
    return jobs as JobStatus[];
  },
  listJobsPendentes: async (params: { page: number }): Promise<PaginatedResponse<JobStatus>> => {
    await mockDelay(500);
    const pendentes = jobs.filter(j => j.status.codigo === 'PENDENTE');
    return { results: pendentes, next: null, previous: null, count: pendentes.length } as PaginatedResponse<JobStatus>;
  },
  listJobsConcluidos: async (params: { page: number }): Promise<PaginatedResponse<JobStatus>> => {
    await mockDelay(500);
    const concluidos = jobs.filter(j => j.status.codigo === 'CONCLUIDO');
    return { results: concluidos, next: null, previous: null, count: concluidos.length } as PaginatedResponse<JobStatus>;
  },
  listJobsErros: async (params: { page: number }): Promise<PaginatedResponse<JobStatus>> => {
    await mockDelay(500);
    const erros = jobs.filter(j => j.status.codigo === 'ERRO');
    return { results: erros, next: null, previous: null, count: erros.length } as PaginatedResponse<JobStatus>;
  },
  getJobStatus: async (uuid: string): Promise<JobStatus> => {
    await mockDelay(500);
    const details = { ...jobDetails };
    const random = Math.random();
    if (details.status.codigo === 'PROCESSANDO') {
      if (random < 0.3) {
        details.status = { codigo: 'CONCLUIDO', descricao: 'Processamento concluído com sucesso.' };
      } else if (random < 0.4) {
        details.status = { codigo: 'ERRO', descricao: 'Falha na simulação.' };
      }
    }
    return details as JobStatus;
  },
  uploadNota: async (data: { file: { uri: string, name: string, type: string }, meu_cnpj?: string }): Promise<{ message: string; job_uuid: string; }> => {
    await mockDelay(1000);
    console.log('[Mock] Uploading nota:', data.file.name);
    return uploadResponse;
  },
  deleteJob: async (uuid: string): Promise<AxiosResponse<any, any>> => {
    await mockDelay(500);
    console.log(`[Mock] Deleting job ${uuid}`);
    return { data: { message: 'Job deletado com sucesso (mock)' } } as AxiosResponse<any, any>;
  },
  reprocessJob: async (uuid: string): Promise<AxiosResponse<any, any>> => {
    await mockDelay(500);
    console.log(`[Mock] Reprocessing job ${uuid}`);
    return { data: { message: 'Job reenviado para processamento (mock)' } } as AxiosResponse<any, any>;
  },
};

const mockDashboardService = {
  getDashboard: async (): Promise<{ top_5_fornecedores_pendentes: TopFornecedor[]; }> => {
    await mockDelay(500);
    return dashboard as { top_5_fornecedores_pendentes: TopFornecedor[] };
  },
};

const mockContasService = {
  getContasAPagar: async (): Promise<Lancamento[]> => {
    await mockDelay(500);
    return contas.aPagar as Lancamento[];
  },
  getContasAReceber: async (): Promise<Lancamento[]> => {
    await mockDelay(500);
    return contas.aReceber as Lancamento[];
  },
};

const mockUnclassifiedCompaniesService = {
    getUnclassifiedCompanies: async (): Promise<UnclassifiedCompany[]> => { await mockDelay(500); return []; },
    updateUnclassifiedCompany: async (company: UnclassifiedCompany): Promise<UnclassifiedCompany> => { await mockDelay(500); return company; }
};

const mockNotaFiscalService = {
    getNotasFiscais: async (): Promise<NotaFiscal[]> => { await mockDelay(500); return []; },
    getClassificacoes: async (): Promise<Classificacao[]> => { await mockDelay(500); return []; },
    updateNotaFiscalClassificacao: async (notaId: string, classificacaoId: string): Promise<NotaFiscal> => { await mockDelay(500); return {} as NotaFiscal; },
    deleteNotaFiscal: async (notaId: string): Promise<void> => { await mockDelay(500); return; }
};

const mockCalendarService = {
    getCalendarResumo: async (params: { ano: number, mes: number }): Promise<CalendarResumoResponse> => { await mockDelay(500); return { ano: params.ano, mes: params.mes, dias: [] }; },
    getCalendarDia: async (data: string): Promise<CalendarDiaResponse> => { await mockDelay(500); return { data: data, detalhes: { contas_a_pagar: [], contas_a_receber: [] } } as unknown as CalendarDiaResponse; }
};


export const JobService = appMode === 'mock' ? mockJobService : realJobService;
export const DashboardService = appMode === 'mock' ? mockDashboardService : realDashboardService;
export const ContasService = appMode === 'mock' ? mockContasService : realContasService;
export const UnclassifiedCompaniesService = appMode === 'mock' ? mockUnclassifiedCompaniesService : realUnclassifiedCompaniesService;
export const NotaFiscalService = appMode === 'mock' ? mockNotaFiscalService : realNotaFiscalService;
export const CalendarService = appMode === 'mock' ? mockCalendarService : realCalendarService;