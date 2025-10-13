import React from 'react';
import { View, Text, StyleSheet, Button, Alert } from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { NotaFiscal } from '@/types';
import withErrorBoundary from '@/components/withErrorBoundary';
import { useDeleteNotaFiscal } from '../hooks/api';

function NotaFiscalDetailScreen() {
  const route = useRoute<any>();
  const navigation = useNavigation<any>();
  const { nota } = route.params as { nota: NotaFiscal };
  const deleteNotaMutation = useDeleteNotaFiscal();

  const handleDelete = (id: string) => {
    Alert.alert(
      'Confirmar Exclusão',
      'Você tem certeza que deseja excluir esta nota fiscal?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Excluir',
          onPress: () => {
            deleteNotaMutation.mutate(id, {
              onSuccess: () => {
                navigation.goBack();
              },
            });
          },
          style: 'destructive',
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Detalhes da Nota Fiscal</Text>
      <Text>ID: {nota.id}</Text>
      <Text>Número: {nota.numero}</Text>
      <Text>Valor: {nota.valor}</Text>
      <Text>CNPJ Emitente: {nota.cnpj_emitente}</Text>
      <Text>Nome Emitente: {nota.nome_emitente}</Text>
      <Text>Classificação ID: {nota.classificacao_id}</Text>
      <Button
        title="Excluir"
        onPress={() => handleDelete(nota.id)}
        color="red"
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 16,
  },
});

export default withErrorBoundary(NotaFiscalDetailScreen);