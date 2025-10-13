import React from 'react';
import { View, Text, FlatList, Button, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useNotasFiscais, useDeleteNotaFiscal } from '../hooks/api';
import Loading from '@/components/Loading';
import { ListItem } from '@/components/ListItem';
import { NotaFiscal } from '@/types';
import withErrorBoundary from '@/components/withErrorBoundary';

function NotasFiscaisScreen() {
  const { data: notas, isLoading, isError } = useNotasFiscais();
  const deleteNotaMutation = useDeleteNotaFiscal();
  const navigation = useNavigation<any>();

  const handleDelete = (id: string) => {
    Alert.alert(
      'Confirmar Exclusão',
      'Você tem certeza que deseja excluir esta nota fiscal?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Excluir',
          onPress: () => deleteNotaMutation.mutate(id),
          style: 'destructive',
        },
      ]
    );
  };

  if (isLoading) return <Loading />;
  if (isError) throw new Error('Erro ao buscar notas fiscais');

  return (
    <View style={{ flex: 1 }}>
      <FlatList
        data={notas}
        keyExtractor={(item) => item.id}
        renderItem={({ item }: { item: NotaFiscal }) => (
          <ListItem
            title={item.numero}
            subtitle={item.nome_emitente}
            right={
              <View style={{ flexDirection: 'row' }}>
                <Button
                  title="Ver"
                  onPress={() => navigation.navigate('NotaFiscalDetail', { nota: item })}
                />
                <Button
                  title="Excluir"
                  onPress={() => handleDelete(item.id)}
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