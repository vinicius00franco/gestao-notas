import { TextStyle, ViewStyle } from 'react-native';

const palette = {
  blue: '#2563eb',
  white: '#ffffff',
  black: '#111827',
  gray: '#6b7280',
  red: '#dc2626',
  green: '#16a34a',
  lightGray: '#f3f4f6',
};

const theme = {
  colors: {
    primary: palette.blue,
    background: palette.white,
    text: palette.black,
    muted: palette.gray,
    danger: palette.red,
    success: palette.green,
    border: palette.lightGray,
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
      color: palette.black,
    } as TextStyle,
    h2: {
      fontSize: 24,
      fontWeight: 'bold',
      color: palette.black,
    } as TextStyle,
    body: {
      fontSize: 16,
      color: palette.black,
    } as TextStyle,
    caption: {
      fontSize: 12,
      color: palette.gray,
    } as TextStyle,
  },
  shadows: {
    small: {
      shadowColor: palette.black,
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 2,
    } as ViewStyle,
    medium: {
      shadowColor: palette.black,
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.2,
      shadowRadius: 8,
      elevation: 4,
    } as ViewStyle,
  },
  components: {
    button: {
      primary: {
        backgroundColor: palette.blue,
        borderRadius: 8,
        paddingVertical: 12,
        paddingHorizontal: 24,
      },
      secondary: {
        backgroundColor: palette.white,
        borderColor: palette.blue,
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