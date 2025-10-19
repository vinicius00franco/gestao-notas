import React, { useMemo, useState, useRef } from 'react';
import { View, Text, Alert, FlatList, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useListJobsPendentes, useListJobsConcluidos, useListJobsErros, useReprocessJob, useDeleteJob } from '../hooks/api';
import Loading from '@/components/Loading';
import { JobStatus, PaginatedResponse } from '@/types';
import { showMessage } from 'react-native-flash-message';
import Animated, { useSharedValue, useAnimatedStyle, withTiming, runOnJS } from 'react-native-reanimated';

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
      <Text style={styles.jobUuid}>UUID: {item.uuid}</Text>
      {item.numero_nota && <Text style={styles.jobNumero}>Número: {item.numero_nota}</Text>}
      <Text>Status: {item.status.codigo}</Text>
      {item.erro && <Text style={{ color: 'red' }}>Erro: {item.erro}</Text>}
      <View style={styles.buttons}>
        <TouchableOpacity
          style={[styles.button, reprocessJob.isPending && styles.buttonDisabled]}
          onPress={handleReprocess}
          disabled={reprocessJob.isPending}
          activeOpacity={0.7}>
          <Text style={[styles.buttonText, reprocessJob.isPending && styles.buttonTextDisabled]}>
            Processar
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.button, styles.buttonDestructive, deleteJob.isPending && styles.buttonDisabled]}
          onPress={handleDelete}
          disabled={deleteJob.isPending}
          activeOpacity={0.7}>
          <Text style={[styles.buttonText, deleteJob.isPending && styles.buttonTextDisabled]}>
            Excluir
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

export default function JobStatusScreen() {
  const [activeTab, setActiveTab] = useState<number>(0); // 0: PENDENTE, 1: CONCLUIDO, 2: ERRO
  const anim = useSharedValue(0);
  const animatingRef = useRef(false);

  const pendentes = useListJobsPendentes();
  const concluidos = useListJobsConcluidos();
  const erros = useListJobsErros();

  const flipTo = (newIndex: number) => {
    if (newIndex === activeTab || animatingRef.current) return;
    animatingRef.current = true;
    // Primeiro meio-flip
    anim.value = withTiming(90, { duration: 200 }, () => {
      // Trocar conteúdo na thread JS
      runOnJS(setActiveTab)(newIndex);
      // Continuar a animação do outro lado
      anim.value = -90;
      anim.value = withTiming(0, { duration: 200 }, () => {
        animatingRef.current = false;
      });
    });
  };

  const animatedStyle = useAnimatedStyle(() => {
    return {
      transform: [{ perspective: 1000 }, { rotateY: `${anim.value}deg` }],
      backfaceVisibility: 'hidden',
    } as any;
  });

  const tabs = [
    { key: 'PENDENTE', label: 'Pendentes' },
    { key: 'CONCLUIDO', label: 'Concluídas' },
    { key: 'ERRO', label: 'Erros' },
  ];

  const pendentesTotal =
    pendentes.data?.pages.reduce(
      (acc: number, page: PaginatedResponse<JobStatus>) => acc + (page.results?.length ?? 0),
      0,
    ) ?? 0;
  const concluidosTotal =
    concluidos.data?.pages.reduce(
      (acc: number, page: PaginatedResponse<JobStatus>) => acc + (page.results?.length ?? 0),
      0,
    ) ?? 0;
  const errosTotal =
    erros.data?.pages.reduce(
      (acc: number, page: PaginatedResponse<JobStatus>) => acc + (page.results?.length ?? 0),
      0,
    ) ?? 0;

  const currentQuery = activeTab === 0 ? pendentes : activeTab === 1 ? concluidos : erros;
  const currentList = currentQuery.data?.pages.flatMap((page: PaginatedResponse<JobStatus>) => page.results) || [];

  if (currentQuery.isLoading && !currentQuery.isFetchingNextPage) return <Loading />;
  if (currentQuery.isError) return <Text style={{ padding: 16 }}>Erro ao buscar notas processadas.</Text>;

  return (
    <View style={{ flex: 1 }}>
      <View style={styles.header}>
        <Text style={styles.title}>Notas processadas</Text>
      </View>

      <View style={styles.tabBar}>
        {tabs.map((t, idx) => (
          <TouchableOpacity key={t.key} style={styles.tabButton} onPress={() => flipTo(idx)}>
            <Text style={[styles.tabLabel, activeTab === idx && styles.tabLabelActive]}>
              {t.label} ({idx === 0 ? pendentesTotal : idx === 1 ? concluidosTotal : errosTotal})
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <Animated.View style={[styles.animatedContainer, animatedStyle]}>
        <FlatList
          data={currentList}
          keyExtractor={(item: JobStatus) => item.uuid}
          renderItem={({ item }: { item: JobStatus }) => <JobItem item={item} />}
          contentContainerStyle={{ padding: 16, gap: 12 }}
          refreshing={currentQuery.isLoading}
          onRefresh={currentQuery.refetch}
          onEndReached={() => {
            if (currentQuery.hasNextPage && !currentQuery.isFetchingNextPage) {
              currentQuery.fetchNextPage();
            }
          }}
          onEndReachedThreshold={0.5}
          ListFooterComponent={() => {
            if (currentQuery.isFetchingNextPage) {
              return (
                <View style={{ padding: 20 }}>
                  <ActivityIndicator size="small" />
                </View>
              );
            }
            return null;
          }}
          ListEmptyComponent={() => (
            <View style={{ padding: 24 }}>
              <Text>Nenhuma nota nesta categoria.</Text>
            </View>
          )}
        />
      </Animated.View>
    </View>
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
  jobNumero: {
    fontSize: 14,
    color: '#666',
  },
  buttons: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 8,
  },
  button: {
    backgroundColor: '#007AFF',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  buttonDestructive: {
    backgroundColor: '#ff3b30',
  },
  buttonDisabled: {
    backgroundColor: '#A0A0A0',
    opacity: 0.6,
  },
  buttonTextDisabled: {
    color: '#E0E0E0',
  },
  header: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  tabBar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 12,
    backgroundColor: '#fafafa',
  },
  tabButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  tabLabel: {
    fontSize: 16,
    color: '#333',
  },
  tabLabelActive: {
    fontWeight: '700',
    color: '#111',
  },
  animatedContainer: {
    flex: 1,
    backfaceVisibility: 'hidden',
  },
});