import React from 'react';
import { View, Text, Button, Alert } from 'react-native';
import { useJobStatus } from '../hooks/api';
import Loading from '@/components/Loading';
import { useRoute } from '@react-navigation/native';
import ProgressBar from '@/components/ProgressBar';

const STATUS_PROGRESS: Record<string, number> = {
  PENDENTE: 0.25,
  PROCESSANDO: 0.75,
  CONCLUIDO: 1,
};

export default function JobStatusScreen() {
  const route = useRoute<any>();
  const uuid = route.params?.uuid as string | undefined;
  const { data, isLoading, isError, refetch } = useJobStatus(uuid);

  const jobUuid = uuid as string;

  const handleReprocess = async () => {
    try {
      await (await import('@/api/services/jobService')).reprocessJob(jobUuid);
      Alert.alert('Reprocessamento', 'Job re-enfileirado para processamento.');
      refetch();
    } catch (e: any) {
      Alert.alert('Erro', e?.message || 'Falha ao reprocessar job');
    }
  };

  const handleDelete = async () => {
    Alert.alert('Excluir job', 'Tem certeza que deseja excluir este job?', [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Excluir',
        style: 'destructive',
            onPress: async () => {
          try {
            await (await import('@/api/services/jobService')).deleteJob(jobUuid);
            Alert.alert('Sucesso', 'Job excluído');
          } catch (e: any) {
            Alert.alert('Erro', e?.message || 'Falha ao excluir job');
          }
        },
      },
    ]);
  };

  if (!uuid) return <Text style={{ padding: 16 }}>UUID não informado.</Text>;
  if (isLoading) return <Loading />;
  if (isError) throw new Error('Erro ao buscar status do job');

  const progress = data?.status?.codigo ? STATUS_PROGRESS[data.status.codigo] ?? 0 : 0;

  return (
    <View style={{ padding: 16, gap: 12 }}>
      <Text style={{ fontSize: 18, fontWeight: '700' }}>Job: {uuid}</Text>
      <View>
        <Text>Status: {data?.status?.codigo} - {data?.status?.descricao}</Text>
        <ProgressBar progress={progress} />
      </View>
      {data?.dt_conclusao && <Text>Concluído em: {new Date(data.dt_conclusao).toLocaleString('pt-BR')}</Text>}
      {data?.erro && <Text style={{ color: 'red' }}>Erro: {data.erro}</Text>}
      <View style={{ flexDirection: 'row', gap: 8 }}>
        <Button title="Reprocessar" onPress={handleReprocess} />
        <Button title="Excluir" onPress={handleDelete} color="#ff3b30" />
      </View>
    </View>
  );
}
