import { useNavigation, useRoute } from '@react-navigation/native';
import { Picker } from '@react-native-picker/picker';
import React, { useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';
import { useClassifyCompany } from '../hooks/api';
import { UnclassifiedCompany } from '../types';

export default function ClassifyCompanyScreen() {
  const route = useRoute<any>();
  const navigation = useNavigation<any>();
  const { company } = route.params;

  const [formData, setFormData] = useState<UnclassifiedCompany>({
    ...company,
    classification: 'fornecedor', // default classification
  });

  const { mutate: classifyCompany, isPending } = useClassifyCompany();

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = () => {
    classifyCompany(formData, {
      onSuccess: () => {
        navigation.goBack();
        Alert.alert('Success', 'Company classified successfully.');
      },
      onError: () => {
        Alert.alert('Error', 'Failed to classify company.');
      },
    });
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Classify Company</Text>
      <TextInput
        style={styles.input}
        value={formData.nome_fantasia}
        onChangeText={(value) => handleInputChange('nome_fantasia', value)}
        placeholder="Nome Fantasia"
      />
      <TextInput
        style={styles.input}
        value={formData.razao_social}
        onChangeText={(value) => handleInputChange('razao_social', value)}
        placeholder="Razão Social"
      />
      <TextInput
        style={styles.input}
        value={formData.cnpj}
        editable={false}
        placeholder="CNPJ"
      />
      <TextInput
        style={styles.input}
        value={formData.logradouro}
        onChangeText={(value) => handleInputChange('logradouro', value)}
        placeholder="Logradouro"
      />
      <TextInput
        style={styles.input}
        value={formData.numero}
        onChangeText={(value) => handleInputChange('numero', value)}
        placeholder="Número"
      />
      <TextInput
        style={styles.input}
        value={formData.bairro}
        onChangeText={(value) => handleInputChange('bairro', value)}
        placeholder="Bairro"
      />
      <TextInput
        style={styles.input}
        value={formData.cidade}
        onChangeText={(value) => handleInputChange('cidade', value)}
        placeholder="Cidade"
      />
      <TextInput
        style={styles.input}
        value={formData.uf}
        onChangeText={(value) => handleInputChange('uf', value)}
        placeholder="UF"
      />
      <TextInput
        style={styles.input}
        value={formData.cep}
        onChangeText={(value) => handleInputChange('cep', value)}
        placeholder="CEP"
      />
      <TextInput
        style={styles.input}
        value={formData.telefone}
        onChangeText={(value) => handleInputChange('telefone', value)}
        placeholder="Telefone"
      />
      <TextInput
        style={styles.input}
        value={formData.email}
        onChangeText={(value) => handleInputChange('email', value)}
        placeholder="Email"
      />
      <Picker
        selectedValue={formData.classification}
        onValueChange={(itemValue) => handleInputChange('classification', itemValue)}
        style={styles.picker}
      >
        <Picker.Item label="Fornecedor" value="fornecedor" />
        <Picker.Item label="Cliente" value="cliente" />
        <Picker.Item label="Outra Empresa" value="outra_empresa" />
        <Picker.Item label="Outro" value="outro" />
      </Picker>
      <TouchableOpacity
        style={[styles.button, isPending && styles.buttonDisabled]}
        onPress={handleSubmit}
        disabled={isPending}
        activeOpacity={0.7}>
        <Text style={[styles.buttonText, isPending && styles.buttonTextDisabled]}>Save</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    padding: 8,
    borderRadius: 6,
    marginBottom: 12,
  },
  picker: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 6,
    marginBottom: 12,
  },
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
  buttonDisabled: {
    backgroundColor: '#A0A0A0',
    opacity: 0.6,
  },
  buttonTextDisabled: {
    color: '#E0E0E0',
  },
});