import React, { useCallback, useEffect, useState } from 'react';
import { NavigationContainer, DefaultTheme, DarkTheme } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createDrawerNavigator, DrawerContentComponentProps } from '@react-navigation/drawer';
import { useColorScheme } from 'react-native';
import * as SplashScreen from 'expo-splash-screen';
import { MaterialIcons } from '@expo/vector-icons';

import DashboardScreen from '@/screens/DashboardScreen';
import ContasAPagarScreen from '@/screens/ContasAPagarScreen';
import ContasAReceberScreen from '@/screens/ContasAReceberScreen';
import UploadNotaScreen from '@/screens/UploadNotaScreen';
import JobStatusScreen from '@/screens/JobStatusScreen';
import HomeScreen from '@/screens/HomeScreen';
import { useTheme } from '@/theme/ThemeProvider';
import CustomDrawerContent from '@/components/CustomDrawerContent';
import UnclassifiedCompaniesScreen from '@/screens/UnclassifiedCompaniesScreen';
import ClassifyCompanyScreen from '@/screens/ClassifyCompanyScreen';
import ClassifyNotasKanbanScreen from '@/screens/ClassifyNotasKanbanScreen';
import Splash from '@/screens/SplashScreen';
import { analytics } from '@/services/analytics';
import { NavigationState } from '@react-navigation/native';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();
const Drawer = createDrawerNavigator();

function MainTabs() {
  const { colors } = useTheme();
  return (
    <Tab.Navigator
      initialRouteName="Dashboard"
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.placeholder,
        tabBarStyle: { backgroundColor: colors.surface },
        tabBarIcon: ({ color, size }) => {
          let iconName: React.ComponentProps<typeof MaterialIcons>['name'] = 'dashboard';

          if (route.name === 'Dashboard') {
            iconName = 'dashboard';
          } else if (route.name === 'Pagar') {
            iconName = 'payment';
          } else if (route.name === 'Receber') {
            iconName = 'receipt-long';
          } else if (route.name === 'Upload') {
            iconName = 'cloud-upload';
          }

          // You can return any component that you like here!
          return <MaterialIcons name={iconName} size={size} color={color} />;
        },
      })}>
      <Tab.Screen name="Dashboard" component={DashboardScreen} />
      <Tab.Screen name="Pagar" component={ContasAPagarScreen} />
      <Tab.Screen name="Receber" component={ContasAReceberScreen} />
      <Tab.Screen name="Upload" component={UploadNotaScreen} />
    </Tab.Navigator>
  );
}

function AppDrawer() {
  const { colors } = useTheme();
  return (
    <Drawer.Navigator
      drawerContent={(props: DrawerContentComponentProps) => <CustomDrawerContent {...props} />}
      screenOptions={({ navigation }) => ({
        headerStyle: {
          backgroundColor: colors.primary,
        },
        headerTintColor: colors.onPrimary,
        drawerStyle: {
          backgroundColor: colors.background,
        },
        drawerActiveTintColor: colors.primary,
        drawerInactiveTintColor: colors.text,
        headerLeft: () => (
          <TouchableOpacity
            testID="drawer-button"
            onPress={() => navigation.openDrawer()}
            style={{ marginLeft: 15 }}>
            <MaterialIcons name="menu" size={24} color={colors.onPrimary} />
          </TouchableOpacity>
        ),
      })}>
      <Drawer.Screen
        name="Main"
        component={MainTabs}
        options={{
          title: 'Gestão de Notas',
          drawerIcon: ({ color, size }) => <MaterialIcons name="account-balance" size={size} color={color} />,
        }}
      />
      <Drawer.Screen
        name="JobStatus"
        component={JobStatusScreen}
        options={{
          title: 'Status do Job',
          drawerIcon: ({ color, size }) => <MaterialIcons name="sync" size={size} color={color} />,
        }}
      />
      <Drawer.Screen
        name="UnclassifiedCompanies"
        component={UnclassifiedCompaniesScreen}
        options={{
          title: 'Unclassified Companies',
          drawerIcon: ({ color, size }) => <MaterialIcons name="business" size={size} color={color} />,
        }}
      />
      <Drawer.Screen
        name="ClassifyNotas"
        component={ClassifyNotasKanbanScreen}
        options={{
          title: 'Classificar Notas',
          drawerIcon: ({ color, size }) => <MaterialIcons name="class" size={size} color={color} />,
        }}
      />
    </Drawer.Navigator>
  );
}

const getCurrentRouteName = (state: NavigationState | undefined): string | undefined => {
  if (!state) {
    return undefined;
  }

  const route = state.routes[state.index];

  if (route.state) {
    // Dive into nested navigators
    return getCurrentRouteName(route.state as NavigationState);
  }

  return route.name;
};

export default function RootNavigator() {
  const scheme = useColorScheme();
  const { colors } = useTheme();
  const [appIsReady, setAppIsReady] = useState(false);

  useEffect(() => {
    async function prepare() {
      try {
        // Keep the splash screen visible while we fetch resources
        await SplashScreen.preventAutoHideAsync();
        // Artificially delay for two seconds to simulate a slow loading
        // experience. Please remove this if you copy and paste the code!
        await new Promise(resolve => setTimeout(resolve, 2000));
      } catch (e) {
        console.warn(e);
      } finally {
        // Tell the application to render
        setAppIsReady(true);
      }
    }

    prepare();
  }, []);

  const onLayoutRootView = useCallback(async () => {
    if (appIsReady) {
      // This tells the splash screen to hide immediately! If we call this after
      // `setAppIsReady`, then we may see a blank screen while the app is
      // loading its initial state and rendering its first pixels. So instead,
      // we hide the splash screen once we know the root view has already
      // performed layout.
      await SplashScreen.hideAsync();
    }
  }, [appIsReady]);

  const navigationTheme = {
    ...(scheme === 'dark' ? DarkTheme : DefaultTheme),
    colors: {
      ...(scheme === 'dark' ? DarkTheme.colors : DefaultTheme.colors),
      primary: colors.primary,
      background: colors.background,
      card: colors.surface,
      text: colors.text,
      border: colors.border,
    },
  };

  if (!appIsReady) {
    return <Splash />;
  }

  return (
    <NavigationContainer
      theme={navigationTheme}
      onReady={onLayoutRootView}
      onStateChange={(state) => {
        const currentRouteName = getCurrentRouteName(state);
        analytics.trackScreenView(currentRouteName);
      }}
    >
      <Stack.Navigator
        initialRouteName="App"
        screenOptions={{
          animation: 'slide_from_right',
          headerShown: false,
        }}>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="App" component={AppDrawer} />
        <Stack.Screen
          name="ClassifyCompany"
          component={ClassifyCompanyScreen}
          options={{ headerShown: true }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}