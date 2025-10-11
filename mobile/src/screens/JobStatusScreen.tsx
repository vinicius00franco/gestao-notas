import React from 'react';
import { View, Text } from 'react-native';
import { useJobStatus } from '@/services/queries';
import Loading from '@/components/Loading';
import { useRoute } from '@react-navigation/native';

export default function JobStatusScreen() {
  const route = useRoute<any>();
  const uuid = route.params?.uuid as string | undefined;
  const { data, isLoading, isError, refetch } = useJobStatus(uuid);
  if (!uuid) return <Text style={{ padding: 16 }}>UUID não informado.</Text>;
  if (isLoading) return <Loading />;
  if (isError) throw new Error('Erro ao buscar status do job');

  return (
    <View style={{ padding: 16 }}>
      <Text style={{ fontSize: 18, fontWeight: '700' }}>Job: {uuid}</Text>
      <Text style={{ marginTop: 8 }}>Status: {data?.status?.codigo} - {data?.status?.descricao}</Text>
      {data?.dt_conclusao && <Text>Concluído em: {new Date(data.dt_conclusao).toLocaleString('pt-BR')}</Text>}
      {data?.erro && <Text style={{ color: 'red' }}>Erro: {data.erro}</Text>}
    </View>
  );
}
