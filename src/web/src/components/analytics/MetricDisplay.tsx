import React from 'react'; // React: 18.0+
import { Box, Typography } from '@mui/material'; // @mui/material: 5.14+
import { ArrowUpward, ArrowDownward } from '@mui/icons-material'; // @mui/icons-material: 5.14+
import formatCurrency from '../../utils/currency';
import { formatPercentage } from '../../utils/formatting';
import Card from '../common/Card';
import Tooltip from '../common/Tooltip';

/**
 * Interface for the props of the MetricDisplay component
 */
interface MetricDisplayProps {
  label: string;
  value: number | null;
  format: 'currency' | 'percentage' | 'number';
  showTrend?: boolean;
  previousValue?: number;
  tooltipText?: string;
  variant?: 'standard' | 'compact';
  inverse?: boolean;
  className?: string;
}

/**
 * Formats the value based on the specified format type
 * @param value 
 * @param format 
 * @returns The formatted value
 */
const formatValue = (value: any, format: string): string => {
  switch (format) {
    case 'currency':
      return formatCurrency(value, 'USD'); // Assuming USD as default currency
    case 'percentage':
      return formatPercentage(value);
    case 'number':
      return value !== null ? value.toLocaleString() : '-';
    default:
      return value !== null ? value.toString() : '-';
  }
};

/**
 * Returns the appropriate trend icon based on value comparison
 * @param currentValue 
 * @param previousValue 
 * @param inverse 
 * @returns The trend icon component
 */
const getTrendIcon = (currentValue: number, previousValue: number, inverse?: boolean) => {
  const isIncreasing = currentValue > previousValue;
  const isPositiveTrend = inverse ? !isIncreasing : isIncreasing;

  if (isPositiveTrend) {
    return <ArrowUpward color="success" />;
  } else {
    return <ArrowDownward color="error" />;
  }
};

/**
 * Component for displaying analytics metrics with formatting and visual indicators
 * @param props 
 * @returns The rendered component
 */
const MetricDisplay: React.FC<MetricDisplayProps> = (props) => {
  const {
    label,
    value,
    format,
    showTrend,
    previousValue,
    tooltipText,
    variant = 'standard',
    inverse,
    className,
  } = props;

  const formattedValue = formatValue(value, format);
  const showTrendIndicator = showTrend && previousValue !== undefined;
  const trendIcon = showTrendIndicator ? getTrendIcon(value || 0, previousValue || 0, inverse) : null;

  return (
    <Card className={className}>
      <Box display="flex" flexDirection="column">
        <Typography variant="subtitle2" color="textSecondary" gutterBottom>
          {label}
          {tooltipText && (
            <Tooltip content={tooltipText}>
              <Box component="span" ml={0.5} fontSize="small" style={{ cursor: 'pointer' }}>
                {/* You can use an info icon here if desired */}
                (i)
              </Box>
            </Tooltip>
          )}
        </Typography>
        <Box display="flex" alignItems="center">
          <Typography variant={variant === 'compact' ? 'h6' : 'h5'} component="div">
            {formattedValue}
          </Typography>
          {showTrendIndicator && trendIcon}
        </Box>
      </Box>
    </Card>
  );
};

export default MetricDisplay;