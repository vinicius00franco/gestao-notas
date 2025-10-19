import 'dotenv/config'
declare const process: any;
const defineConfig = () => ({
  name: 'gestao-notas-mobile',
  slug: 'gestao-notas-mobile',
  owner: 'pfranco',
  scheme: 'gestaonotas',
  version: '0.1.0',
  orientation: 'portrait',
  // If you want custom icons/splash images, place them under mobile/assets and uncomment the entries below.
  // icon: './assets/icon.png', // crie os assets se desejar customizar
  userInterfaceStyle: 'automatic',
  splash: {
    "image": "./assets/splash.png",
    "resizeMode": "contain",
    "backgroundColor": "#ffffff"
  },
  plugins: [
    [
      "expo-splash-screen",
      {
        "splash_screen_resize_mode": "contain",
        "splash_background_color": "#ffffff"
      }
    ]
  ],
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
    apiBaseUrl: (process as any)?.env?.API_BASE_URL,
    // Add a new APP_MODE variable to control the data source
    appMode: (process as any)?.env?.APP_MODE || 'real', // 'real' or 'mock'
    eas: {
      projectId: "42afdd4a-ca0b-46f0-81f5-cb4826a2170f"
    }
  }
});

export default defineConfig;
