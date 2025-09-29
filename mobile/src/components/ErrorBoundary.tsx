import React from 'react';
import { View, Text } from 'react-native';

type Props = { children: React.ReactNode };
type State = { hasError: boolean; message?: string };

export default class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError(error: any) {
    return { hasError: true, message: String(error) };
  }
  componentDidCatch(error: any) {
    console.error('ErrorBoundary', error);
  }
  render() {
    if (this.state.hasError) {
      return (
        <View style={{ padding: 16 }}>
          <Text>Ocorreu um erro inesperado.</Text>
          {this.state.message && <Text style={{ color: 'red' }}>{this.state.message}</Text>}
        </View>
      );
    }
    return this.props.children;
  }
}
