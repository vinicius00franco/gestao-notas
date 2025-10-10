import React from 'react';
import { NavigationContainer, DefaultTheme, DarkTheme } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createDrawerNavigator, DrawerContentComponentProps } from '@react-navigation/drawer';
import { useColorScheme } from 'react-native';

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

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();
const Drawer = createDrawerNavigator();

function MainTabs() {
  const { colors } = useTheme();
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.placeholder,
        tabBarStyle: { backgroundColor: colors.surface },
      }}>
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
      screenOptions={{
        headerStyle: {
          backgroundColor: colors.primary,
        },
        headerTintColor: colors.onPrimary,
        drawerStyle: {
          backgroundColor: colors.background,
        },
        drawerActiveTintColor: colors.primary,
        drawerInactiveTintColor: colors.text,
      }}>
      <Drawer.Screen name="Main" component={MainTabs} options={{ title: 'Gestão de Notas' }} />
      <Drawer.Screen name="JobStatus" component={JobStatusScreen} options={{ title: 'Status do Job' }} />
      <Drawer.Screen name="UnclassifiedCompanies" component={UnclassifiedCompaniesScreen} options={{ title: 'Unclassified Companies' }} />
    </Drawer.Navigator>
  );
}

export default function RootNavigator() {
  const scheme = useColorScheme();
  const { colors } = useTheme();

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

  return (
    <NavigationContainer theme={navigationTheme}>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={HomeScreen} options={{ headerShown: false }} />
        <Stack.Screen name="App" component={AppDrawer} options={{ headerShown: false }} />
        <Stack.Screen name="ClassifyCompany" component={ClassifyCompanyScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}