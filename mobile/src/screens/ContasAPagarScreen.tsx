import React from 'react';
import { View, FlatList, Text } from 'react-native';
import { useContasAPagar } from '../hooks/api';
import Loading from '@/components/Loading';
import { ListItem } from '@/components/ListItem';
import { formatCurrencyBRL } from '../utils/format';

export default function ContasAPagarScreen() {
  const { data, isLoading, isError, refetch } = useContasAPagar();
  if (isLoading) return <Loading />;
  if (isError) throw new Error('Erro ao buscar contas a pagar');

  return (
    <View style={{ flex: 1 }}>
      <FlatList
        data={data}
        keyExtractor={(item) => item.uuid}
        renderItem={({ item }: { item: { uuid: string; descricao: string; data_vencimento: string; valor: number | string | null } }) => (
          <ListItem
            title={item.descricao}
            subtitle={`Venc.: ${new Date(item.data_vencimento).toLocaleDateString('pt-BR')}`}
            right={<Text>{formatCurrencyBRL(item.valor)}</Text>}
          />
        )}
        ListEmptyComponent={<Text style={{ padding: 16 }}>Nenhuma conta a pagar.</Text>}
      />
    </View>
  );
}
