import axios from 'axios';
import Constants from 'expo-constants';

// Resolve API base URL with priority:
// 1. API_BASE_URL from Expo config (via .env)
// 2. Throw error if not defined
const apiBaseUrl = (Constants.expoConfig?.extra?.apiBaseUrl as string);

if (!apiBaseUrl) {
  throw new Error(
    'API_BASE_URL is not defined. Please set the API_BASE_URL environment variable in your .env file or app.config.ts'
  );
}

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