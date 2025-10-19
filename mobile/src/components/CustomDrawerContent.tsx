import { useTheme } from '@/theme/ThemeProvider';
import { MaterialIcons } from '@expo/vector-icons';
import { DrawerContentComponentProps, DrawerContentScrollView, DrawerItemList } from '@react-navigation/drawer';
import { StyleSheet, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

const CustomDrawerContent = (props: DrawerContentComponentProps) => {
  const { colors } = useTheme();

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
      <TouchableOpacity style={styles.closeButton} onPress={() => props.navigation.closeDrawer()}>
        <MaterialIcons name="close" size={24} color={colors.text}/>
      </TouchableOpacity>
      
     
      <DrawerContentScrollView {...props}>
        <DrawerItemList {...props} />
      </DrawerContentScrollView>
     
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  header: {
    padding: 20,
    alignItems: 'center',
  },
  headerText: {
    fontSize: 20,
    fontWeight: 'bold',
  },
 closeButton: {
   position: 'absolute',
   top: 30,
   right: 20,
   zIndex: 1,
 }, 
});

export default CustomDrawerContent;