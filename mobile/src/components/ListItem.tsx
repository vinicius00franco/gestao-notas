import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';

export function ListItem({ title, subtitle, right }: { title: string; subtitle?: string; right?: React.ReactNode }) {
  const theme = useTheme();

  const styles = StyleSheet.create({
    container: {
      padding: theme.spacing.m,
      borderBottomWidth: 1,
      borderColor: theme.colors.border,
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    content: {},
    title: {
      ...theme.typography.body,
      fontWeight: '600',
      color: theme.colors.text,
    },
    subtitle: {
      ...theme.typography.caption,
      color: theme.colors.muted,
    },
  });

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>{title}</Text>
        {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
      </View>
      {right}
    </View>
  );
}