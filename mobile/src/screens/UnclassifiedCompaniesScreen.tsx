import { useNavigation } from '@react-navigation/native';
import React from 'react';
import { Button, FlatList, Text, View } from 'react-native';
import { useUnclassifiedCompanies } from '../hooks/api';
import { UnclassifiedCompany } from '../types';

export default function UnclassifiedCompaniesScreen() {
  const navigation = useNavigation<any>();
  const { data, error, isLoading } = useUnclassifiedCompanies();

  if (isLoading) {
    return <Text>Loading...</Text>;
  }

  if (error) {
    return <Text>Error fetching data</Text>;
  }

  return (
    <View style={{ flex: 1, padding: 16 }}>
      <FlatList
        data={data as UnclassifiedCompany[]}
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