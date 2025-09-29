import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getContasAPagar, getContasAReceber, getDashboard, getJobStatus, uploadNota } from './api';

export const queryKeys = {
  contasAPagar: ['contasAPagar'] as const,
  contasAReceber: ['contasAReceber'] as const,
  dashboard: ['dashboard'] as const,
  jobStatus: (uuid: string) => ['jobStatus', uuid] as const,
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

export function useUploadNota() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: uploadNota,
    onSuccess: () => {
      // Após processar, revalidar listas e dashboard
      qc.invalidateQueries({ queryKey: queryKeys.contasAPagar });
      qc.invalidateQueries({ queryKey: queryKeys.contasAReceber });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard });
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
