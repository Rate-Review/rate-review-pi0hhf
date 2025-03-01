import React from 'react';
import styled from 'styled-components';
import Breadcrumbs from '../common/Breadcrumbs';
import { useWindowSize } from '../../hooks/useWindowSize';
import { colors } from '../../theme/colors';
import { spacing } from '../../theme/spacing';

/**
 * Interface defining the props for the PageHeader component
 */
export interface PageHeaderProps {
  /**
   * The title of the page
   */
  title: string;
  
  /**
   * Optional action elements to display in the header (buttons, controls, etc.)
   */
  actions?: React.ReactNode;
  
  /**
   * Optional breadcrumb items for navigation
   */
  breadcrumbs?: Array<{ label: string; path: string }>;
  
  /**
   * Whether to show breadcrumbs (defaults to true)
   */
  showBreadcrumbs?: boolean;
}

// Styled container for the header section
const Container = styled.div<{ isMobile: boolean }>`
  display: flex;
  flex-direction: column;
  width: 100%;
  margin-bottom: ${props => props.isMobile ? spacing.md : spacing.lg}px;
  padding-bottom: ${spacing.sm}px;
  border-bottom: 1px solid ${colors.divider};
`;

// Styled section for the page title and actions
const TitleSection = styled.div<{ isMobile: boolean }>`
  display: flex;
  flex-direction: ${props => props.isMobile ? 'column' : 'row'};
  justify-content: space-between;
  align-items: ${props => props.isMobile ? 'flex-start' : 'center'};
  margin-bottom: ${props => props.isMobile ? spacing.xs : spacing.sm}px;
  gap: ${props => props.isMobile ? spacing.sm : 0}px;
`;

// Styled heading element for the page title
const Title = styled.h1`
  font-size: ${props => props.theme.fontSize ? props.theme.fontSize.xl : '1.5rem'};
  font-weight: 500;
  color: ${colors.text.primary};
  margin: 0;
  padding: 0;
`;

// Styled section for action buttons/controls
const ActionsSection = styled.div<{ isMobile: boolean }>`
  display: flex;
  flex-wrap: wrap;
  gap: ${spacing.sm}px;
  justify-content: ${props => props.isMobile ? 'flex-start' : 'flex-end'};
  align-items: center;
  margin-top: ${props => props.isMobile ? spacing.xs : 0}px;
`;

// Styled section for breadcrumbs
const BreadcrumbsSection = styled.div`
  margin-bottom: ${spacing.sm}px;
`;

/**
 * React functional component that renders the page header with title, breadcrumbs, and actions
 * 
 * @param props - PageHeaderProps containing title, actions, breadcrumbs, and showBreadcrumbs flag
 * @returns Rendered page header component
 */
export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  actions,
  breadcrumbs,
  showBreadcrumbs = true
}) => {
  // Use the window size hook to determine if we're in mobile view
  const { width } = useWindowSize();
  const isMobile = width < 768;

  return (
    <Container isMobile={isMobile} data-testid="page-header">
      {showBreadcrumbs && breadcrumbs && breadcrumbs.length > 0 && (
        <BreadcrumbsSection>
          <Breadcrumbs custom={breadcrumbs} routes={[]} />
        </BreadcrumbsSection>
      )}
      
      <TitleSection isMobile={isMobile}>
        <Title>{title}</Title>
        
        {actions && (
          <ActionsSection isMobile={isMobile}>
            {actions}
          </ActionsSection>
        )}
      </TitleSection>
    </Container>
  );
};

export default PageHeader;