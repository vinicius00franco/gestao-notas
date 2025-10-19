import 'react-native-gesture-handler';
// Important: Initialize Reanimated before any other imports that use it
import 'react-native-reanimated';
import React from 'react';
import { AppState, Platform } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import RootNavigator from '@/navigation/RootNavigator';
import NotificationsService from '@/services/notifications';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StatusBar } from 'expo-status-bar';
import { ThemeProvider } from '@/theme/ThemeProvider';
import FlashMessage from 'react-native-flash-message';
import { useInit } from './hooks/use-init';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnReconnect: true,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  useInit();
  React.useEffect(() => {
    // initialize push notifications (skip on web)
    const initNotifications = async () => {
      if (Platform.OS !== 'web') {
        await NotificationsService.configureNotifications();
        // initial fetch of pending notifications
        await NotificationsService.fetchAndShowPendingNotifications();
      }
    };
    initNotifications();

    // listen app foreground transitions to fetch pending notifications
    const sub = AppState.addEventListener('change', (state) => {
      if (state === 'active' && Platform.OS !== 'web') {
        NotificationsService.fetchAndShowPendingNotifications();
      }
    });
    return () => sub.remove();
  }, []);
  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <StatusBar style="auto" />
          <RootNavigator />
          {Platform.OS !== 'web' ? <FlashMessage position="top" /> : null}
        </ThemeProvider>
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}
