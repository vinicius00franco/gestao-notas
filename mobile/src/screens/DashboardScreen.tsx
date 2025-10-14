import React, { useMemo } from 'react';
import { View, Button, SafeAreaView, ScrollView, StyleSheet, Text } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import CalendarDashboard from '@/components/CalendarDashboard';
import Card from '@/components/Card';
import LineChartCard from '@/components/charts/LineChartCard';
import StackedBarChartCard from '@/components/charts/StackedBarChartCard';
import DonutChartCard from '@/components/charts/DonutChartCard';
import { useTheme } from '@/theme/ThemeProvider';

export default function DashboardScreen() {
  const navigation = useNavigation<any>();
  const theme = useTheme();

  const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'];
  const lineData = useMemo(
    () => [
      { x: 'Jan', y: 620 },
      { x: 'Fev', y: 980 },
      { x: 'Mar', y: 820 },
      { x: 'Abr', y: 510 },
      { x: 'Mai', y: 530 },
      { x: 'Jun', y: 560 },
    ],
    [],
  );

  const stackedSeries = useMemo(
    () => [
      { color: '#4C6FFF', data: months.map((m, i) => ({ x: m, y: [30, 20, 15, 10, 25, 35][i] })) },
      { color: '#FF5C8A', data: months.map((m, i) => ({ x: m, y: [20, 15, 10, 8, 12, 18][i] })) },
      { color: '#22C55E', data: months.map((m, i) => ({ x: m, y: [10, 8, 6, 5, 7, 9][i] })) },
    ],
    [],
  );

  const donutData = useMemo(
    () => [
      { x: 'Com descrição', y: 18575, color: '#7C3AED' },
      { x: 'Sem descrição', y: 13250, color: '#EDE9FE' },
    ],
    [],
  );

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: theme.colors.background },
    header: { paddingHorizontal: 16, paddingTop: 4, paddingBottom: 8 },
    title: { ...theme.typography.h2 },
    subtitle: { ...theme.typography.caption },
    actions: { flexDirection: 'row', gap: 8, paddingHorizontal: 8, paddingBottom: 8 },
    grid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
    half: { width: '49%' },
    kpiRow: { flexDirection: 'row', justifyContent: 'space-between' },
    kpi: { width: '49%' },
    bottomBar: {
      position: 'absolute',
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: theme.colors.surface,
      padding: 12,
      borderTopWidth: StyleSheet.hairlineWidth,
      borderColor: theme.colors.border,
    },
    bottomText: { textAlign: 'center', color: theme.colors.onSurfaceVariant },
  });

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Sales Analysis</Text>
        <Text style={styles.subtitle}>Overview summary (1 of 9)</Text>
      </View>
      <View style={styles.actions}>
        <Button title="Classificar Notas" onPress={() => navigation.navigate('UnclassifiedCompanies')} />
        <Button title="Notas Fiscais" onPress={() => navigation.navigate('NotasFiscais')} />
      </View>
      <ScrollView contentContainerStyle={{ padding: 12, paddingBottom: 110 }}>
        <View style={styles.kpiRow}>
          <Card title="Sales" style={styles.kpi}>
            <Text style={{ ...theme.typography.h1 }}>$12.6M</Text>
          </Card>
          <Card title="Revenue" style={styles.kpi}>
            <Text style={{ ...theme.typography.h1 }}>$12.6M</Text>
          </Card>
        </View>

        <LineChartCard title="Average of Expenditures ($m) by Date" data={lineData} />

        <StackedBarChartCard title="Sales by Month and Region" series={stackedSeries} categories={months} />

        <View style={styles.grid}>
          <DonutChartCard title="Metadata completeness" data={donutData} height={220} />
          <Card style={styles.half} title="Usage and overage per capacity">
            <Text style={styles.subtitle}>Contoso-Sales 99% / 100%</Text>
            <Text style={styles.subtitle}>Contoso-Marketing 80% / 100%</Text>
          </Card>
        </View>

        <Card title="Opportunity Created by Campaign">
          <CalendarDashboard />
        </Card>
      </ScrollView>

      <View style={styles.bottomBar}>
        <Text style={styles.bottomText}>Comments   •   Reset   •   Filters   •   Pages   •   More</Text>
      </View>
    </SafeAreaView>
  );
}
