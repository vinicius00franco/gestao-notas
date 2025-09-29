import React from 'react';
import { View, Text } from 'react-native';

export default function EmptyState({ message }: { message: string }) {
  return (
    <View style={{ padding: 16 }}>
      <Text style={{ color: '#6b7280' }}>{message}</Text>
    </View>
  );
}
