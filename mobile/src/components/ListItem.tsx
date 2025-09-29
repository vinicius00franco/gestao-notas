import React from 'react';
import { View, Text } from 'react-native';

export function ListItem({ title, subtitle, right }: { title: string; subtitle?: string; right?: React.ReactNode }) {
  return (
    <View style={{ padding: 16, borderBottomWidth: 1, borderColor: '#eee', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
      <View>
        <Text style={{ fontWeight: '600' }}>{title}</Text>
        {subtitle && <Text style={{ color: '#6b7280' }}>{subtitle}</Text>}
      </View>
      {right}
    </View>
  );
}
