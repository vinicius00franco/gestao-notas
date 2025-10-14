
import React, { useState } from 'react';
import { View, Button, SafeAreaView, ScrollView, StyleSheet, Text, ActivityIndicator, TouchableOpacity } from 'react-native';

import React, { useMemo } from 'react';
import { SafeAreaView } from 'react-native-safe-area-context';

import { useNavigation } from '@react-navigation/native';
import Card from '@/components/Card';
import LineChartCard from '@/components/charts/LineChartCard';
import BarChartCard from '@/components/charts/BarChartCard';
import DonutChartCard from '@/components/charts/DonutChartCard';
import { useTheme } from '@/theme/ThemeProvider';
import { useDashboardData, Period } from '@/hooks/useDashboardData';

const PERIODS: { label: string; value: Period }[] = [
  { label: 'Últimos 7 dias', value: 'last_7_days' },
  { label: 'Último mês', value: 'last_month' },
  { label: 'Últimos 3 meses', value: 'last_3_months' },
  { label: 'Último ano', value: 'last_year' },
];

export default function DashboardScreen() {
  const navigation = useNavigation<any>();
  const theme = useTheme();
  const [period, setPeriod] = useState<Period>('last_month');
  const { data, isLoading, isError } = useDashboardData(period);

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: theme.colors.background },
    header: { paddingHorizontal: 16, paddingTop: 4, paddingBottom: 8 },
    title: { ...theme.typography.h2 },
    subtitle: { ...theme.typography.caption },
    actions: { flexDirection: 'row', gap: 8, paddingHorizontal: 8, paddingBottom: 8 },
    periodFilterContainer: {
      flexDirection: 'row',
      justifyContent: 'space-around',
      paddingVertical: 8,
      backgroundColor: theme.colors.surface,
    },
    periodButton: {
      paddingHorizontal: 12,
      paddingVertical: 8,
      borderRadius: 16,
    },
    periodButtonActive: {
      backgroundColor: theme.colors.primary,
    },
    periodButtonText: {
      ...theme.typography.body2,
      color: theme.colors.onSurface,
    },
    periodButtonTextActive: {
      color: theme.colors.onPrimary,
    },
    kpiRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12, flexWrap: 'wrap', gap: 12 },
    kpi: { width: '48%' },
    loaderContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
    errorContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
    errorText: { ...theme.typography.h3, color: theme.colors.error },
  });

  if (isLoading) {
    return (
      <View style={styles.loaderContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  if (isError || !data) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Erro ao carregar os dados.</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Dashboard de Análise</Text>
        <Text style={styles.subtitle}>Visão geral do negócio</Text>
      </View>

      <View style={styles.periodFilterContainer}>
        {PERIODS.map(p => (
          <TouchableOpacity
            key={p.value}
            style={[styles.periodButton, period === p.value && styles.periodButtonActive]}
            onPress={() => setPeriod(p.value)}
          >
            <Text style={[styles.periodButtonText, period === p.value && styles.periodButtonTextActive]}>{p.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <ScrollView contentContainerStyle={{ padding: 12, paddingBottom: 24 }}>
        <View style={styles.kpiRow}>
          <Card title="Receita Total" style={styles.kpi}>
            <Text style={{ ...theme.typography.h1 }}>R$ {data.kpis.total_revenue.toFixed(2)}</Text>
          </Card>
          <Card title="Contas a Pagar" style={styles.kpi}>
            <Text style={{ ...theme.typography.h1 }}>R$ {data.kpis.pending_payments.toFixed(2)}</Text>
          </Card>
          <Card title="Notas Processadas" style={styles.kpi}>
            <Text style={{ ...theme.typography.h1 }}>{data.kpis.processed_invoices}</Text>
          </Card>
          <Card title="Fornecedores Ativos" style={styles.kpi}>
            <Text style={{ ...theme.typography.h1 }}>{data.kpis.active_suppliers}</Text>
          </Card>
        </View>

        <LineChartCard
          title="Evolução da Receita (Últimos 6 Meses)"
          data={data.charts.revenue_evolution.map(item => ({ x: item.month, y: item.total }))}
        />

        <BarChartCard
          title="Top 5 Fornecedores"
          data={data.charts.top_suppliers.map(item => ({ x: item.nome, y: item.total }))}
        />

        <DonutChartCard
          title="Distribuição de Lançamentos"
          data={data.charts.financial_entry_distribution.map(item => ({ x: item.tipo, y: item.total }))}
        />

        <BarChartCard
          title="Status dos Lançamentos"
          data={data.charts.financial_status_distribution.map(item => ({ x: item.status, y: item.count }))}
        />
      </ScrollView>
    </SafeAreaView>
  );
}
