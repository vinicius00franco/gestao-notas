import React from 'react';
import { View, Text, StyleSheet, Alert, TouchableOpacity } from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { NotaFiscal } from '@/types';
import withErrorBoundary from '@/components/withErrorBoundary';
import { useDeleteNotaFiscal } from '../hooks/api';

function NotaFiscalDetailScreen() {
  const route = useRoute<any>();
  const navigation = useNavigation<any>();
  const { nota } = route.params as { nota: NotaFiscal };
  const deleteNotaMutation = useDeleteNotaFiscal();

  const handleDelete = (uuid: string) => {
    Alert.alert(
      'Confirmar Exclusão',
      'Você tem certeza que deseja excluir esta nota fiscal?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Excluir',
          onPress: () => {
            deleteNotaMutation.mutate(uuid, {
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
      <Text>UUID: {nota.uuid}</Text>
      <Text>Número: {nota.numero}</Text>
      <Text>Valor: {String(nota.valor_total)}</Text>
      <Text>CNPJ Emitente: {nota.parceiro?.cnpj}</Text>
      <Text>Nome Emitente: {nota.parceiro?.nome}</Text>
      <TouchableOpacity
        style={styles.button}
        onPress={() => handleDelete(nota.uuid)}
        activeOpacity={0.7}>
        <Text style={styles.buttonText}>Excluir</Text>
      </TouchableOpacity>
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
  button: {
    backgroundColor: '#ff3b30',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 16,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default withErrorBoundary(NotaFiscalDetailScreen);