import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { NotaFiscal } from '../types';
import { useTheme } from '@/theme/ThemeProvider';

interface NotaFiscalCardProps {
  item: NotaFiscal;
  isActive?: boolean;
}

const NotaFiscalCard: React.FC<NotaFiscalCardProps> = ({ item, isActive }) => {
  const { colors } = useTheme();

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
    borderRadius: 12,
    marginVertical: 8,
    marginHorizontal: 4,
    elevation: 3,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    overflow: 'hidden',
  },
  cardHeader: {
    padding: 16,
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  cardBody: {
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  label: {
    fontSize: 14,
    marginBottom: 4,
  },
  value: {
    fontWeight: '600',
  },
  valor: {
    fontWeight: 'bold',
    fontSize: 16,
  },
  footer: {
    borderTopWidth: 1,
    padding: 12,
    alignItems: 'flex-start',
  },
  statusIndicator: {
    width: '40%',
    height: 6,
    borderRadius: 3,
  },
});

export default NotaFiscalCard;