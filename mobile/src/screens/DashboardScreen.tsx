import { ActivityIndicator, FlatList, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useDashboard } from '../hooks/api';
import { useTheme } from '../theme/ThemeProvider';
import { TopFornecedor } from '../types';

export default function DashboardScreen() {
  const theme = useTheme();
  const { data, isLoading, isError } = useDashboard();

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: theme.colors.background },
    loaderContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
    errorContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
    errorText: { ...theme.typography.h2, color: theme.colors.error },
    header: { paddingHorizontal: 16, paddingTop: 4, paddingBottom: 8 },
    title: { ...theme.typography.h2 },
    listContainer: {
      paddingHorizontal: 16,
    },
    itemContainer: {
      backgroundColor: theme.colors.surface,
      padding: 16,
      marginVertical: 8,
      borderRadius: 8,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    itemText: {
      ...theme.typography.body,
      color: theme.colors.onSurface,
    },
    itemTitle: {
      ...theme.typography.h2,
      color: theme.colors.onSurface,
      marginBottom: 4,
    }
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

  const renderItem = ({ item }: { item: TopFornecedor }) => (
    <View style={styles.itemContainer}>
      <Text style={styles.itemTitle}>{item.nome}</Text>
      <Text style={styles.itemText}>CNPJ: {item.cnpj}</Text>
      <Text style={styles.itemText}>Total a Pagar: R$ {item.total_a_pagar.toFixed(2)}</Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Top 5 Fornecedores Pendente</Text>
      </View>
      <FlatList
        data={data.top_5_fornecedores_pendentes}
        renderItem={renderItem}
        keyExtractor={(item) => item.cnpj}
        contentContainerStyle={styles.listContainer}
      />
    </SafeAreaView>
  );
}