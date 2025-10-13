import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getContasAPagar, getContasAReceber } from '../api/services/contasService';
import { getDashboard } from '../api/services/dashboardService';
import { deleteJob, getJobStatus, listJobs, reprocessJob, uploadNota } from '../api/services/jobService';
import { getUnclassifiedCompanies, updateUnclassifiedCompany } from '../services/unclassifiedCompaniesService';
import {
  getNotasFiscais,
  getClassificacoes,
  updateNotaFiscalClassificacao,
  deleteNotaFiscal,
} from '../services/notaFiscalService';
import { JobStatus, UnclassifiedCompany, NotaFiscal, Classificacao } from '../types';

export const queryKeys = {
  contasAPagar: ['contasAPagar'] as const,
  contasAReceber: ['contasAReceber'] as const,
  dashboard: ['dashboard'] as const,
  jobStatus: (uuid: string) => ['jobStatus', uuid] as const,
  unclassifiedCompanies: ['unclassifiedCompanies'] as const,
  notasFiscais: ['notasFiscais'] as const,
  classificacoes: ['classificacoes'] as const,
  jobs: ['jobs'] as const,
};

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

import { showMessage } from 'react-native-flash-message';
import { useNavigation } from '@react-navigation/native';

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
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.notasFiscais });
export function useListJobs() {
  return useQuery({
    queryKey: queryKeys.jobs,
    queryFn: listJobs,
  });
}

export function useReprocessJob() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: reprocessJob,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.jobs });
    },
  });
}

export function useDeleteJob() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deleteJob,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.jobs });
    },
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

export function useUnclassifiedCompanies() {
  return useQuery({
    queryKey: queryKeys.unclassifiedCompanies,
    queryFn: getUnclassifiedCompanies,
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