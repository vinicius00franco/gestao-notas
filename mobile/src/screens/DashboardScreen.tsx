import React from 'react';
import { View, Text, FlatList, Button } from 'react-native';
import { useDashboard } from '../hooks/api';
import Loading from '@/components/Loading';
import { ListItem } from '@/components/ListItem';
import { formatCurrencyBRL } from '../utils/format';
import { useNavigation } from '@react-navigation/native';

export default function DashboardScreen() {
  const { data, isLoading, isError, refetch } = useDashboard();
  const navigation = useNavigation<any>();

  if (isLoading) return <Loading />;
  if (isError) throw new Error('Erro ao buscar dados do dashboard');

  const fornecedores = data?.top_5_fornecedores_pendentes || [];

  return (
    <View style={{ flex: 1 }}>
      <Button
        title="Unclassified Companies"
        onPress={() => navigation.navigate('UnclassifiedCompanies')}
      />
      <Button
        title="Ver/Excluir Notas Fiscais"
        onPress={() => navigation.navigate('NotasFiscais')}
      />
      <Text style={{ fontSize: 18, fontWeight: '700', padding: 16 }}>Top 5 Fornecedores (A Pagar)</Text>
      <FlatList
        data={fornecedores}
        keyExtractor={(item) => item.cnpj}
        renderItem={({ item }: { item: { nome: string; cnpj: string; total_a_pagar: number | string | null } }) => (
          <ListItem title={item.nome} subtitle={item.cnpj} right={<Text>{formatCurrencyBRL(item.total_a_pagar)}</Text>} />
        )}
        ListEmptyComponent={<Text style={{ padding: 16 }}>Sem dados.</Text>}
      />
    </View>
  );
}
