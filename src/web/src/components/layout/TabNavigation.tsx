import React, { useMemo } from 'react'; //  ^18.0.0
import { Link, useLocation } from 'react-router-dom'; //  ^6.4.0
import { styled } from 'styled-components'; //  ^5.3.5

import { useAuth } from '../../hooks/useAuth';
import { usePermissions } from '../../hooks/usePermissions';
import { useWindowSize } from '../../hooks/useWindowSize';
import { ROUTES } from '../../constants/routes';
import { Badge } from '../common/Badge';

// Styled component for the navigation container
const NavContainer = styled.nav`
  display: flex;
  background-color: ${props => props.theme.colors.background};
  border-bottom: 1px solid ${props => props.theme.colors.border};
  padding: 0 ${props => props.theme.spacing.md}};
  height: 56px;
  align-items: center;
`;

// Styled component for the navigation tabs container
const NavTabs = styled.div`
  display: flex;
  height: 100%;
  align-items: center;
`;

// Styled component for individual navigation tabs
const NavTab = styled(Link)<{ active: boolean }>`
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 ${props => props.theme.spacing.md}};
  color: ${props => props.active ? props.theme.colors.primary : props.theme.colors.neutral};
  font-weight: ${props => props.active ? 500 : 400};
  position: relative;
  text-decoration: none;
  transition: color 0.2s ease-in-out;

  &:hover {
    color: ${props => props.theme.colors.primary};
  }
`;

// Styled component for the active tab indicator
const ActiveIndicator = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background-color: ${props => props.theme.colors.primary};
`;

// Interface for the TabNavigation component props
interface TabNavigationProps {
  notifications?: Record<string, number>;
}

// Interface for individual tab items
interface TabItem {
  id: string;
  label: string;
  path: string;
  icon?: React.ReactNode;
  requiredPermission?: string;
  roles?: string[];
}

/**
 * @function isRouteActive
 * @description Checks if a given route is active based on the current location path
 * @param {string} path - The route path to check
 * @param {string} currentPath - The current location path
 * @returns {boolean} True if the route is active, false otherwise
 */
const isRouteActive = (path: string, currentPath: string): boolean => {
  // Compare the given path with the current path
  // Return true if the current path starts with the given path and either they're equal or the given path is not '/'
  return currentPath.startsWith(path) && (currentPath === path || path !== '/');
};

/**
 * @function TabNavigation
 * @description A tab-based navigation component that displays different tabs based on user role and permissions
 * @param {TabNavigationProps} props - The component props
 * @returns {JSX.Element} Rendered navigation component
 */
const TabNavigation: React.FC<TabNavigationProps> = (props) => {
  // IE1: Destructure notifications from props with default empty object
  const { notifications = {} } = props;

  // IE1: Get current location using useLocation hook
  const location = useLocation();

  // IE1: Get user role and authentication state using useAuth hook
  const { userRole } = useAuth();

  // IE1: Get user permissions using usePermissions hook
  const { can } = usePermissions();

  // IE1: Get window dimensions using useWindowSize hook
  const { width } = useWindowSize();

  // IE1: Define tabs configuration using useMemo with dependencies on role and permissions
  const tabs: TabItem[] = useMemo(() => {
    // IE1: Create tabs for Dashboard, Rates, Negotiations, Analytics, Messages, and Settings
    let initialTabs: TabItem[] = [
      { id: 'dashboard', label: 'Dashboard', path: ROUTES.CLIENT_DASHBOARD },
      { id: 'rates', label: 'Rates', path: ROUTES.RATE_REQUESTS },
      { id: 'negotiations', label: 'Negotiations', path: ROUTES.NEGOTIATIONS },
      { id: 'analytics', label: 'Analytics', path: ROUTES.ANALYTICS },
      { id: 'messages', label: 'Messages', path: ROUTES.MESSAGES },
      { id: 'settings', label: 'Settings', path: ROUTES.SETTINGS },
    ];

    // IE1: Filter tabs based on user role and permissions
    initialTabs = initialTabs.filter(tab => {
      if (tab.requiredPermission && !can('read', tab.requiredPermission, 'organization')) {
        return false;
      }
      if (tab.roles && userRole && !tab.roles.includes(userRole)) {
        return false;
      }
      return true;
    });

    return initialTabs;
  }, [can, userRole]);

  // IE1: Render the navigation container with tabs
  return (
    <NavContainer>
      <NavTabs>
        {tabs.map((tab) => (
          <NavTab
            key={tab.id}
            to={tab.path}
            active={isRouteActive(tab.path, location.pathname)}
          >
            {tab.label}
            {notifications[tab.id] > 0 && (
              <Badge
                variant="error"
                size="small"
                count={notifications[tab.id]}
              />
            )}
            {isRouteActive(tab.path, location.pathname) && <ActiveIndicator />}
          </NavTab>
        ))}
      </NavTabs>
    </NavContainer>
  );
};

export default TabNavigation;