import 'react-native-gesture-handler';
import React from 'react';
import { AppState } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import RootNavigator from '@/navigation/RootNavigator';
import NotificationsService from '@/services/notifications';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StatusBar } from 'expo-status-bar';
import DefaultErrorBoundary from '@/components/DefaultErrorBoundary';
import { ThemeProvider } from '@/theme/ThemeProvider';
import FlashMessage from 'react-native-flash-message';

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
  React.useEffect(() => {
    // initialize push notifications (will register token and set listeners)
    const initNotifications = async () => {
      await NotificationsService.configureNotifications();
      // initial fetch of pending notifications
      await NotificationsService.fetchAndShowPendingNotifications();
    };
    initNotifications();

    // listen app foreground transitions to fetch pending notifications
    const sub = AppState.addEventListener('change', (state) => {
      if (state === 'active') {
        NotificationsService.fetchAndShowPendingNotifications();
      }
    });
    return () => sub.remove();
  }, []);
  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <DefaultErrorBoundary>
            <StatusBar style="auto" />
            <RootNavigator />
            <FlashMessage position="top" />
          </DefaultErrorBoundary>
        </ThemeProvider>
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}
