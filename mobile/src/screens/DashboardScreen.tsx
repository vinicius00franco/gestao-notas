import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, Button } from 'react-native';
import { useDashboard } from '@/services/queries';
import LoadingIndicator from '@/components/LoadingIndicator';
import ErrorView from '@/components/ErrorView';
import Loading from '@/components/Loading';
import { ListItem } from '@/components/ListItem';
import { useNavigation } from '@react-navigation/native';

export default function DashboardScreen() {
  const { data, isError, refetch } = useDashboard();
  const navigation = useNavigation<any>();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 2000); // Simulate loading for 2 seconds

    return () => clearTimeout(timer);
  }, []);


  if (isLoading) return <LoadingIndicator fullscreen message="Carregando dashboard..." />;
  if (isError) return <ErrorView onRetry={refetch} />;

  const fornecedores = data?.top_5_fornecedores_pendentes || [];

  return (
    <View style={{ flex: 1 }}>
      <Button
        title="Unclassified Companies"
        onPress={() => navigation.navigate('UnclassifiedCompanies')}
      />
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
