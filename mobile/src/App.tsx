import 'react-native-gesture-handler';
import React from 'react';
import { AppState } from 'react-native';
import RootNavigator from '@/navigation/RootNavigator';
import NotificationsService from '@/services/notifications';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StatusBar } from 'expo-status-bar';
import ErrorBoundary from '@/components/ErrorBoundary';
import { ThemeProvider } from '@/theme/ThemeProvider';

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
    NotificationsService.configureNotifications();
    // initial fetch of pending notifications
    NotificationsService.fetchAndShowPendingNotifications();

    // listen app foreground transitions to fetch pending notifications
    const sub = AppState.addEventListener('change', (state) => {
      if (state === 'active') {
        NotificationsService.fetchAndShowPendingNotifications();
      }
    });
    return () => sub.remove();
  }, []);
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <ErrorBoundary>
          <StatusBar style="auto" />
          <RootNavigator />
        </ErrorBoundary>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
