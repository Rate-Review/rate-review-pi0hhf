import React, { Component, ErrorInfo, ReactNode } from 'react';
import Alert from '../common/Alert';
import Button from '../common/Button';

/**
 * Interface defining the props for the ErrorBoundary component
 */
interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode | ((error: Error) => ReactNode);
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetOnChange?: boolean;
}

/**
 * Interface defining the state for the ErrorBoundary component
 */
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * Component that catches errors in its child component tree and displays a fallback UI 
 * instead of crashing the whole application
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null
    };
  }

  /**
   * React static lifecycle method that updates state when an error is caught
   */
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  /**
   * Lifecycle method called after an error has been thrown in a descendant component
   */
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log the error to console or error tracking service
    console.error('Error caught by ErrorBoundary:', error);
    console.error('Component stack trace:', errorInfo.componentStack);
    
    // Call the onError prop if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  /**
   * Lifecycle method called after component updates
   */
  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    // If resetOnChange is true and children have changed, reset the error state
    if (
      this.props.resetOnChange &&
      this.state.hasError &&
      prevProps.children !== this.props.children
    ) {
      this.reset();
    }
  }

  /**
   * Method to reset the error state and allow the component to try rendering again
   */
  reset = () => {
    this.setState({
      hasError: false,
      error: null
    });
  };

  /**
   * Renders either the fallback UI when an error occurs or the children components
   */
  render() {
    if (this.state.hasError) {
      // If a custom fallback is provided
      if (this.props.fallback) {
        // If fallback is a function, call it with the error
        if (typeof this.props.fallback === 'function') {
          return this.props.fallback(this.state.error!);
        }
        // Otherwise, just render the fallback
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <Alert 
          severity="error"
          title="Something went wrong"
          message="An error occurred while rendering this component. You can try again or contact support if the problem persists."
          action={
            <Button 
              variant="outline" 
              size="small" 
              onClick={this.reset}
              aria-label="Try again"
            >
              Try again
            </Button>
          }
        />
      );
    }

    // No error, render children normally
    return this.props.children;
  }
}

export default ErrorBoundary;