import React from 'react';
import { View, Text, FlatList, Alert, StyleSheet, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useNotasFiscais, useDeleteNotaFiscal } from '../hooks/api';
import Loading from '@/components/Loading';
import { ListItem } from '@/components/ListItem';
import { NotaFiscal } from '@/types';
import { formatCurrencyBRL } from '../utils/format';
import withErrorBoundary from '@/components/withErrorBoundary';

function NotasFiscaisScreen() {
  const { data: notas, isLoading, isError, error, refetch } = useNotasFiscais();
  const deleteNotaMutation = useDeleteNotaFiscal();
  const navigation = useNavigation<any>();

  const handleDelete = (uuid: string) => {
    Alert.alert(
      'Confirmar Exclusão',
      'Você tem certeza que deseja excluir esta nota fiscal?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Excluir',
          onPress: () => deleteNotaMutation.mutate(uuid),
          style: 'destructive',
        },
      ]
    );
  };

  if (isLoading) return <Loading />;
  if (isError) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 16 }}>
        <Text style={{ fontSize: 18, color: 'red', marginBottom: 16 }}>Erro ao buscar notas fiscais</Text>
        <Text style={{ fontSize: 14, color: 'gray' }}>
          {error?.message || 'Erro desconhecido'}
        </Text>
        <TouchableOpacity style={styles.button} onPress={() => refetch()} activeOpacity={0.7}>
          <Text style={styles.buttonText}>Tentar Novamente</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={{ flex: 1 }}>
      <FlatList
        data={notas}
        keyExtractor={(item) => item.uuid}
        renderItem={({ item }: { item: NotaFiscal }) => (
          <ListItem
            title={item.numero}
            subtitle={`${item.parceiro?.nome ?? ''} • ${item.parceiro?.cnpj ?? ''}`}
            right={
              <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                <Text style={{ marginRight: 12 }}>{formatCurrencyBRL(item.valor_total)}</Text>
                <TouchableOpacity
                  style={styles.button}
                  onPress={() => navigation.navigate('NotaFiscalDetail', { nota: item })}
                  activeOpacity={0.7}>
                  <Text style={styles.buttonText}>Ver</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.button, styles.buttonDestructive]}
                  onPress={() => handleDelete(item.uuid)}
                  activeOpacity={0.7}>
                  <Text style={styles.buttonText}>Excluir</Text>
                </TouchableOpacity>
              </View>
            }
          />
        )}
        ListEmptyComponent={<Text style={{ padding: 16 }}>Nenhuma nota fiscal encontrada.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#007AFF',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 8,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  buttonDestructive: {
    backgroundColor: '#ff3b30',
  },
});

export default withErrorBoundary(NotasFiscaisScreen);