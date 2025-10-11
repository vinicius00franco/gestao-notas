import 'dotenv/config'
declare const process: any;
const defineConfig = () => ({
  name: 'gestao-notas-mobile',
  slug: 'gestao-notas-mobile',
  scheme: 'gestaonotas',
  version: '0.1.0',
  orientation: 'portrait',
  // If you want custom icons/splash images, place them under mobile/assets and uncomment the entries below.
  // icon: './assets/icon.png', // crie os assets se desejar customizar
  userInterfaceStyle: 'automatic',
  // splash: {
  //   image: './assets/splash.png',
  //   resizeMode: 'contain',
  //   backgroundColor: '#ffffff'
  // },
  ios: { 
    supportsTablet: true,
    bundleIdentifier: 'com.gestaonotas.mobile'
  },
  android: { 
    package: 'com.gestaonotas.mobile',
    adaptiveIcon: {
      backgroundColor: '#FFFFFF'
    }
  },
  // web: { bundler: 'metro', output: 'static', favicon: './assets/favicon.png' },
  extra: {
    apiBaseUrl: (process as any)?.env?.API_BASE_URL || 'http://localhost:8000'
    // Note: projectId will be added automatically by 'eas init' or you can add it manually
    // after creating an Expo account and project at https://expo.dev
  }
});

export default defineConfig;
