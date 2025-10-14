import React from 'react';
import { View, Text, FlatList, Button, Alert } from 'react-native';
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
        <Button title="Tentar Novamente" onPress={() => refetch()} />
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
                <Button
                  title="Ver"
                  onPress={() => navigation.navigate('NotaFiscalDetail', { nota: item })}
                />
                <Button
                  title="Excluir"
                  onPress={() => handleDelete(item.uuid)}
                  color="red"
                />
              </View>
            }
          />
        )}
        ListEmptyComponent={<Text style={{ padding: 16 }}>Nenhuma nota fiscal encontrada.</Text>}
      />
    </View>
  );
}

export default withErrorBoundary(NotasFiscaisScreen);