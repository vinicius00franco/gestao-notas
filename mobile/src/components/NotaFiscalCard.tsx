import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { NotaFiscal } from '../types';

interface NotaFiscalCardProps {
  item: NotaFiscal;
  isActive?: boolean;
}

const NotaFiscalCard: React.FC<NotaFiscalCardProps> = ({ item, isActive }) => {
  return (
    <View style={[styles.card, isActive && styles.activeCard]}>
      <Text style={styles.title}>Nota Fiscal: {item.numero}</Text>
      <Text>Valor: {String(item.valor_total)}</Text>
      <Text>CNPJ: {item.parceiro?.cnpj}</Text>
      <Text>Emitente: {item.parceiro?.nome}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    padding: 16,
    marginVertical: 8,
    borderRadius: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
  },
  activeCard: {
    transform: [{ scale: 1.05 }],
    backgroundColor: '#f0f0f0',
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
});

export default NotaFiscalCard;