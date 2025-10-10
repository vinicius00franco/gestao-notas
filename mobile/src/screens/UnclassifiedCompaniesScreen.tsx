import React from 'react';
import { View, Text, FlatList, Button } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import { useNavigation } from '@react-navigation/native';

const fetchUnclassifiedCompanies = async () => {
  const { data } = await api.get('/api/unclassified-companies/');
  return data;
};

export default function UnclassifiedCompaniesScreen() {
  const navigation = useNavigation<any>();
  const { data, error, isLoading } = useQuery({
    queryKey: ['unclassifiedCompanies'],
    queryFn: fetchUnclassifiedCompanies,
  });

  if (isLoading) {
    return <Text>Loading...</Text>;
  }

  if (error) {
    return <Text>Error fetching data</Text>;
  }

  return (
    <View style={{ flex: 1, padding: 16 }}>
      <FlatList
        data={data}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={{ padding: 12, borderBottomWidth: 1, borderBottomColor: '#ccc' }}>
            <Text style={{ fontSize: 16, fontWeight: 'bold' }}>{item.nome_fantasia}</Text>
            <Text>{item.cnpj}</Text>
            <Button
              title="Classify"
              onPress={() => navigation.navigate('ClassifyCompany', { company: item })}
            />
          </View>
        )}
      />
    </View>
  );
}