import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
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
      <TouchableOpacity style={styles.button} onPress={onRetry} activeOpacity={0.7}>
        <Text style={styles.buttonText}>Tentar Novamente</Text>
      </TouchableOpacity>
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
  button: {
    backgroundColor: colors.primary,
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ErrorScreen;