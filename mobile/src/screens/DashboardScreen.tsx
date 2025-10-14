import React from 'react';
import { View, Button } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import CalendarDashboard from '@/components/CalendarDashboard';

export default function DashboardScreen() {
  const navigation = useNavigation<any>();
  return (
    <View style={{ flex: 1 }}>
      <View style={{ flexDirection: 'row', gap: 8, padding: 8 }}>
        <Button title="Unclassified Companies" onPress={() => navigation.navigate('UnclassifiedCompanies')} />
        <Button title="Ver/Excluir Notas Fiscais" onPress={() => navigation.navigate('NotasFiscais')} />
      </View>
      <CalendarDashboard />
    </View>
  );
}
