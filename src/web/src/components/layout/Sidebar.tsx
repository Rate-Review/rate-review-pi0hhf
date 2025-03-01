import React, { useState, useEffect, useCallback } from 'react'; //  ^18.0.0
import { NavLink, useLocation } from 'react-router-dom'; // ^6.4.0
import {
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Tooltip, // ^5.14.0
} from '@mui/material'; // ^5.14.0
import { styled } from '@mui/material/styles'; // ^5.14.0
import {
  Dashboard as DashboardIcon,
  AttachMoney as RateIcon,
  CompareArrows as NegotiationIcon,
  BarChart as AnalyticsIcon,
  Email as MessageIcon,
  Settings as SettingsIcon,
  MenuOpen as MenuOpenIcon,
  Menu as MenuIcon, // ^5.14.0
} from '@mui/icons-material'; // ^5.14.0
import { routes } from '../constants/routes';
import { useTheme } from '../context/ThemeContext';
import { usePermissions } from '../hooks/usePermissions';
import { useWindowSize } from '../hooks/useWindowSize';
import { useOrganizationContext } from '../context/OrganizationContext';

/**
 * @interface NavItem
 * @description Interface describing the structure of navigation items in the sidebar
 */
interface NavItem {
  label: string;
  icon: React.ComponentType;
  path: string;
  permission?: string;
}

/**
 * @const SidebarContainer
 * @description Custom styling for the sidebar drawer with theme-aware colors and responsive width
 */
const SidebarContainer = styled(Drawer, { shouldForwardProp: (prop) => prop !== 'isOpen' })(
  ({ theme, isOpen }) => ({
    width: isOpen ? 240 : 60,
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
    '& .MuiDrawer-paper': {
      width: isOpen ? 240 : 60,
      backgroundColor: theme.palette.background.paper,
      color: theme.palette.text.primary,
      transition: theme.transitions.create('width', {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.enteringScreen,
      }),
      overflowX: 'hidden',
    },
  })
);

/**
 * @const SidebarHeader
 * @description Header section of the sidebar containing the toggle button and padding
 */
const SidebarHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

/**
 * @const NavItemText
 * @description Custom styling for navigation item text with transitions for collapse/expand animations
 */
const NavItemText = styled(ListItemText, {
  shouldForwardProp: (prop) => prop !== 'isOpen',
})(({ theme, isOpen }) => ({
  opacity: isOpen ? 1 : 0,
  transition: theme.transitions.create('opacity', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.shortest,
  }),
}));

/**
 * @const NavItemIcon
 * @description Custom styling for navigation item icons with consistent sizing and colors
 */
const NavItemIcon = styled(ListItemIcon)(({ theme }) => ({
  minWidth: 56,
  color: theme.palette.text.secondary,
}));

/**
 * @function Sidebar
 * @description Main component for sidebar navigation that displays different navigation links based on user role and permissions, with responsive design for different screen sizes
 * @returns {JSX.Element} The rendered sidebar component
 */
const Sidebar = (): JSX.Element => {
  // LD1: Initialize state for sidebar open/closed status
  const [open, setOpen] = useState(true);

  // LD1: Get current location from React Router
  const location = useLocation();

  // LD1: Get theme from ThemeContext
  const { theme } = useTheme();

  // LD1: Get organization type from OrganizationContext
  const { currentOrganization } = useOrganizationContext();

  // LD1: Get user permissions from usePermissions hook
  const { can } = usePermissions();

  // LD1: Get window size from useWindowSize hook
  const { width } = useWindowSize();

  // LD1: Define toggle function for opening and closing sidebar
  const toggleDrawer = useCallback(() => {
    setOpen(!open);
  }, [open]);

  // LD1: Define navigation items based on organization type (Law Firm, Client, Admin)
  const baseNavItems: NavItem[] = [
    { label: 'Dashboard', icon: DashboardIcon, path: routes.CLIENT_DASHBOARD },
    { label: 'Rates', icon: RateIcon, path: routes.RATE_REQUESTS },
    { label: 'Negotiations', icon: NegotiationIcon, path: routes.NEGOTIATIONS },
    { label: 'Analytics', icon: AnalyticsIcon, path: routes.ANALYTICS },
    { label: 'Messages', icon: MessageIcon, path: routes.MESSAGES },
    { label: 'Settings', icon: SettingsIcon, path: routes.SETTINGS },
  ];

  // LD1: Filter navigation items based on user permissions
  const navItems = baseNavItems.filter(item => {
    return item.permission ? can('read', item.permission, 'organization') : true;
  });

  // LD1: Handle responsive behavior based on window size
  useEffect(() => {
    if (width && width < theme.breakpoints.values.md) {
      setOpen(false);
    } else {
      setOpen(true);
    }
  }, [width, theme.breakpoints.values.md]);

  /**
   * @function renderNavItems
   * @description Renders navigation items as links based on the provided navigation configuration
   * @param {NavItem[]} navItems - Array of navigation items to render
   * @param {boolean} isOpen - Whether the sidebar is open or closed
   * @returns {JSX.Element[]} Array of navigation item elements
   */
  const renderNavItems = (navItems: NavItem[], isOpen: boolean): JSX.Element[] => {
    return navItems.map((item) => (
      <ListItem key={item.label} disablePadding sx={{ display: 'block' }}>
        <Tooltip title={item.label} placement="right" disableHoverListener={isOpen}>
          <NavLink
            to={item.path}
            style={({ isActive }) => ({
              textDecoration: 'none',
              color: theme.palette.text.primary,
              backgroundColor: isActive ? theme.palette.action.selected : 'transparent',
            })}
          >
            <ListItem button sx={{
              minHeight: 48,
              justifyContent: isOpen ? 'initial' : 'center',
              px: 2.5,
            }}>
              <NavItemIcon sx={{
                mr: isOpen ? 3 : 'auto',
                justifyContent: 'center',
              }}>
                <item.icon />
              </NavItemIcon>
              <NavItemText primary={item.label} isOpen={isOpen} />
            </ListItem>
          </NavLink>
        </Tooltip>
      </ListItem>
    ));
  };

  // LD1: Render the drawer component with navigation items
  return (
    <SidebarContainer variant="permanent" open={open}>
      <SidebarHeader>
        <IconButton onClick={toggleDrawer}>
          {open ? <MenuOpenIcon /> : <MenuIcon />}
        </IconButton>
      </SidebarHeader>
      <Divider />
      <List>
        {renderNavItems(navItems, open)}
      </List>
    </SidebarContainer>
  );
};

export default Sidebar;