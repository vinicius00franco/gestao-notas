import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, getContasAPagar, getContasAReceber, getDashboard, getJobStatus, uploadNota } from './api';

export const queryKeys = {
  contasAPagar: ['contasAPagar'] as const,
  contasAReceber: ['contasAReceber'] as const,
  dashboard: ['dashboard'] as const,
  jobStatus: (uuid: string) => ['jobStatus', uuid] as const,
  unclassifiedCompanies: ['unclassifiedCompanies'] as const,
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

export function useClassifyCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (company: any) => api.put(`/api/unclassified-companies/${company.id}/`, company),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.unclassifiedCompanies });
    },
  });
}

export function useJobStatus(uuid?: string) {
  return useQuery({
    queryKey: queryKeys.jobStatus(uuid || ''),
    queryFn: () => getJobStatus(uuid!),
    enabled: !!uuid,
    refetchInterval: (data: any) => {
      const status = data?.status?.codigo as string | undefined;
      // Polling rápido enquanto estiver PROCESSANDO/PENDENTE
      if (status === 'PENDENTE' || status === 'PROCESSANDO') return 2000;
      return false;
    },
  });
}
