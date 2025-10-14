import axios, { AxiosError } from 'axios';
import Constants from 'expo-constants';
import { Platform } from 'react-native';

/**
 * Resolve API Base URL trying (in order):
 * 1. Explicit env/API_BASE_URL (expoConfig.extra.apiBaseUrl)
 * 2. Expo dev server host (Constants.expoConfig.hostUri / Constants.expoGoConfig?.hostUri)
 * 3. Browser location.host when Platform=web
 * 4. Android emulator default 10.0.2.2
 * 5. iOS simulator localhost
 */
function resolveApiBaseUrl() {
  // 1. Explicit override
  const explicit = Constants.expoConfig?.extra?.apiBaseUrl;
  if (explicit) return explicit.replace(/\/$/, '');

  // 2. Expo hostUri (e.g. 192.168.15.10:19000 or something.exp.direct:80)
  const hostUri: string | undefined = (Constants as any).expoConfig?.hostUri || (Constants as any).expoGoConfig?.hostUri;
  if (hostUri) {
    const host = hostUri.split(':')[0];
    if (host && /^\d+\.\d+\.\d+\.\d+$/.test(host)) {
      return `http://${host}:8080`;
    }
  }

  // 3. Try to get local IP from environment or config
  // You can set API_BASE_URL in .env file for your machine's IP
  const envUrl = process.env.API_BASE_URL;
  if (envUrl) return envUrl.replace(/\/$/, '');

  // 4. Web fallback: use current origin host
  if (Platform.OS === 'web' && typeof window !== 'undefined' && window.location?.hostname) {
    return `${window.location.protocol}//${window.location.hostname}:8080`;
  }

  // 5. Android emulator
  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8080';
  }

  // 6. iOS simulator / generic fallback
  return 'http://localhost:8080';
}

const apiBaseUrl = resolveApiBaseUrl();

export const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 20000,
  headers: { Accept: 'application/json' },
});

// Enhanced logging for troubleshooting network issues
api.interceptors.request.use((config) => {
  const composedUrl = `${config.baseURL || apiBaseUrl}${config.url || ''}`;
  console.debug('[api] Request', {
    method: config.method,
    url: composedUrl,
    hasAuth: !!config.headers?.Authorization,
    platform: Platform.OS,
  });
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.message === 'Network Error' || error.code === 'ERR_NETWORK') {
      console.error('[api] Network error', {
        baseURL: apiBaseUrl,
        originalURL: `${error.config?.baseURL || apiBaseUrl}${error.config?.url || ''}`,
        platform: Platform.OS,
        // axios hides more details; suggest checks
        suggestion: 'Verifique se o dispositivo consegue acessar o host (mesma rede Wi-Fi) e se o nginx está escutando na porta 8080.',
      });
    } else {
      console.error('[api] Response error', {
        status: error.response?.status,
        data: error.response?.data,
        url: `${error.config?.baseURL || apiBaseUrl}${error.config?.url || ''}`,
      });
    }
    return Promise.reject(error);
  }
);

export function setAuthToken(token?: string) {
  if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  else delete (api.defaults.headers.common as any)['Authorization'];
}

// Expose the resolved base URL for diagnostics (e.g., show in a debug screen)
export const resolvedApiBaseUrl = apiBaseUrl;