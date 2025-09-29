import React from 'react';
import { View, Text, Button } from 'react-native';

export default function ErrorView({ message, onRetry }: { message?: string; onRetry?: () => void }) {
  return (
    <View style={{ padding: 16 }}>
      <Text style={{ color: '#dc2626', marginBottom: 8 }}>Erro: {message || 'Algo deu errado.'}</Text>
      {onRetry && <Button title="Tentar novamente" onPress={onRetry} />}
    </View>
  );
}
