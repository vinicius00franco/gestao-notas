import { MaterialIcons } from '@expo/vector-icons';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createDrawerNavigator, DrawerContentComponentProps } from '@react-navigation/drawer';
import { DarkTheme, DefaultTheme, NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import * as SplashScreen from 'expo-splash-screen';
import React, { useCallback, useEffect } from 'react';
import { TouchableOpacity, useColorScheme } from 'react-native';
import { useGlobalStore } from '../store/global';

import CustomDrawerContent from '@/components/CustomDrawerContent';
import withErrorBoundary from '@/components/withErrorBoundary';
import CalendarScreen from '@/screens/CalendarScreen';
import ClassifyCompanyScreen from '@/screens/ClassifyCompanyScreen';
import ClassifyNotasKanbanScreen from '@/screens/ClassifyNotasKanbanScreen';
import ContasAPagarScreen from '@/screens/ContasAPagarScreen';
import ContasAReceberScreen from '@/screens/ContasAReceberScreen';
import DashboardScreen from '@/screens/DashboardScreen';
import HomeScreen from '@/screens/HomeScreen';
import JobStatusScreen from '@/screens/JobStatusScreen';
import NotaFiscalDetailScreen from '@/screens/NotaFiscalDetailScreen';
import NotasFiscaisScreen from '@/screens/NotasFiscaisScreen';
import Splash from '@/screens/SplashScreen';
import UnclassifiedCompaniesScreen from '@/screens/UnclassifiedCompaniesScreen';
import UploadNotaScreen from '@/screens/UploadNotaScreen';
import { useTheme } from '@/theme/ThemeProvider';

const DashboardScreenWithErrorBoundary = withErrorBoundary(DashboardScreen);
const ContasAPagarScreenWithErrorBoundary = withErrorBoundary(ContasAPagarScreen);
const ContasAReceberScreenWithErrorBoundary = withErrorBoundary(ContasAReceberScreen);
const UploadNotaScreenWithErrorBoundary = withErrorBoundary(UploadNotaScreen);
const JobStatusScreenWithErrorBoundary = withErrorBoundary(JobStatusScreen);
const UnclassifiedCompaniesScreenWithErrorBoundary = withErrorBoundary(UnclassifiedCompaniesScreen);
const ClassifyCompanyScreenWithErrorBoundary = withErrorBoundary(ClassifyCompanyScreen);
const ClassifyNotasKanbanScreenWithErrorBoundary = withErrorBoundary(ClassifyNotasKanbanScreen);
const NotasFiscaisScreenWithErrorBoundary = withErrorBoundary(NotasFiscaisScreen);
const NotaFiscalDetailScreenWithErrorBoundary = withErrorBoundary(NotaFiscalDetailScreen);
const HomeScreenWithErrorBoundary = withErrorBoundary(HomeScreen);
const CalendarScreenWithErrorBoundary = withErrorBoundary(CalendarScreen);

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
      <Tab.Screen name="Dashboard" component={DashboardScreenWithErrorBoundary} />
      <Tab.Screen name="Pagar" component={ContasAPagarScreenWithErrorBoundary} />
      <Tab.Screen name="Receber" component={ContasAReceberScreenWithErrorBoundary} />
      <Tab.Screen name="Upload" component={UploadNotaScreenWithErrorBoundary} />
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
          headerTitleStyle: { left: 60 },
          drawerIcon: ({ color, size }) => <MaterialIcons name="account-balance" size={size} color={color} />,
        }}
      />
      <Drawer.Screen
        name="JobStatus"
        component={JobStatusScreenWithErrorBoundary}
        options={{
          title: 'Status do Job',
          headerTitleStyle: { left: 70 },
          drawerIcon: ({ color, size }) => <MaterialIcons name="sync" size={size} color={color} />,
        }}
      />
      <Drawer.Screen
        name="UnclassifiedCompanies"
        component={ClassifyNotasKanbanScreenWithErrorBoundary}
        options={{
          title: 'Classificar Notas',
          headerTitleStyle: { left: 60 },
          drawerIcon: ({ color, size }) => <MaterialIcons name="class" size={size} color={color} />,
        }}
      />
      <Drawer.Screen
        name="NotasFiscais"
        component={NotasFiscaisScreenWithErrorBoundary}
        options={{
          title: 'Notas Fiscais',
          headerTitleStyle: { left: 70 },
          drawerIcon: ({ color, size }) => <MaterialIcons name="receipt" size={size} color={color} />,
        }}
      />
      <Drawer.Screen
        name="Calendario"
        component={CalendarScreenWithErrorBoundary}
        options={{
          title: 'Calendário',
          headerTitleStyle: { left: 90 },
          drawerIcon: ({ color, size }) => <MaterialIcons name="event" size={size} color={color} />,
        }}
      />
    </Drawer.Navigator>
  );
}

export default function RootNavigator() {
  const scheme = useColorScheme();
  const { colors } = useTheme();
  const { isDBReady } = useGlobalStore();

  useEffect(() => {
    async function prepare() {
      try {
        await SplashScreen.preventAutoHideAsync();
      } catch (e) {
        console.warn(e);
      }
    }

    prepare();
  }, []);

  const onLayoutRootView = useCallback(async () => {
    if (isDBReady) {
      await SplashScreen.hideAsync();
    }
  }, [isDBReady]);

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

  if (!isDBReady) {
    // Render a visible fallback while waiting DB init to avoid a blank page
    return <Splash />;
  }

  return (
    <NavigationContainer theme={navigationTheme} onReady={onLayoutRootView}>
      <Stack.Navigator
        initialRouteName="App"
        screenOptions={{
          animation: 'slide_from_right',
          headerShown: false,
        }}>
        <Stack.Screen name="Home" component={HomeScreenWithErrorBoundary} />
        <Stack.Screen name="App" component={AppDrawer} />
        <Stack.Screen
          name="ClassifyCompany"
          component={ClassifyCompanyScreenWithErrorBoundary}
          options={{ headerShown: true }}
        />
        <Stack.Screen
          name="NotaFiscalDetail"
          component={NotaFiscalDetailScreenWithErrorBoundary}
          options={{ headerShown: true, title: 'Detalhes da Nota' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}