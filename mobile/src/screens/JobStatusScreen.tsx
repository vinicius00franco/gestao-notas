import React from 'react';
import { View, Text, Button, Alert, FlatList, StyleSheet } from 'react-native';
import { useListJobs, useReprocessJob, useDeleteJob } from '../hooks/api';
import Loading from '@/components/Loading';
import { JobStatus } from '@/types';
import { showMessage } from 'react-native-flash-message';

const JobItem = ({ item }: { item: JobStatus }) => {
  const reprocessJob = useReprocessJob();
  const deleteJob = useDeleteJob();

  const handleReprocess = () => {
    reprocessJob.mutate(item.uuid, {
      onSuccess: () => showMessage({ message: 'Job reenfileirado!', type: 'success' }),
      onError: (e: any) => showMessage({ message: e.message || 'Erro', type: 'danger' }),
    });
  };

  const handleDelete = () => {
    Alert.alert('Excluir job', `Confirmar exclusão do job ${item.uuid}?`, [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Excluir',
        style: 'destructive',
        onPress: () =>
          deleteJob.mutate(item.uuid, {
            onSuccess: () => showMessage({ message: 'Job excluído!', type: 'success' }),
            onError: (e: any) => showMessage({ message: e.message || 'Erro', type: 'danger' }),
          }),
      },
    ]);
  };

  return (
    <View style={styles.jobItem}>
      <Text style={styles.jobUuid}>{item.uuid}</Text>
      <Text>Status: {item.status.codigo}</Text>
      {item.erro && <Text style={{ color: 'red' }}>Erro: {item.erro}</Text>}
      <View style={styles.buttons}>
        <Button title="Processar" onPress={handleReprocess} disabled={reprocessJob.isPending} />
        <Button title="Excluir" onPress={handleDelete} color="#ff3b30" disabled={deleteJob.isPending} />
      </View>
    </View>
  );
};

export default function JobStatusScreen() {
  const { data: jobs, isLoading, isError, refetch } = useListJobs();

  if (isLoading) return <Loading />;
  if (isError) return <Text style={{ padding: 16 }}>Erro ao buscar jobs.</Text>;

  return (
    <FlatList
      data={jobs}
      keyExtractor={(item) => item.uuid}
      renderItem={({ item }) => <JobItem item={item} />}
      contentContainerStyle={{ padding: 16, gap: 12 }}
      ListHeaderComponent={() => <Text style={styles.title}>Fila de Processamento</Text>}
      refreshing={isLoading}
      onRefresh={refetch}
    />
  );
}

const styles = StyleSheet.create({
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  jobItem: {
    padding: 12,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    gap: 8,
  },
  jobUuid: {
    fontSize: 16,
    fontWeight: '700',
  },
  buttons: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 8,
  },
});