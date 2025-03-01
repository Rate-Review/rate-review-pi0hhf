import React from 'react';
import styled from 'styled-components';
import { useTheme } from '../../context/ThemeContext';
import { ErrorBoundary } from '../common/ErrorBoundary';
import { Card } from '../common/Card';
import { useWindowSize } from '../../hooks/useWindowSize';

/**
 * Interface defining props for AuthLayout component
 */
interface AuthLayoutProps {
  children: React.ReactNode;
  title?: string;
  showLogo?: boolean;
}

/**
 * Styled component for the main auth layout container
 */
const AuthContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  width: 100%;
  background-image: url('/assets/images/auth-background.jpg');
  background-size: cover;
  background-position: center;
  background-color: ${props => props.theme.palette.background.default};
  padding: ${props => props.theme.spacing(2)};
`;

/**
 * Styled component for the auth content card
 */
const AuthCard = styled(Card)`
  width: 100%;
  max-width: 450px;
  margin: ${props => props.theme.spacing(4)} auto;
  border-radius: ${props => props.theme.shape.borderRadius * 2}px;
  box-shadow: ${props => props.theme.shadows[3]};
  overflow: hidden;
  background-color: ${props => props.theme.palette.background.paper};
  
  @media (max-width: 600px) {
    max-width: 100%;
    margin: ${props => props.theme.spacing(2)} auto;
  }
`;

/**
 * Styled component for the logo area
 */
const LogoContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: ${props => props.theme.spacing(3)} 0;
  
  img {
    max-width: 180px;
    height: auto;
  }
  
  @media (max-width: 600px) {
    padding: ${props => props.theme.spacing(2)} 0;
    
    img {
      max-width: 150px;
    }
  }
`;

/**
 * Styled component for the auth page title
 */
const AuthTitle = styled.h1`
  font-family: ${props => props.theme.typography.fontFamily};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  font-size: ${props => props.theme.typography.h4.fontSize};
  text-align: center;
  color: ${props => props.theme.palette.text.primary};
  margin-top: 0;
  margin-bottom: ${props => props.theme.spacing(3)};
  
  @media (max-width: 600px) {
    font-size: ${props => props.theme.typography.h5.fontSize};
    margin-bottom: ${props => props.theme.spacing(2)};
  }
`;

/**
 * Styled component for the auth form content area
 */
const AuthContent = styled.div`
  padding: ${props => props.theme.spacing(0, 3, 4)};
  
  @media (max-width: 600px) {
    padding: ${props => props.theme.spacing(0, 2, 3)};
  }
`;

/**
 * Layout component for authentication pages that provides a consistent, branded experience
 * 
 * @param {React.ReactNode} children - Content to be rendered within the auth layout
 * @param {string} title - Optional title to be displayed above the content
 * @param {boolean} showLogo - Whether to show the logo, defaults to true
 * @returns {JSX.Element} Rendered layout component
 */
const AuthLayout: React.FC<AuthLayoutProps> = ({ 
  children, 
  title, 
  showLogo = true 
}) => {
  const { theme } = useTheme();
  const { width } = useWindowSize();
  
  const isMobile = width < 600;
  
  return (
    <AuthContainer>
      <AuthCard variant="elevated" padding={0}>
        {showLogo && (
          <LogoContainer>
            <img 
              src="/assets/images/logo.svg" 
              alt="Justice Bid" 
              width={isMobile ? 150 : 180} 
              height="auto"
            />
          </LogoContainer>
        )}
        
        <AuthContent>
          {title && <AuthTitle>{title}</AuthTitle>}
          
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </AuthContent>
      </AuthCard>
    </AuthContainer>
  );
};

export default AuthLayout;