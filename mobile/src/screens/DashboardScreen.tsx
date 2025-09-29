import React from 'react';
import { View, Text, FlatList } from 'react-native';
import { useDashboard } from '@/services/queries';
import Loading from '@/components/Loading';
import ErrorView from '@/components/ErrorView';
import { ListItem } from '@/components/ListItem';

export default function DashboardScreen() {
  const { data, isLoading, isError, refetch } = useDashboard();
  if (isLoading) return <Loading />;
  if (isError) return <ErrorView onRetry={refetch} />;

  const fornecedores = data?.top_5_fornecedores_pendentes || [];

  return (
    <View style={{ flex: 1 }}>
      <Text style={{ fontSize: 18, fontWeight: '700', padding: 16 }}>Top 5 Fornecedores (A Pagar)</Text>
      <FlatList
        data={fornecedores}
        keyExtractor={(item) => item.cnpj}
        renderItem={({ item }: { item: { nome: string; cnpj: string; total_a_pagar: number } }) => (
          <ListItem title={item.nome} subtitle={item.cnpj} right={<Text>R$ {item.total_a_pagar.toFixed(2)}</Text>} />
        )}
        ListEmptyComponent={<Text style={{ padding: 16 }}>Sem dados.</Text>}
      />
    </View>
  );
}
