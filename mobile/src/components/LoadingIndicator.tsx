import React from 'react';
import { View, ActivityIndicator, StyleSheet, Modal, Text } from 'react-native';
import { useTheme } from '@/theme/ThemeProvider';

interface LoadingIndicatorProps {
  fullscreen?: boolean;
  message?: string;
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ fullscreen = false, message }) => {
  const { colors } = useTheme();

  const indicator = (
    <View style={styles.indicatorContainer}>
      <ActivityIndicator size="large" color={colors.primary} />
      {message && <Text style={[styles.message, { color: colors.text }]}>{message}</Text>}
    </View>
  );

  if (fullscreen) {
    return (
      <Modal transparent={true} animationType="none" visible={true}>
        <View style={[styles.modalBackground, { backgroundColor: 'rgba(0, 0, 0, 0.5)' }]}>
          <View style={[styles.activityIndicatorWrapper, { backgroundColor: colors.background }]}>
            {indicator}
          </View>
        </View>
      </Modal>
    );
  }

  return indicator;
};

const styles = StyleSheet.create({
  indicatorContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalBackground: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  activityIndicatorWrapper: {
    borderRadius: 10,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-around',
    padding: 20,
  },
  message: {
    marginTop: 10,
    fontSize: 16,
  },
});

export default LoadingIndicator;