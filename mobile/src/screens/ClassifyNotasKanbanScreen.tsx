import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, FlatList } from 'react-native';
import NotaFiscalCard from '../components/NotaFiscalCard';
import { NotaFiscal, Classificacao } from '../types';
import { useNotasFiscais, useClassificacoes, useUpdateNotaFiscalClassificacao } from '../hooks/api';
import { useTheme } from '@/theme/ThemeProvider';

type KanbanColumn = Classificacao & { notas: NotaFiscal[] };

const ClassifyNotasKanbanScreen = () => {
  const { colors } = useTheme();
  const { data: notasFiscais, isLoading: isLoadingNotas, refetch: refetchNotasFiscais } = useNotasFiscais();
  const { data: classificacoes, isLoading: isLoadingClassificacoes } = useClassificacoes();
  const { mutate: updateClassificacao } = useUpdateNotaFiscalClassificacao();

  const [data, setData] = useState<KanbanColumn[]>([]);

  useEffect(() => {
    if (notasFiscais && classificacoes) {
      const unclassifiedId = 'unclassified';
      const allClassificacoes = [
        { id: unclassifiedId, nome: 'Não Classificado' },
        ...classificacoes,
      ];

      const groupedData = allClassificacoes.map(c => ({
        ...c,
        notas: notasFiscais.filter((n: NotaFiscal) => (n.classificacao_id || unclassifiedId) === c.id),
      }));
      setData(groupedData);
    }
  }, [notasFiscais, classificacoes]);

  if (isLoadingNotas || isLoadingClassificacoes) {
    return <ActivityIndicator size="large" style={{ flex: 1, justifyContent: 'center' }} />;
  }

  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.background }}>
      {data.map(column => (
        <View key={column.id} style={styles.column}>
          <Text style={[styles.columnHeader, { color: colors.onBackground }]}>{column.nome}</Text>
          <FlatList
            data={column.notas}
            renderItem={({ item }) => <NotaFiscalCard item={item} />}
            keyExtractor={item => `nota-${item.id}`}
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={{ paddingHorizontal: 10 }}
          />
        </View>
      ))}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  column: {
    marginVertical: 10,
    paddingVertical: 10,
  },
  columnHeader: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
    paddingHorizontal: 20,
  },
});

export default ClassifyNotasKanbanScreen;