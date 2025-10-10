import React from 'react';
import { View, Text, StyleSheet, SafeAreaView, TouchableOpacity } from 'react-native';
import { DrawerContentScrollView, DrawerItemList, DrawerContentComponentProps } from '@react-navigation/drawer';
import { useTheme } from '@/theme/ThemeProvider';

const CustomDrawerContent = (props: DrawerContentComponentProps) => {
  const { colors } = useTheme();

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
      <View style={[styles.header, { backgroundColor: colors.primary }]}>
        <Text style={[styles.headerText, { color: colors.onPrimary }]}>Gestão de Notas</Text>
      </View>
      <DrawerContentScrollView {...props}>
        <DrawerItemList {...props} />
      </DrawerContentScrollView>
      <View style={styles.footer}>
        <TouchableOpacity onPress={() => props.navigation.closeDrawer()} style={styles.footerButton}>
          <Text style={{ color: colors.text }}>Fechar</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  header: {
    padding: 20,
    paddingTop: 40,
    alignItems: 'center',
  },
  headerText: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  footer: {
    borderTopWidth: 1,
    borderTopColor: '#ccc',
    padding: 20,
  },
  footerButton: {
    padding: 10,
    alignItems: 'center',
  },
});

export default CustomDrawerContent;