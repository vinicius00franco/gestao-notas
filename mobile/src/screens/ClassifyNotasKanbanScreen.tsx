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
        notas: notasFiscais.filter((n: NotaFiscal) => ((n as any).classificacao_id || unclassifiedId) === c.id),
      }));
      setData(groupedData);
    }
  }, [notasFiscais, classificacoes]);

  const onDragEnd = (
    item: NotaFiscal,
    fromColumnIndex: number,
    toColumnIndex: number,
    fromIndex: number,
    toIndex: number
  ) => {
    const newData = [...data];
    const fromColumn = newData[fromColumnIndex];
    const toColumn = newData[toColumnIndex];

    // Remove from old column
    const [movedItem] = fromColumn.notas.splice(fromIndex, 1);

    // Add to new column
    toColumn.notas.splice(toIndex, 0, movedItem);

    setData(newData);

    if (fromColumn.id !== toColumn.id) {
      // Use uuid as the canonical identifier for notas when talking to the API
      updateClassificacao({ notaId: (item as any).uuid, classificacaoId: toColumn.id }, {
        onSuccess: () => refetchNotasFiscais(),
      });
    }
  };

  const renderItem = ({ item, drag, isActive }: RenderItemParams<NotaFiscal>) => {
    return (
      <TouchableOpacity onLongPress={drag}>
        <NotaFiscalCard item={item} isActive={isActive} />
      </TouchableOpacity>
    );
  };

  const [draggedItem, setDraggedItem] = useState<{item: NotaFiscal, index: number, column: number} | null>(null)

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
            renderItem={renderItem}
            keyExtractor={(item) => `nota-${(item as any).uuid}`}
            onDragBegin={(index: number) => {
              const item = column.notas[index];
              setDraggedItem({item, index, column: columnIndex});
            }}
            onDragEnd={({ to, from }) => {
                const toColumnIndex = Math.floor((scrollOffset + (SCREEN_WIDTH / 2)) / COLUMN_WIDTH)
                if (draggedItem) {
                    onDragEnd(draggedItem.item, draggedItem.column, toColumnIndex, from, to)
                }
                setDraggedItem(null)
            }}
            containerStyle={{ flex: 1 }}
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