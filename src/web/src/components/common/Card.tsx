import React from 'react';
import styled from 'styled-components';

// Props interfaces
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'outlined' | 'elevated' | 'flat';
  padding?: string | number;
  width?: string | number;
  height?: string | number;
  onClick?: () => void;
  className?: string;
  children: React.ReactNode;
}

interface CardHeaderProps {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
  children?: React.ReactNode;
}

interface CardContentProps {
  padding?: string | number;
  className?: string;
  children: React.ReactNode;
}

interface CardFooterProps {
  className?: string;
  children: React.ReactNode;
}

// Styled components
const StyledCard = styled.div<{
  variant?: 'outlined' | 'elevated' | 'flat';
  padding?: string | number;
  width?: string | number;
  height?: string | number;
  clickable?: boolean;
}>`
  background-color: ${props => props.theme.colors?.background || '#FFFFFF'};
  border-radius: ${props => props.theme.borderRadius?.md || '4px'};
  padding: ${props => props.padding || props.theme.spacing?.md || '16px'};
  width: ${props => props.width || 'auto'};
  height: ${props => props.height || 'auto'};
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  
  ${props => {
    const borderWidth = props.theme.borderWidth || '1px';
    const borderColor = props.theme.colors?.border || '#E2E8F0';
    const shadowMd = props.theme.shadows?.md || '0 4px 6px rgba(0, 0, 0, 0.1)';
    
    switch (props.variant) {
      case 'outlined':
        return `
          border: ${borderWidth} solid ${borderColor};
          box-shadow: none;
        `;
      case 'elevated':
        return `
          border: none;
          box-shadow: ${shadowMd};
        `;
      case 'flat':
      default:
        return `
          border: none;
          box-shadow: none;
        `;
    }
  }}
  
  ${props => {
    if (props.clickable) {
      const transition = props.theme.transitions?.normal || '250ms ease-in-out';
      const shadowLg = props.theme.shadows?.lg || '0 10px 15px rgba(0, 0, 0, 0.1)';
      
      return `
        cursor: pointer;
        transition: transform ${transition}, box-shadow ${transition};
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: ${shadowLg};
        }
      `;
    }
    return '';
  }}
`;

const StyledCardHeader = styled.div`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding-bottom: ${props => props.theme.spacing?.md || '16px'};
`;

const HeaderContent = styled.div`
  flex: 1;
`;

const HeaderTitle = styled.h3`
  margin: 0;
  color: ${props => props.theme.colors?.text?.primary || '#2C5282'};
  font-size: ${props => props.theme.typography?.fontSize?.lg || '18px'};
  font-weight: ${props => props.theme.typography?.fontWeight?.medium || '500'};
`;

const HeaderSubtitle = styled.h4`
  margin: ${props => `${props.theme.spacing?.xs || '4px'} 0 0 0`};
  color: ${props => props.theme.colors?.text?.secondary || '#718096'};
  font-size: ${props => props.theme.typography?.fontSize?.md || '16px'};
  font-weight: ${props => props.theme.typography?.fontWeight?.normal || '400'};
`;

const HeaderAction = styled.div`
  margin-left: ${props => props.theme.spacing?.md || '16px'};
`;

const StyledCardContent = styled.div<{ padding?: string | number }>`
  flex: 1;
  padding: ${props => props.padding || `0 0 ${props.theme.spacing?.md || '16px'} 0`};
`;

const StyledCardFooter = styled.div`
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-top: ${props => props.theme.spacing?.md || '16px'};
  border-top: ${props => `${props.theme.borderWidth || '1px'} solid ${props.theme.colors?.border || '#E2E8F0'}`};
`;

/**
 * Card Header component to display title, subtitle, and optional actions
 */
const CardHeader: React.FC<CardHeaderProps> = ({
  title,
  subtitle,
  action,
  className,
  children,
}) => {
  if (children) {
    return <StyledCardHeader className={className}>{children}</StyledCardHeader>;
  }

  return (
    <StyledCardHeader className={className}>
      <HeaderContent>
        {title && <HeaderTitle>{title}</HeaderTitle>}
        {subtitle && <HeaderSubtitle>{subtitle}</HeaderSubtitle>}
      </HeaderContent>
      {action && <HeaderAction>{action}</HeaderAction>}
    </StyledCardHeader>
  );
};

/**
 * Card Content component to contain the main content of the card
 */
const CardContent: React.FC<CardContentProps> = ({
  padding,
  className,
  children,
}) => {
  return (
    <StyledCardContent padding={padding} className={className}>
      {children}
    </StyledCardContent>
  );
};

/**
 * Card Footer component to display actions or other content at the bottom of the card
 */
const CardFooter: React.FC<CardFooterProps> = ({
  className,
  children,
}) => {
  return (
    <StyledCardFooter className={className}>
      {children}
    </StyledCardFooter>
  );
};

/**
 * Main Card component that serves as a container for content.
 * Can be used with CardHeader, CardContent, and CardFooter or with custom content.
 */
const Card: React.FC<CardProps> = ({
  variant = 'elevated',
  padding,
  width,
  height,
  onClick,
  className,
  children,
  ...rest
}) => {
  return (
    <StyledCard
      variant={variant}
      padding={padding}
      width={width}
      height={height}
      clickable={!!onClick}
      className={className}
      onClick={onClick}
      {...rest}
    >
      {children}
    </StyledCard>
  );
};

export { CardHeader, CardContent, CardFooter, Card };
export default Card;