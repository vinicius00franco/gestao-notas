import { useNavigation } from '@react-navigation/native';
import React from 'react';
import { FlatList, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
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
        keyExtractor={(item) => (item as any).uuid.toString()}
        renderItem={({ item }) => (
          <View style={{ padding: 12, borderBottomWidth: 1, borderBottomColor: '#ccc' }}>
            <Text style={{ fontSize: 16, fontWeight: 'bold' }}>{item.nome_fantasia}</Text>
            <Text>{item.cnpj}</Text>
            <TouchableOpacity
              style={styles.button}
              onPress={() => navigation.navigate('ClassifyCompany', { company: item })}
              activeOpacity={0.7}>
              <Text style={styles.buttonText}>Classify</Text>
            </TouchableOpacity>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#007AFF',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});