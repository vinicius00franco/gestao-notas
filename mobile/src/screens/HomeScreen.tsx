import React from 'react';
import { View, Text, Button, StyleSheet, BackHandler, Platform, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';

export default function HomeScreen() {
  const navigation = useNavigation<any>();

  const entrar = (tab?: string) => {
    if (tab) {
      navigation.navigate('MainTabs', { screen: tab });
    } else {
      navigation.navigate('MainTabs');
    }
  };

  const sairDoApp = () => {
    if (Platform.OS === 'android') {
      BackHandler.exitApp();
    } else {
      Alert.alert('Indisponível', 'Encerrar o app programaticamente não é permitido no iOS.');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Gestão de Notas</Text>
      <View style={styles.section}>
        <Button title="Entrar" onPress={() => entrar()} />
      </View>
      <View style={styles.section}>
        <Text style={styles.subtitle}>Acessos rápidos</Text>
        <View style={styles.buttonsRow}>
          <View style={[styles.buttonItem, { marginRight: 8 }]}><Button title="Dashboard" onPress={() => entrar('Dashboard')} /></View>
          <View style={[styles.buttonItem, { marginLeft: 8 }]}><Button title="A Pagar" onPress={() => entrar('Pagar')} /></View>
        </View>
        <View style={[styles.buttonsRow, { marginTop: 12 }]}>
          <View style={[styles.buttonItem, { marginRight: 8 }]}><Button title="A Receber" onPress={() => entrar('Receber')} /></View>
          <View style={[styles.buttonItem, { marginLeft: 8 }]}><Button title="Upload" onPress={() => entrar('Upload')} /></View>
        </View>
      </View>
      <View style={[styles.section, { marginTop: 24 }] }>
        <Button color="#d32f2f" title="Sair do app" onPress={sairDoApp} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, justifyContent: 'center' },
  title: { fontSize: 24, fontWeight: '800', textAlign: 'center', marginBottom: 24 },
  subtitle: { fontSize: 16, fontWeight: '600', marginBottom: 12 },
  section: { marginVertical: 8 },
  buttonsRow: { flexDirection: 'row' },
  buttonItem: { flex: 1 },
});
