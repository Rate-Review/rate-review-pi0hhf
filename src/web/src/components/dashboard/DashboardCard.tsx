import React from 'react';
import { Box, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';
import Card from '../common/Card';

// Define the props interface
interface DashboardCardProps {
  title: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
  minHeight?: number;
  noPadding?: boolean;
  fullHeight?: boolean;
}

// Create styled components
const StyledCard = styled(Card)<{ minHeight?: number; noPadding?: boolean; fullHeight?: boolean }>`
  height: ${props => props.fullHeight ? '100%' : 'auto'};
  min-height: ${props => props.minHeight ? `${props.minHeight}px` : 'auto'};
  display: flex;
  flex-direction: column;
  margin-bottom: ${({ theme }) => theme.spacing(3)};
`;

const CardHeader = styled(Box)`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: ${({ theme }) => theme.spacing(2)};
`;

const CardContent = styled(Box)<{ noPadding?: boolean }>`
  flex: 1;
  ${props => props.noPadding ? 'padding: 0;' : ''}
`;

/**
 * A reusable card component for dashboard elements that provides consistent styling and structure
 */
const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  children,
  actions,
  minHeight,
  noPadding = false,
  fullHeight = false,
}) => {
  return (
    <StyledCard 
      variant="elevated"
      padding={noPadding ? 0 : undefined}
      minHeight={minHeight}
      fullHeight={fullHeight}
    >
      <CardHeader>
        <Typography variant="h6" color="primary">
          {title}
        </Typography>
        {actions && (
          <Box>
            {actions}
          </Box>
        )}
      </CardHeader>
      <CardContent noPadding={noPadding}>
        {children}
      </CardContent>
    </StyledCard>
  );
};

export default DashboardCard;