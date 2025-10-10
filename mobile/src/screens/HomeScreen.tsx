import React from 'react';
import { View, Text, StyleSheet, BackHandler, Platform, Alert, TouchableOpacity, SafeAreaView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '@/theme/ThemeProvider';

export default function HomeScreen() {
  const navigation = useNavigation<any>();
  const { colors, spacing, typography, shadows } = useTheme();

  const entrar = (tab?: string) => {
    if (tab) {
      navigation.navigate('App', {
        screen: 'Main',
        params: { screen: tab },
      });
    } else {
      navigation.navigate('App');
    }
  };

  const sairDoApp = () => {
    if (Platform.OS === 'android') {
      BackHandler.exitApp();
    } else {
      Alert.alert('Indisponível', 'Encerrar o app programaticamente não é permitido no iOS.');
    }
  };

  const quickAccessButtons = [
    { title: 'Dashboard', screen: 'Dashboard' },
    { title: 'A Pagar', screen: 'Pagar' },
    { title: 'A Receber', screen: 'Receber' },
    { title: 'Upload', screen: 'Upload' },
  ];

  return (
    <SafeAreaView style={[styles.safeArea, { backgroundColor: colors.background }]}>
      <View style={[styles.container, { padding: spacing.l }]}>
        <Text style={[styles.title, typography.h1, { color: colors.primary, marginBottom: spacing.xl }]}>
          Bem-vindo ao Gestão de Notas
        </Text>
        <Text style={[styles.subtitle, typography.body, { color: colors.text, marginBottom: spacing.xxl, textAlign: 'center' }]}>
          Acesse rapidamente as principais funcionalidades do app.
        </Text>

        <TouchableOpacity
          style={[styles.mainButton, { backgroundColor: colors.primary, marginBottom: spacing.xl }, shadows.medium]}
          onPress={() => entrar()}
          activeOpacity={0.8}>
          <Text style={[styles.mainButtonText, typography.h2, { color: colors.onPrimary }]}>Entrar no App</Text>
        </TouchableOpacity>

        <View style={styles.quickAccessContainer}>
          {quickAccessButtons.map((button, index) => (
            <TouchableOpacity
              key={index}
              style={[
                styles.quickAccessButton,
                {
                  backgroundColor: colors.surface,
                  borderColor: colors.border,
                  width: '48%',
                  marginBottom: spacing.m,
                },
                shadows.small,
              ]}
              onPress={() => entrar(button.screen)}
              activeOpacity={0.7}>
              <Text style={[styles.quickAccessButtonText, typography.body, { color: colors.primary }]}>
                {button.title}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <TouchableOpacity
          style={[styles.exitButton, { marginTop: 'auto', backgroundColor: colors.error }]}
          onPress={sairDoApp}
          activeOpacity={0.8}>
          <Text style={[styles.exitButtonText, { color: colors.onError }]}>Sair do App</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    textAlign: 'center',
  },
  subtitle: {
    textAlign: 'center',
  },
  mainButton: {
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 30,
    width: '100%',
    alignItems: 'center',
  },
  mainButtonText: {
    fontWeight: 'bold',
  },
  quickAccessContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    width: '100%',
  },
  quickAccessButton: {
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 1,
  },
  quickAccessButtonText: {
    fontWeight: '600',
  },
  exitButton: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 20,
    alignItems: 'center',
  },
  exitButtonText: {
    fontWeight: 'bold',
    fontSize: 16,
  },
});