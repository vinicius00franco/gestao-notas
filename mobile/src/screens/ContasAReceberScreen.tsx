import React from 'react';
import { View, FlatList, Text, TouchableOpacity } from 'react-native';
import { useContasAReceber } from '../hooks/api';
import Loading from '@/components/Loading';
import { ListItem } from '@/components/ListItem';
import { formatCurrencyBRL } from '../utils/format';

export default function ContasAReceberScreen() {
  const { data, isLoading, isError, refetch } = useContasAReceber();
  if (isLoading) return <Loading />;
  if (isError) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 16 }}>
        <Text style={{ fontSize: 16, marginBottom: 16 }}>Erro ao buscar contas a receber</Text>
        <TouchableOpacity onPress={() => refetch()} style={{ padding: 12, backgroundColor: '#6200ee', borderRadius: 8 }}>
          <Text style={{ color: 'white' }}>Tentar novamente</Text>
        </TouchableOpacity>
      </View>
    );
  }

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
        ListEmptyComponent={<Text style={{ padding: 16 }}>Nenhuma conta a receber.</Text>}
      />
    </View>
  );
}
