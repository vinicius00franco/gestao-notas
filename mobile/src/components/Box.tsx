import React, { ReactNode } from 'react';
import { View, ViewProps, StyleSheet } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';
import { Theme } from '../theme';

type Spacing = keyof Theme['spacing'];

interface BoxProps extends ViewProps {
  children?: ReactNode;
  m?: Spacing;
  p?: Spacing;
  mx?: Spacing;
  my?: Spacing;
  px?: Spacing;
  py?: Spacing;
  mt?: Spacing;
  mb?: Spacing;
  ml?: Spacing;
  mr?: Spacing;
  pt?: Spacing;
  pb?: Spacing;
  pl?: Spacing;
  pr?: Spacing;
}

export const Box = ({
  children,
  m,
  p,
  mx,
  my,
  px,
  py,
  mt,
  mb,
  ml,
  mr,
  pt,
  pb,
  pl,
  pr,
  style,
  ...rest
}: BoxProps) => {
  const theme = useTheme();

  const styles = StyleSheet.create({
    box: {
      margin: m ? theme.spacing[m] : undefined,
      padding: p ? theme.spacing[p] : undefined,
      marginHorizontal: mx ? theme.spacing[mx] : undefined,
      marginVertical: my ? theme.spacing[my] : undefined,
      paddingHorizontal: px ? theme.spacing[px] : undefined,
      paddingVertical: py ? theme.spacing[py] : undefined,
      marginTop: mt ? theme.spacing[mt] : undefined,
      marginBottom: mb ? theme.spacing[mb] : undefined,
      marginLeft: ml ? theme.spacing[ml] : undefined,
      marginRight: mr ? theme.spacing[mr] : undefined,
      paddingTop: pt ? theme.spacing[pt] : undefined,
      paddingBottom: pb ? theme.spacing[pb] : undefined,
      paddingLeft: pl ? theme.spacing[pl] : undefined,
      paddingRight: pr ? theme.spacing[pr] : undefined,
    },
  });

  return (
    <View style={[styles.box, style]} {...rest}>
      {children}
    </View>
  );
};