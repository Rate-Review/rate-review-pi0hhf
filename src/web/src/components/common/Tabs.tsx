import React, { useEffect, useRef, useState } from 'react';
import styled, { css } from 'styled-components';
import { useWindowSize } from '../../../hooks/useWindowSize';

// Define the TabItem interface for individual tab items
export interface TabItem {
  id: string | number;
  label: string | React.ReactNode;
  icon?: React.ReactNode;
  disabled?: boolean;
}

// Define the props interface for the Tabs component
export interface TabsProps {
  /**
   * Array of tab items to display
   */
  tabs: TabItem[];
  
  /**
   * ID of the currently active tab
   */
  activeTab: string | number;
  
  /**
   * Callback function when a tab is selected
   */
  onChange: (tabId: string | number) => void;
  
  /**
   * Orientation of the tabs - horizontal or vertical
   * @default 'horizontal'
   */
  orientation?: 'horizontal' | 'vertical';
  
  /**
   * Visual style variant of the tabs
   * @default 'default'
   */
  variant?: 'default' | 'contained' | 'outlined';
  
  /**
   * Size of the tabs
   * @default 'medium'
   */
  size?: 'small' | 'medium' | 'large';
  
  /**
   * Whether tabs should take full width of the container
   * @default false
   */
  fullWidth?: boolean;
  
  /**
   * Additional CSS class name
   */
  className?: string;
}

// Define interface for the active indicator's style
interface IndicatorStyle {
  left?: string;
  top?: string;
  width?: string;
  height?: string;
  transform?: string;
}

// Styled components for the tabs
const TabsContainer = styled.div<{
  orientation?: 'horizontal' | 'vertical';
  variant?: 'default' | 'contained' | 'outlined';
}>`
  display: flex;
  position: relative;
  flex-direction: ${props => props.orientation === 'vertical' ? 'column' : 'row'};
  
  ${props => props.variant === 'contained' && css`
    background-color: #F7FAFC;
    border-radius: 4px;
    padding: 4px;
  `}
  
  ${props => props.variant === 'outlined' && css`
    border: 1px solid #E2E8F0;
    border-radius: 4px;
    padding: 4px;
  `}
`;

const TabList = styled.div<{
  orientation?: 'horizontal' | 'vertical';
  fullWidth?: boolean;
}>`
  display: flex;
  flex-direction: ${props => props.orientation === 'vertical' ? 'column' : 'row'};
  ${props => props.fullWidth && props.orientation !== 'vertical' && css`
    width: 100%;
  `}
`;

const TabItem = styled.button<{
  active: boolean;
  disabled?: boolean;
  size?: 'small' | 'medium' | 'large';
  orientation?: 'horizontal' | 'vertical';
  fullWidth?: boolean;
  variant?: 'default' | 'contained' | 'outlined';
}>`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: ${props => {
    switch (props.size) {
      case 'small': return '8px 16px';
      case 'large': return '16px 32px';
      default: return '12px 24px';
    }
  }};
  background: none;
  border: none;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  opacity: ${props => props.disabled ? 0.5 : 1};
  font-weight: ${props => props.active ? '500' : '400'};
  color: ${props => props.active ? '#2C5282' : '#718096'};
  position: relative;
  transition: all 0.3s ease;
  outline: none;
  white-space: nowrap;
  
  ${props => props.fullWidth && props.orientation !== 'vertical' && css`
    flex: 1;
  `}
  
  ${props => props.variant === 'contained' && css`
    border-radius: 4px;
    ${props.active && css`
      background-color: #EBF8FF;
    `}
  `}
  
  ${props => props.variant === 'outlined' && css`
    border-radius: 4px;
    ${props.active && css`
      background-color: #EBF8FF;
      border: 1px solid #90CDF4;
    `}
  `}
  
  &:hover {
    color: ${props => props.disabled ? '#718096' : '#2C5282'};
    background-color: ${props => {
      if (props.disabled) return 'transparent';
      return props.variant === 'default' ? 'transparent' : '#F7FAFC';
    }};
  }
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(66, 153, 225, 0.5);
  }
`;

const TabIcon = styled.span`
  margin-right: 8px;
  display: flex;
  align-items: center;
`;

const ActiveIndicator = styled.div<{
  style?: React.CSSProperties;
  orientation?: 'horizontal' | 'vertical';
  variant?: 'default' | 'contained' | 'outlined';
}>`
  position: absolute;
  background-color: ${props => props.variant === 'default' ? '#3182CE' : 'transparent'};
  transition: all 0.3s ease;
  
  ${props => props.variant === 'default' && props.orientation === 'horizontal' && css`
    height: 2px;
    bottom: 0;
  `}
  
  ${props => props.variant === 'default' && props.orientation === 'vertical' && css`
    width: 2px;
    right: 0;
  `}
`;

/**
 * A customizable tab navigation component that supports horizontal and vertical orientations
 * with various visual styles. The component provides a consistent navigation pattern for
 * switching between different content sections across the application.
 *
 * @param {TabsProps} props - The component props
 * @returns {React.ReactElement} The rendered Tabs component
 * 
 * @example
 * // Basic usage with horizontal tabs
 * <Tabs
 *   tabs={[
 *     { id: 'tab1', label: 'Dashboard' },
 *     { id: 'tab2', label: 'Rates' },
 *     { id: 'tab3', label: 'Negotiations' }
 *   ]}
 *   activeTab="tab1"
 *   onChange={(tabId) => setActiveTab(tabId)}
 * />
 * 
 * @example
 * // Vertical tabs with icons
 * <Tabs
 *   orientation="vertical"
 *   variant="outlined"
 *   tabs={[
 *     { id: 'tab1', label: 'Dashboard', icon: <DashboardIcon /> },
 *     { id: 'tab2', label: 'Rates', icon: <RatesIcon /> },
 *     { id: 'tab3', label: 'Negotiations', icon: <NegotiationsIcon /> }
 *   ]}
 *   activeTab="tab1"
 *   onChange={(tabId) => setActiveTab(tabId)}
 * />
 */
const Tabs: React.FC<TabsProps> = ({
  tabs,
  activeTab,
  onChange,
  orientation = 'horizontal',
  variant = 'default',
  size = 'medium',
  fullWidth = false,
  className,
}) => {
  // Create a reference to the tabs container
  const tabsRef = useRef<HTMLDivElement>(null);
  
  // Use window size hook to detect screen size changes for responsive behavior
  const windowSize = useWindowSize();
  
  // State for the active indicator style
  const [indicatorStyle, setIndicatorStyle] = useState<IndicatorStyle>({});

  // Function to update the indicator position based on the active tab
  const updateIndicator = () => {
    if (!tabsRef.current) return;
    
    const activeTabElement = tabsRef.current.querySelector(`[data-tab-id="${activeTab}"]`) as HTMLElement;
    
    if (!activeTabElement) return;
    
    if (orientation === 'horizontal') {
      setIndicatorStyle({
        left: `${activeTabElement.offsetLeft}px`,
        width: `${activeTabElement.offsetWidth}px`,
        transform: 'none',
      });
    } else {
      setIndicatorStyle({
        top: `${activeTabElement.offsetTop}px`,
        height: `${activeTabElement.offsetHeight}px`,
        transform: 'none',
      });
    }
  };

  // Update indicator when active tab changes
  useEffect(() => {
    updateIndicator();
  }, [activeTab]);

  // Update indicator when window size changes or tabs change
  useEffect(() => {
    updateIndicator();
  }, [windowSize, tabs, orientation]);

  // Tab click handler
  const handleTabClick = (tab: TabItem) => {
    if (tab.disabled) return;
    onChange(tab.id);
  };

  return (
    <TabsContainer
      ref={tabsRef}
      orientation={orientation}
      variant={variant}
      className={className}
    >
      <TabList orientation={orientation} fullWidth={fullWidth}>
        {tabs.map((tab) => (
          <TabItem
            key={tab.id}
            data-tab-id={tab.id}
            active={activeTab === tab.id}
            disabled={tab.disabled}
            size={size}
            orientation={orientation}
            fullWidth={fullWidth}
            variant={variant}
            onClick={() => handleTabClick(tab)}
            aria-selected={activeTab === tab.id}
            role="tab"
          >
            {tab.icon && <TabIcon>{tab.icon}</TabIcon>}
            {tab.label}
          </TabItem>
        ))}
      </TabList>
      
      {variant === 'default' && (
        <ActiveIndicator
          style={indicatorStyle as React.CSSProperties}
          orientation={orientation}
          variant={variant}
        />
      )}
    </TabsContainer>
  );
};

export default Tabs;