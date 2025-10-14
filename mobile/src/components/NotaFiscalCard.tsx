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
    <View
      style={[
        styles.card,
        { backgroundColor: colors.surface, shadowColor: colors.shadow },
        isActive && { transform: [{ scale: 1.05 }], backgroundColor: colors.primaryContainer },
      ]}>
      <View style={styles.cardHeader}>
        <Text style={[styles.title, { color: colors.onSurface }]}>{item.nome_emitente}</Text>
      </View>
      <View style={styles.cardBody}>
        <Text style={[styles.label, { color: colors.onSurfaceVariant }]}>
          Nota Fiscal: <Text style={styles.value}>{item.numero}</Text>
        </Text>
        <Text style={[styles.label, { color: colors.onSurfaceVariant }]}>
          Valor: <Text style={[styles.value, styles.valor]}>R$ {item.valor}</Text>
        </Text>
      </View>
      <View style={[styles.footer, { borderTopColor: colors.outline }]}>
        <View style={[styles.statusIndicator, { backgroundColor: colors.primary }]} />
      </View>
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