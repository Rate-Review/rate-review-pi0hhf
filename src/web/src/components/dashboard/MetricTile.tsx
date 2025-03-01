import React from 'react';
import { Box, Typography, Tooltip } from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { formatCurrency, formatPercentage, formatNumber } from '../../utils/formatting';
import colors from '../../theme/colors';

/**
 * Props interface for the MetricTile component
 */
interface MetricTileProps {
  /** Label text for the metric */
  label: string;
  /** The primary value to display */
  value: number | string;
  /** Optional secondary value to display below the primary value */
  secondaryValue?: number | string;
  /** Format type for the value display */
  format?: 'currency' | 'percentage' | 'number';
  /** Currency code for currency format (e.g., USD, EUR) */
  currencyCode?: string;
  /** Whether to show trend indicator */
  showTrend?: boolean;
  /** Previous value for trend calculation */
  previousValue?: number;
  /** Text to show in tooltip on hover */
  tooltipText?: string;
  /** Override for positive trend direction */
  positive?: boolean;
  /** Invert the meaning of up/down trend (e.g., for costs) */
  inverse?: boolean;
  /** Size variant for the tile */
  size?: 'small' | 'medium' | 'large';
  /** Optional CSS class name */
  className?: string;
}

// Styled components for consistent visual presentation
const Container = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  padding: theme.spacing(2),
  height: '100%',
  '&.small': {
    padding: theme.spacing(1),
  },
  '&.large': {
    padding: theme.spacing(3),
  },
}));

const LabelWrapper = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(1),
}));

const ValueWrapper = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  '&.small': {
    '& .primary-value': {
      fontSize: '1.25rem',
      fontWeight: 500,
    },
    '& .secondary-value': {
      fontSize: '0.875rem',
    },
  },
  '&.medium': {
    '& .primary-value': {
      fontSize: '1.5rem',
      fontWeight: 600,
    },
    '& .secondary-value': {
      fontSize: '1rem',
    },
  },
  '&.large': {
    '& .primary-value': {
      fontSize: '2rem',
      fontWeight: 700,
    },
    '& .secondary-value': {
      fontSize: '1.125rem',
    },
  },
}));

const TrendIndicator = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  marginLeft: theme.spacing(1),
  fontWeight: 500,
  fontSize: '0.875rem',
  '& svg': {
    fontSize: '1rem',
    marginRight: theme.spacing(0.5),
  },
}));

/**
 * Formats the numerical value based on the specified format type
 * 
 * @param value - The value to format
 * @param format - The format type
 * @param currencyCode - Currency code for currency formatting
 * @returns Formatted value as string
 */
const formatValue = (
  value: number | string,
  format: string = 'number',
  currencyCode: string = 'USD'
): string => {
  // If value is already a string, return as is
  if (typeof value === 'string') {
    return value;
  }

  // Format based on type
  switch (format) {
    case 'currency':
      return formatCurrency(value, currencyCode);
    case 'percentage':
      return formatPercentage(value);
    case 'number':
    default:
      return formatNumber(value);
  }
};

/**
 * Determines the color for trend indicators based on the trend direction and inverse setting
 * 
 * @param isPositiveTrend - Whether the trend is positive
 * @param inverse - Whether to invert the color logic
 * @returns Color code from theme
 */
const getTrendColor = (isPositiveTrend: boolean, inverse: boolean = false): string => {
  // Determine if the trend should be considered positive
  const isPositive = inverse ? !isPositiveTrend : isPositiveTrend;
  
  // Return appropriate color
  return isPositive ? colors.success.main : colors.error.main;
};

/**
 * A component that displays a formatted metric with a label and optional trend indicator
 * Used throughout the dashboard for displaying key metrics and KPIs
 * 
 * @param props - Component props
 * @returns Rendered metric tile component
 */
const MetricTile: React.FC<MetricTileProps> = ({
  label,
  value,
  secondaryValue,
  format = 'number',
  currencyCode = 'USD',
  showTrend = false,
  previousValue,
  tooltipText,
  positive,
  inverse = false,
  size = 'medium',
  className,
}) => {
  // Format the primary value
  const formattedValue = formatValue(value, format, currencyCode);
  
  // Format the secondary value if provided
  const formattedSecondaryValue = secondaryValue
    ? formatValue(secondaryValue, format, currencyCode)
    : undefined;
  
  // Determine trend direction if applicable
  const isTrendPositive = positive !== undefined
    ? positive
    : previousValue !== undefined && typeof value === 'number'
      ? value > previousValue
      : false;
  
  // Calculate percentage change if possible
  let percentChange: string | undefined;
  if (previousValue !== undefined && typeof value === 'number' && previousValue !== 0) {
    const changeValue = ((value - previousValue) / Math.abs(previousValue)) * 100;
    percentChange = `${changeValue > 0 ? '+' : ''}${formatPercentage(changeValue / 100)}`;
  }
  
  // Get color for trend indicator
  const trendColor = getTrendColor(isTrendPositive, inverse);

  // Render the component
  const content = (
    <Container className={`${size} ${className || ''}`}>
      <LabelWrapper>
        <Typography
          variant="body2"
          color="textSecondary"
          component="div"
        >
          {label}
        </Typography>
      </LabelWrapper>
      <ValueWrapper className={size}>
        <Typography
          className="primary-value"
          variant={size === 'large' ? 'h4' : size === 'medium' ? 'h5' : 'h6'}
          component="div"
        >
          {formattedValue}
        </Typography>
        
        {showTrend && previousValue !== undefined && (
          <TrendIndicator sx={{ color: trendColor }}>
            {isTrendPositive ? <TrendingUp /> : <TrendingDown />}
            {percentChange && <span>{percentChange}</span>}
          </TrendIndicator>
        )}
      </ValueWrapper>
      
      {formattedSecondaryValue && (
        <Typography
          className="secondary-value"
          variant="body2"
          color="textSecondary"
          component="div"
          sx={{ mt: 0.5 }}
        >
          {formattedSecondaryValue}
        </Typography>
      )}
    </Container>
  );

  // Wrap with tooltip if tooltip text is provided
  return tooltipText ? (
    <Tooltip title={tooltipText} arrow>
      {content}
    </Tooltip>
  ) : content;
};

export default MetricTile;