import React from 'react';
import DefaultErrorBoundary from './DefaultErrorBoundary';

const withErrorBoundary = <P extends object>(
  WrappedComponent: React.ComponentType<P>
): React.FC<P> => {
  const ComponentWithErrorBoundary: React.FC<P> = (props) => (
    <DefaultErrorBoundary>
      <WrappedComponent {...props} />
    </DefaultErrorBoundary>
  );

  // Set a display name for easier debugging
  const displayName =
    WrappedComponent.displayName || WrappedComponent.name || 'Component';
  ComponentWithErrorBoundary.displayName = `withErrorBoundary(${displayName})`;

  return ComponentWithErrorBoundary;
};

export default withErrorBoundary;