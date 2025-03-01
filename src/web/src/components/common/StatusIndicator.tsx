/**
 * StatusIndicator.tsx
 * 
 * A reusable component that visually represents status information with appropriate styling
 * and colors based on the status type. Used throughout the application to indicate various
 * states of negotiations, rates, approvals, and other processes.
 */

import React from 'react';
import styled from 'styled-components';
import theme from '../../theme'; // React 18.0.0

/**
 * Enum for available status indicator sizes
 */
export enum StatusSize {
  SMALL = 'small',
  MEDIUM = 'medium',
  LARGE = 'large',
}

/**
 * Props interface for the StatusIndicator component
 */
export interface StatusIndicatorProps {
  status: string;                       // The status value to display
  label?: string;                       // Optional custom label (if not provided, uses the status)
  size?: StatusSize;                    // Size of the indicator
  showDot?: boolean;                    // Whether to show a colored dot
  showLabel?: boolean;                  // Whether to show the text label
  statusColorMap?: Record<string, string>; // Custom mapping of status to colors
  className?: string;                   // Custom class name
  style?: React.CSSProperties;          // Custom inline styles
}

/**
 * Determines the appropriate color for a given status
 * 
 * @param status - The status value
 * @param colorMap - Custom mapping of status to colors
 * @returns The color code to use for the status
 */
const getStatusColor = (status: string, colorMap: Record<string, string>): string => {
  // Check if status exists in the provided color map
  if (status in colorMap) {
    return colorMap[status];
  }

  // Default color mapping based on common status keywords
  const lowerStatus = status.toLowerCase();
  
  if (lowerStatus.includes('approved') || lowerStatus.includes('active') || 
      lowerStatus.includes('completed') || lowerStatus.includes('success')) {
    return theme.colors.success.main;
  }
  
  if (lowerStatus.includes('rejected') || lowerStatus.includes('failed') || 
      lowerStatus.includes('error')) {
    return theme.colors.error.main;
  }
  
  if (lowerStatus.includes('pending') || lowerStatus.includes('waiting') || 
      lowerStatus.includes('in progress')) {
    return theme.colors.info.main;
  }
  
  if (lowerStatus.includes('draft') || lowerStatus.includes('saved')) {
    return theme.colors.neutral.main;
  }
  
  if (lowerStatus.includes('warning') || lowerStatus.includes('caution') ||
      lowerStatus.includes('counterproposed')) {
    return theme.colors.warning.main;
  }
  
  // Default color if no matches
  return theme.colors.primary.main;
};

/**
 * Styled container for the status indicator
 */
const StatusContainer = styled.div<{ size: StatusSize }>`
  display: flex;
  align-items: center;
  gap: ${props => props.size === StatusSize.SMALL ? '4px' : 
               props.size === StatusSize.MEDIUM ? '6px' : '8px'};
`;

/**
 * Styled dot element for visual status indication
 */
const StatusDot = styled.div<{ color: string; size: StatusSize }>`
  width: ${props => props.size === StatusSize.SMALL ? '8px' : 
               props.size === StatusSize.MEDIUM ? '10px' : '12px'};
  height: ${props => props.size === StatusSize.SMALL ? '8px' : 
                props.size === StatusSize.MEDIUM ? '10px' : '12px'};
  border-radius: 50%;
  background-color: ${props => props.color};
  flex-shrink: 0;
`;

/**
 * Styled text element for the status label
 */
const StatusText = styled.span<{ color: string; size: StatusSize }>`
  font-size: ${props => props.size === StatusSize.SMALL ? '0.75rem' : 
                   props.size === StatusSize.MEDIUM ? '0.875rem' : '1rem'};
  font-weight: ${props => props.size === StatusSize.SMALL ? '400' : '500'};
  color: ${props => props.color};
`;

/**
 * StatusIndicator component for displaying status information with appropriate visual styling
 * 
 * @param props - Component props
 * @returns Rendered status indicator component
 */
const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  size = StatusSize.MEDIUM,
  showDot = true,
  showLabel = true,
  statusColorMap = {},
  className,
  style,
}) => {
  // Define default status color mapping for common statuses
  const defaultStatusColorMap: Record<string, string> = {
    'Approved': theme.colors.success.main,
    'Rejected': theme.colors.error.main,
    'Pending': theme.colors.info.main,
    'Draft': theme.colors.neutral.main,
    'In Progress': theme.colors.info.main,
    'Completed': theme.colors.success.main,
    'Submitted': theme.colors.primary.main,
    'UnderReview': theme.colors.info.main,
    'CounterProposed': theme.colors.warning.main,
    'Expired': theme.colors.neutral.dark,
  };
  
  // Merge default mapping with any custom mapping provided via props
  const mergedColorMap = { ...defaultStatusColorMap, ...statusColorMap };
  
  // Determine color for the given status
  const statusColor = getStatusColor(status, mergedColorMap);
  
  // Determine display text (use provided label or capitalize the status)
  const displayText = label || status.charAt(0).toUpperCase() + status.slice(1);
  
  return (
    <StatusContainer 
      size={size} 
      className={className} 
      style={style}
    >
      {showDot && <StatusDot color={statusColor} size={size} />}
      {showLabel && <StatusText color={statusColor} size={size}>{displayText}</StatusText>}
    </StatusContainer>
  );
};

export default StatusIndicator;