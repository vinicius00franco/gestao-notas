const defineConfig = () => ({
  name: 'gestao-notas-mobile',
  slug: 'gestao-notas-mobile',
  scheme: 'gestaonotas',
  version: '0.1.0',
  orientation: 'portrait',
  icon: './assets/icon.png', // crie os assets se desejar customizar
  userInterfaceStyle: 'automatic',
  splash: {
  image: './assets/splash.png',
    resizeMode: 'contain',
    backgroundColor: '#ffffff'
  },
  ios: { supportsTablet: true },
  android: { adaptiveIcon: { foregroundImage: './assets/adaptive-icon.png', backgroundColor: '#ffffff' } },
  web: { bundler: 'metro', output: 'static', favicon: './assets/favicon.png' },
  extra: {
    apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000'
  }
});

export default defineConfig;
