import React from 'react';
import { View, FlatList, Text } from 'react-native';
import { useContasAReceber } from '@/services/queries';
import Loading from '@/components/Loading';
import ErrorView from '@/components/ErrorView';
import { ListItem } from '@/components/ListItem';

export default function ContasAReceberScreen() {
  const { data, isLoading, isError, refetch } = useContasAReceber();
  if (isLoading) return <Loading />;
  if (isError) return <ErrorView onRetry={refetch} />;

  return (
    <View style={{ flex: 1 }}>
      <FlatList
        data={data}
        keyExtractor={(item) => item.uuid}
        renderItem={({ item }: { item: { uuid: string; descricao: string; data_vencimento: string; valor: number } }) => (
          <ListItem
            title={item.descricao}
            subtitle={`Venc.: ${new Date(item.data_vencimento).toLocaleDateString('pt-BR')}`}
            right={<Text>R$ {item.valor.toFixed(2)}</Text>}
          />
        )}
        ListEmptyComponent={<Text style={{ padding: 16 }}>Nenhuma conta a receber.</Text>}
      />
    </View>
  );
}
