import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import styled from 'styled-components';
import { useWindowSize } from '../../hooks/useWindowSize';
import { theme } from '../../theme';

interface TooltipProps {
  children: React.ReactNode;
  content: React.ReactNode;
  position?: 'top' | 'right' | 'bottom' | 'left';
  delay?: number;
  disabled?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const TooltipContainer = styled.div<{ visible: boolean; top: number; left: number; position: string; }>`
  position: absolute;
  top: ${props => `${props.top}px`};
  left: ${props => `${props.left}px`};
  background-color: ${props => props.theme.colors.neutral.dark};
  color: ${props => props.theme.colors.background.paper};
  padding: ${props => `${props.theme.spacing.xs}px ${props.theme.spacing.sm}px`};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.sm};
  max-width: 300px;
  z-index: 1000;
  opacity: ${props => props.visible ? 1 : 0};
  pointer-events: none;
  transition: opacity ${props => props.theme.transitions.normal};
  box-shadow: ${props => props.theme.shadows.md};
  &:after {
    content: '';
    position: absolute;
    
    ${props => props.position === 'top' && `
      bottom: -6px;
      left: 50%;
      transform: translateX(-50%);
      border-width: 6px 6px 0;
      border-style: solid;
      border-color: ${props.theme.colors.neutral.dark} transparent transparent;
    `}
    
    ${props => props.position === 'right' && `
      left: -6px;
      top: 50%;
      transform: translateY(-50%);
      border-width: 6px 6px 6px 0;
      border-style: solid;
      border-color: transparent ${props.theme.colors.neutral.dark} transparent transparent;
    `}
    
    ${props => props.position === 'bottom' && `
      top: -6px;
      left: 50%;
      transform: translateX(-50%);
      border-width: 0 6px 6px;
      border-style: solid;
      border-color: transparent transparent ${props.theme.colors.neutral.dark};
    `}
    
    ${props => props.position === 'left' && `
      right: -6px;
      top: 50%;
      transform: translateY(-50%);
      border-width: 6px 0 6px 6px;
      border-style: solid;
      border-color: transparent transparent transparent ${props.theme.colors.neutral.dark};
    `}
  }
`;

/**
 * Calculates the position of the tooltip based on the target element,
 * window size, and specified position.
 * 
 * @param targetRect - The bounding rectangle of the target element
 * @param position - The desired tooltip position ('top', 'right', 'bottom', 'left')
 * @param tooltipRect - The bounding rectangle of the tooltip element
 * @param windowSize - The current window dimensions
 * @returns The calculated position as {top, left} coordinates
 */
function calculatePosition(
  targetRect: DOMRect,
  position: string,
  tooltipRect: DOMRect,
  windowSize: { width: number; height: number }
): { top: number; left: number } {
  // Extract dimensions
  const targetWidth = targetRect.width;
  const targetHeight = targetRect.height;
  const tooltipWidth = tooltipRect.width;
  const tooltipHeight = tooltipRect.height;
  
  // Default offset to prevent tooltip from touching target
  const offset = 8;
  
  let top = 0;
  let left = 0;
  
  // Initial position calculation based on specified position
  switch (position) {
    case 'top':
      top = targetRect.top - tooltipHeight - offset;
      left = targetRect.left + (targetWidth / 2) - (tooltipWidth / 2);
      break;
    case 'right':
      top = targetRect.top + (targetHeight / 2) - (tooltipHeight / 2);
      left = targetRect.right + offset;
      break;
    case 'bottom':
      top = targetRect.bottom + offset;
      left = targetRect.left + (targetWidth / 2) - (tooltipWidth / 2);
      break;
    case 'left':
      top = targetRect.top + (targetHeight / 2) - (tooltipHeight / 2);
      left = targetRect.left - tooltipWidth - offset;
      break;
    default:
      top = targetRect.top - tooltipHeight - offset;
      left = targetRect.left + (targetWidth / 2) - (tooltipWidth / 2);
  }
  
  // Adjust position to ensure tooltip stays within viewport boundaries
  
  // Prevent left overflow
  if (left < 0) {
    left = Math.max(5, left);
  }
  
  // Prevent right overflow
  if (left + tooltipWidth > windowSize.width) {
    left = Math.min(windowSize.width - tooltipWidth - 5, left);
  }
  
  // Prevent top overflow
  if (top < 0) {
    // If tooltip is on top and overflows, move it to the bottom
    if (position === 'top') {
      top = targetRect.bottom + offset;
    } else {
      top = Math.max(5, top);
    }
  }
  
  // Prevent bottom overflow
  if (top + tooltipHeight > windowSize.height) {
    // If tooltip is on bottom and overflows, move it to the top
    if (position === 'bottom') {
      top = targetRect.top - tooltipHeight - offset;
    } else {
      top = Math.min(windowSize.height - tooltipHeight - 5, top);
    }
  }
  
  return { top, left };
}

/**
 * A reusable tooltip component that displays additional information when users
 * hover over or focus on an element. Supports multiple positions, follows accessibility
 * best practices, and integrates with the application's design system.
 * 
 * @param props - The component props
 * @returns The rendered tooltip component
 */
const Tooltip: React.FC<TooltipProps> = ({
  children,
  content,
  position = 'top',
  delay = 300,
  disabled = false,
  className,
  style
}) => {
  const [visible, setVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const targetRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<number | null>(null);
  const windowSize = useWindowSize();

  // Show tooltip after delay
  const handleMouseEnter = () => {
    if (disabled) return;
    
    if (timeoutRef.current) {
      window.clearTimeout(timeoutRef.current);
    }
    
    timeoutRef.current = window.setTimeout(() => {
      setVisible(true);
    }, delay);
  };

  // Hide tooltip and clear timeout
  const handleMouseLeave = () => {
    if (timeoutRef.current) {
      window.clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    
    setVisible(false);
  };

  // Handle keyboard focus for accessibility
  const handleFocus = () => {
    if (disabled) return;
    setVisible(true);
  };

  // Handle blur for accessibility
  const handleBlur = () => {
    setVisible(false);
  };

  // Calculate tooltip position when visibility changes
  useEffect(() => {
    if (visible && targetRef.current && tooltipRef.current) {
      const targetRect = targetRef.current.getBoundingClientRect();
      const tooltipRect = tooltipRef.current.getBoundingClientRect();
      
      const { top, left } = calculatePosition(
        targetRect,
        position,
        tooltipRect,
        {
          width: windowSize.width,
          height: windowSize.height
        }
      );
      
      setTooltipPosition({ top, left });
    }
  }, [visible, position, windowSize]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        window.clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return (
    <>
      <div
        ref={targetRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onFocus={handleFocus}
        onBlur={handleBlur}
        className={className}
        style={style}
      >
        {children}
      </div>
      
      {visible && createPortal(
        <TooltipContainer
          ref={tooltipRef}
          visible={visible}
          top={tooltipPosition.top}
          left={tooltipPosition.left}
          position={position}
          role="tooltip"
          aria-live="polite"
        >
          {content}
        </TooltipContainer>,
        document.body
      )}
    </>
  );
};

export default Tooltip;