import React, { useState, useEffect } from 'react'; //  ^18.0.0
import { useNavigate, useLocation } from 'react-router-dom'; //  ^6.4.0
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Box,
  Divider,
  Avatar,
  Typography,
} from '@mui/material'; //  ^5.14.0
import { styled } from '@mui/material/styles'; //  ^5.14.0
import {
  DashboardOutlined,
  DescriptionOutlined,
  HandshakeOutlined,
  BarChartOutlined,
  MessageOutlined,
  SettingsOutlined,
  Close,
} from '@mui/icons-material'; //  ^5.14.0
import { useTheme } from '../context/ThemeContext';
import { usePermissions } from '../hooks/usePermissions';
import { useAuth } from '../hooks/useAuth';
import { routes } from '../constants/routes';

// Define the MobileNavigationProps interface
interface MobileNavigationProps {
  className?: string;
  isOpen: boolean;
  onClose: () => void;
}

// Define the NavigationItem interface
interface NavigationItem {
  label: string;
  path: string;
  icon: React.ReactNode;
  permission?: string;
  subItems?: Array<{
    label: string;
    path: string;
    permission?: string;
  }>;
}

// Define the navigationItems array
const navigationItems: NavigationItem[] = [
  { label: 'Dashboard', path: routes.DASHBOARD, icon: <DashboardOutlined />, permission: 'dashboard:view' },
  { label: 'Rates', path: routes.RATES, icon: <DescriptionOutlined />, permission: 'rates:view', subItems: [
    { label: 'Rate Requests', path: routes.RATE_REQUESTS, permission: 'rates:view' },
    { label: 'Rate Submissions', path: routes.RATE_SUBMISSIONS, permission: 'rates:view' },
    { label: 'Rate History', path: routes.RATE_HISTORY, permission: 'rates:view' },
    { label: 'Rate Analytics', path: routes.RATE_ANALYTICS, permission: 'analytics:view' }
  ]},
  { label: 'Negotiations', path: routes.NEGOTIATIONS, icon: <HandshakeOutlined />, permission: 'negotiations:view', subItems: [
    { label: 'Active Negotiations', path: routes.ACTIVE_NEGOTIATIONS, permission: 'negotiations:view' },
    { label: 'Completed Negotiations', path: routes.COMPLETED_NEGOTIATIONS, permission: 'negotiations:view' }
  ]},
  { label: 'Analytics', path: routes.ANALYTICS, icon: <BarChartOutlined />, permission: 'analytics:view', subItems: [
    { label: 'Rate Impact', path: routes.RATE_IMPACT, permission: 'analytics:view' },
    { label: 'Peer Comparisons', path: routes.PEER_COMPARISONS, permission: 'analytics:view' },
    { label: 'Historical Trends', path: routes.HISTORICAL_TRENDS, permission: 'analytics:view' },
    { label: 'Attorney Performance', path: routes.ATTORNEY_PERFORMANCE, permission: 'analytics:view' },
    { label: 'Custom Reports', path: routes.CUSTOM_REPORTS, permission: 'analytics:view' }
  ]},
  { label: 'Messages', path: routes.MESSAGES, icon: <MessageOutlined />, permission: 'messages:view', subItems: [
    { label: 'All Messages', path: routes.ALL_MESSAGES, permission: 'messages:view' },
    { label: 'By Negotiation', path: routes.MESSAGES_BY_NEGOTIATION, permission: 'messages:view' },
    { label: 'By Firm/Client', path: routes.MESSAGES_BY_ORGANIZATION, permission: 'messages:view' }
  ]},
  { label: 'Settings', path: routes.SETTINGS, icon: <SettingsOutlined />, permission: 'settings:view', subItems: [
    { label: 'Organization', path: routes.ORGANIZATION_SETTINGS, permission: 'settings:view' },
    { label: 'Users & Permissions', path: routes.USER_MANAGEMENT, permission: 'users:manage' },
    { label: 'Rate Rules', path: routes.RATE_RULES, permission: 'rates:manage' },
    { label: 'Outside Counsel Guidelines', path: routes.OCG, permission: 'ocg:view' },
    { label: 'Peer Groups', path: routes.PEER_GROUPS, permission: 'peers:manage' },
    { label: 'Integrations', path: routes.INTEGRATIONS, permission: 'integrations:manage' },
    { label: 'Notifications', path: routes.NOTIFICATION_SETTINGS, permission: 'notifications:manage' }
  ]}
];

// Define the renderNavItem function
const renderNavItem = (item: NavigationItem, currentPath: string, isSubItem: boolean) => {
  const isActive = currentPath.startsWith(item.path);

  return (
    <ListItem button key={item.label} component="a" href={item.path}
      sx={{
        pl: isSubItem ? 4 : 2,
        backgroundColor: isActive ? 'rgba(0, 0, 0, 0.04)' : 'transparent',
        '&:hover': {
          backgroundColor: 'rgba(0, 0, 0, 0.08)',
        },
      }}
    >
      {!isSubItem && (
        <ListItemIcon sx={{ minWidth: 36 }}>
          {item.icon}
        </ListItemIcon>
      )}
      <ListItemText primary={item.label} />
    </ListItem>
  );
};

// Define the renderNavItems function
const renderNavItems = () => {
  return (
    <List>
      {navigationItems.map((item) => (
        renderNavItem(item, location.pathname, false)
      ))}
    </List>
  );
};

// Define the MobileNavigation component
const MobileNavigation: React.FC<MobileNavigationProps> = ({ className, isOpen, onClose }) => {
  const { theme } = useTheme();
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [expandedSections, setExpandedSections] = useState<string[]>([]);

  const toggleSection = (label: string) => {
    setExpandedSections((prev) =>
      prev.includes(label) ? prev.filter((item) => item !== label) : [...prev, label]
    );
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    onClose();
  };

  return (
    <Drawer
      anchor="left"
      open={isOpen}
      onClose={onClose}
      sx={{
        width: 250,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: 250,
          boxSizing: 'border-box',
          backgroundColor: theme.palette.background.default,
          color: theme.palette.text.primary,
        },
      }}
    >
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h6">Justice Bid</Typography>
        <IconButton onClick={onClose}>
          <Close />
        </IconButton>
      </Box>
      <Divider />
      {renderNavItems()}
    </Drawer>
  );
};

export default MobileNavigation;