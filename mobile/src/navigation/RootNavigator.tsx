import React from 'react';
import { NavigationContainer, DefaultTheme, DarkTheme } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import DashboardScreen from '@/screens/DashboardScreen';
import ContasAPagarScreen from '@/screens/ContasAPagarScreen';
import ContasAReceberScreen from '@/screens/ContasAReceberScreen';
import UploadNotaScreen from '@/screens/UploadNotaScreen';
import JobStatusScreen from '@/screens/JobStatusScreen';
import { useColorScheme } from 'react-native';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

function Tabs() {
  return (
    <Tab.Navigator>
      <Tab.Screen name="Dashboard" component={DashboardScreen} />
      <Tab.Screen name="Pagar" component={ContasAPagarScreen} />
      <Tab.Screen name="Receber" component={ContasAReceberScreen} />
      <Tab.Screen name="Upload" component={UploadNotaScreen} />
    </Tab.Navigator>
  );
}

export default function RootNavigator() {
  const scheme = useColorScheme();
  return (
    <NavigationContainer theme={scheme === 'dark' ? DarkTheme : DefaultTheme}>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={Tabs} options={{ headerShown: false }} />
        <Stack.Screen name="JobStatus" component={JobStatusScreen} options={{ title: 'Status do Job' }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
