import React, { ReactNode } from 'react';
import { View, Text, StyleSheet, ViewProps } from 'react-native';
import { useTheme } from '@/theme/ThemeProvider';

type CardProps = ViewProps & {
  title?: string;
  children?: ReactNode;
};

export default function Card({ title, children, style, ...rest }: CardProps) {
  const theme = useTheme();

  const styles = StyleSheet.create({
    container: {
      backgroundColor: theme.colors.surface,
      borderRadius: 12,
      padding: theme.spacing.m,
      marginVertical: theme.spacing.s,
      ...theme.shadows.small,
    },
    title: {
      ...theme.typography.caption,
      color: theme.colors.onSurfaceVariant,
      marginBottom: theme.spacing.s,
    },
  });

  return (
    <View style={[styles.container, style]} {...rest}>
      {title ? <Text style={styles.title}>{title}</Text> : null}
      {children}
    </View>
  );
}
