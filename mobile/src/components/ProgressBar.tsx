import React from 'react';
import { View, Text } from 'react-native';

interface ProgressBarProps {
  progress: number;
}

export default function ProgressBar({ progress }: ProgressBarProps) {
  return (
    <View>
      <Text>{(progress * 100).toFixed(0)}%</Text>
      <View style={{ height: 10, backgroundColor: '#e0e0e0', borderRadius: 5 }}>
        <View style={{ height: '100%', width: `${progress * 100}%`, backgroundColor: '#3b82f6', borderRadius: 5 }} />
      </View>
    </View>
  );
}