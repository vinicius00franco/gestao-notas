import React, { Component, ErrorInfo, ReactNode } from 'react';
import ErrorScreen from '../screens/ErrorScreen';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

class DefaultErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(_: Error): State {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false });
  };

  public render() {
    if (this.state.hasError) {
      return <ErrorScreen onRetry={this.handleReset} />;
    }

    return this.props.children;
  }
}

export default DefaultErrorBoundary;