import { TextStyle, ViewStyle } from 'react-native';
import { colors } from './colors';

const theme = {
  colors: {
    ...colors,
  },
  spacing: {
    xs: 4,
    s: 8,
    m: 16,
    l: 24,
    xl: 32,
    xxl: 40,
  },
  typography: {
    h1: {
      fontSize: 32,
      fontWeight: 'bold',
      color: colors.text,
    } as TextStyle,
    h2: {
      fontSize: 24,
      fontWeight: 'bold',
      color: colors.text,
    } as TextStyle,
    body: {
      fontSize: 16,
      color: colors.text,
    } as TextStyle,
    caption: {
      fontSize: 12,
      color: colors.placeholder,
    } as TextStyle,
  },
  shadows: {
    small: {
      shadowColor: colors.text,
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 2,
    } as ViewStyle,
    medium: {
      shadowColor: colors.text,
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.2,
      shadowRadius: 8,
      elevation: 4,
    } as ViewStyle,
  },
  components: {
    button: {
      primary: {
        backgroundColor: colors.primary,
        borderRadius: 8,
        paddingVertical: 12,
        paddingHorizontal: 24,
      },
      secondary: {
        backgroundColor: colors.surface,
        borderColor: colors.primary,
        borderWidth: 1,
        borderRadius: 8,
        paddingVertical: 12,
        paddingHorizontal: 24,
      },
    },
  },
};

export type Theme = typeof theme;
export default theme;