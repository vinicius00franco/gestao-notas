import React from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';
import { colors } from '../theme/colors';

interface Props {
  onRetry: () => void;
}

const ErrorScreen: React.FC<Props> = ({ onRetry }) => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Oops! Algo deu errado.</Text>
      <Text style={styles.message}>
        Não foi possível concluir sua solicitação. Por favor, tente novamente.
      </Text>
      <Button title="Tentar Novamente" onPress={onRetry} color={colors.primary} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.text,
    textAlign: 'center',
    marginBottom: 16,
  },
  message: {
    fontSize: 16,
    color: colors.text,
    textAlign: 'center',
    marginBottom: 24,
  },
});

export default ErrorScreen;