import 'react-native-gesture-handler';
import React from 'react';
import RootNavigator from '@/navigation/RootNavigator';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StatusBar } from 'expo-status-bar';
import ErrorBoundary from '@/components/ErrorBoundary';

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
  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <StatusBar style="auto" />
        <RootNavigator />
      </ErrorBoundary>
    </QueryClientProvider>
  );
}
