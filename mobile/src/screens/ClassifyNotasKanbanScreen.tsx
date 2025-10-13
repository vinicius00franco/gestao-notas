import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, Dimensions } from 'react-native';
import DraggableFlatList, {
  RenderItemParams,
  DragEndParams,
} from 'react-native-draggable-flatlist';
import { TouchableOpacity } from 'react-native-gesture-handler';
import NotaFiscalCard from '../components/NotaFiscalCard';
import { NotaFiscal, Classificacao } from '../types';
import { useNotasFiscais, useClassificacoes, useUpdateNotaFiscalClassificacao } from '../hooks/api';

type KanbanColumn = Classificacao & { notas: NotaFiscal[] };
const COLUMN_WIDTH = 300;
const { width: SCREEN_WIDTH } = Dimensions.get('window');

const ClassifyNotasKanbanScreen = () => {
  const { data: notasFiscais, isLoading: isLoadingNotas, refetch: refetchNotasFiscais } = useNotasFiscais();
  const { data: classificacoes, isLoading: isLoadingClassificacoes } = useClassificacoes();
  const { mutate: updateClassificacao } = useUpdateNotaFiscalClassificacao();

  const [data, setData] = useState<KanbanColumn[]>([]);
  const [scrollOffset, setScrollOffset] = useState(0);
  const scrollViewRef = useRef<ScrollView>(null);

  useEffect(() => {
    if (notasFiscais && classificacoes) {
      const unclassifiedId = 'unclassified';
      const allClassificacoes = [...classificacoes, { id: unclassifiedId, nome: 'Não Classificado' }];

      const groupedData = allClassificacoes.map(c => ({
        ...c,
        notas: notasFiscais.filter((n: NotaFiscal) => (n.classificacao_id || unclassifiedId) === c.id),
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
      updateClassificacao({ notaId: item.id, classificacaoId: toColumn.id }, {
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
    <ScrollView
      horizontal
      ref={scrollViewRef}
      onScroll={(e) => setScrollOffset(e.nativeEvent.contentOffset.x)}
      scrollEventThrottle={16}
      style={{ flex: 1, backgroundColor: '#f5f5f5' }}
    >
      {data.map((column, columnIndex) => (
        <View key={column.id} style={styles.column}>
          <Text style={styles.columnHeader}>{column.nome}</Text>
          <DraggableFlatList
            data={column.notas}
            renderItem={renderItem}
            keyExtractor={(item) => `nota-${item.id}`}
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
    width: COLUMN_WIDTH,
    margin: 10,
    padding: 10,
    backgroundColor: '#e3e3e3',
    borderRadius: 8,
    height: '95%',
  },
  columnHeader: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    paddingHorizontal: 5,
  },
});

export default ClassifyNotasKanbanScreen;