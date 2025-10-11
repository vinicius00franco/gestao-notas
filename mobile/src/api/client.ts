import axios from 'axios';
import Constants from 'expo-constants';

// Resolve API base URL with priority:
// 1. API_BASE_URL from Expo config (via .env)
// 2. Fallback to a sensible default for local dev
const apiBaseUrl =
  (Constants.expoConfig?.extra?.apiBaseUrl as string) || 'http://localhost:8080';

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