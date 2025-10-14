import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { getContasAPagar, getContasAReceber } from '../api/services/contasService';
import { getDashboard } from '../api/services/dashboardService';
import { getCalendarResumo, getCalendarDia, CalendarResumoResponse, CalendarDiaResponse } from '../api/services/calendarService';
import {
  listJobs,
  listJobsPendentes,
  listJobsConcluidos,
  listJobsErros,
  deleteJob,
  getJobStatus,
  reprocessJob,
  uploadNota,
} from '../api/services/jobService';
import {
  getUnclassifiedCompanies,
  updateUnclassifiedCompany,
} from '../services/unclassifiedCompaniesService';
import {
  getNotasFiscais,
  getClassificacoes,
  updateNotaFiscalClassificacao,
  deleteNotaFiscal,
} from '../services/notaFiscalService';
import { JobStatus, PaginatedResponse, UnclassifiedCompany, NotaFiscal, Classificacao } from '../types';
import { showMessage } from 'react-native-flash-message';
import { useNavigation } from '@react-navigation/native';

export const queryKeys = {
  contasAPagar: ['contasAPagar'] as const,
  contasAReceber: ['contasAReceber'] as const,
  dashboard: ['dashboard'] as const,
  calendarResumo: (ano: number, mes: number) => ['calendarResumo', ano, mes] as const,
  calendarDia: (data: string) => ['calendarDia', data] as const,
  jobStatus: (uuid: string) => ['jobStatus', uuid] as const,
  unclassifiedCompanies: ['unclassifiedCompanies'] as const,
  notasFiscais: ['notasFiscais'] as const,
  classificacoes: ['classificacoes'] as const,
  jobs: ['jobs'] as const,
  jobsPendentes: ['jobsPendentes'] as const,
  jobsConcluidos: ['jobsConcluidos'] as const,
  jobsErros: ['jobsErros'] as const,
};

// -------------------
// Query Hooks
// -------------------

export function useContasAPagar() {
  return useQuery({
    queryKey: queryKeys.contasAPagar,
    queryFn: getContasAPagar,
    staleTime: 30_000,
  });
}

export function useContasAReceber() {
  return useQuery({
    queryKey: queryKeys.contasAReceber,
    queryFn: getContasAReceber,
    staleTime: 30_000,
  });
}

export function useDashboard() {
  return useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: getDashboard,
    staleTime: 60_000,
  });
}

export function useListJobs() {
  return useQuery({
    queryKey: queryKeys.jobs,
    queryFn: listJobs,
  });
}

export function useNotasFiscais() {
  return useQuery({
    queryKey: queryKeys.notasFiscais,
    queryFn: getNotasFiscais,
  });
}

export function useClassificacoes() {
  return useQuery({
    queryKey: queryKeys.classificacoes,
    queryFn: getClassificacoes,
  });
}

export function useUnclassifiedCompanies() {
  return useQuery({
    queryKey: queryKeys.unclassifiedCompanies,
    queryFn: getUnclassifiedCompanies,
  });
}

export function useJobStatus(uuid?: string) {
  return useQuery({
    queryKey: queryKeys.jobStatus(uuid || ''),
    queryFn: () => getJobStatus(uuid!),
    enabled: !!uuid,
    refetchInterval: (query) => {
      const status = query.state.data?.status?.codigo;
      // Polling rápido enquanto estiver PROCESSANDO/PENDENTE
      if (status === 'PENDENTE' || status === 'PROCESSANDO') return 2000;
      return false;
    },
  });
}

// -------------------
// Infinite Query Hooks
// -------------------

const getNextPageParam = (lastPage: PaginatedResponse<JobStatus>) => {
  if (lastPage.next) {
    const url = new URL(lastPage.next);
    return parseInt(url.searchParams.get('page') || '1');
  }
  return undefined;
};

export function useListJobsPendentes() {
  return useInfiniteQuery({
    queryKey: queryKeys.jobsPendentes,
    queryFn: ({ pageParam = 1 }) => listJobsPendentes({ page: pageParam }),
    initialPageParam: 1,
    getNextPageParam,
  });
}

export function useListJobsConcluidos() {
  return useInfiniteQuery({
    queryKey: queryKeys.jobsConcluidos,
    queryFn: ({ pageParam = 1 }) => listJobsConcluidos({ page: pageParam }),
    initialPageParam: 1,
    getNextPageParam,
  });
}

export function useListJobsErros() {
  return useInfiniteQuery({
    queryKey: queryKeys.jobsErros,
    queryFn: ({ pageParam = 1 }) => listJobsErros({ page: pageParam }),
    initialPageParam: 1,
    getNextPageParam,
  });
}

// -------------------
// Mutation Hooks
// -------------------

export function useUploadNota() {
  const qc = useQueryClient();
  const nav = useNavigation<any>();
  return useMutation({
    mutationFn: uploadNota,
    onSuccess: (out) => {
      showMessage({
        message: out.message,
        type: 'success',
      });
      nav.navigate('JobStatus', { uuid: out.job_uuid });
    },
    onError: (error: any) => {
      showMessage({
        message: error.response?.data?.detail || 'An error occurred',
        type: 'danger',
      });
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: queryKeys.contasAPagar });
      qc.invalidateQueries({ queryKey: queryKeys.contasAReceber });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard });
    },
  });
}

export function useDeleteNotaFiscal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (notaId: string) => deleteNotaFiscal(notaId),
    onSuccess: (data) => {
      showMessage({
        message: data.message || 'Nota fiscal excluída com sucesso!',
        type: 'success',
      });
      qc.invalidateQueries({ queryKey: queryKeys.notasFiscais });
    },
    onError: (error: any) => {
      showMessage({
        message: error.response?.data?.error || 'Erro ao excluir nota fiscal',
        type: 'danger',
      });
    },
  });
}

export function useUpdateNotaFiscalClassificacao() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ notaId, classificacaoId }: { notaId: string; classificacaoId: string }) =>
      updateNotaFiscalClassificacao(notaId, classificacaoId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.notasFiscais });
    },
  });
}

export function useReprocessJob() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: reprocessJob,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.jobs });
      qc.invalidateQueries({ queryKey: queryKeys.jobsPendentes });
      qc.invalidateQueries({ queryKey: queryKeys.jobsErros });
    },
  });
}

export function useDeleteJob() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deleteJob,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.jobs });
      qc.invalidateQueries({ queryKey: queryKeys.jobsPendentes });
      qc.invalidateQueries({ queryKey: queryKeys.jobsConcluidos });
      qc.invalidateQueries({ queryKey: queryKeys.jobsErros });
    },
  });
}

export function useClassifyCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (company: UnclassifiedCompany) => updateUnclassifiedCompany(company),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.unclassifiedCompanies });
    },
  });
}

// -------------------
// Calendar Hooks
// -------------------

export function useCalendarResumo(ano: number, mes: number) {
  return useQuery<CalendarResumoResponse>({
    queryKey: queryKeys.calendarResumo(ano, mes),
    queryFn: () => getCalendarResumo({ ano, mes }),
  });
}

export function useCalendarDia(data: string) {
  return useQuery<CalendarDiaResponse>({
    queryKey: queryKeys.calendarDia(data),
    queryFn: () => getCalendarDia(data),
    enabled: !!data,
  });
}