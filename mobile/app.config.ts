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
  ios: { supportsTablet: true },
  android: { package: 'com.gestaonotas.mobile' },
  // web: { bundler: 'metro', output: 'static', favicon: './assets/favicon.png' },
  extra: {
    apiBaseUrl: (process as any)?.env?.API_BASE_URL || 'http://localhost:8000'
  }
});

export default defineConfig;
