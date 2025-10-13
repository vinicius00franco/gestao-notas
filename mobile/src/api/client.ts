import axios from 'axios';
import Constants from 'expo-constants';
import { Platform } from 'react-native';

// Define default URLs based on the platform
const defaultApiBaseUrl = Platform.OS === 'android'
  ? 'http://10.0.2.2:8080'
  : 'http://localhost:8080';

// Resolve API base URL with priority:
// 1. API_BASE_URL from Expo config (via .env)
// 2. Platform-specific default
const apiBaseUrl = Constants.expoConfig?.extra?.apiBaseUrl || defaultApiBaseUrl;

export const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 15000,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
});

export function setAuthToken(token?: string) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete (api.defaults.headers.common as any)['Authorization'];
  }
}