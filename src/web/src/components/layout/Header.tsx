import React from 'react'; // React library for component creation //  ^18.0.0
import { useState, useRef, useEffect } from 'react'; // React hooks for state and side effects //  ^18.0.0
import styled from 'styled-components'; // CSS-in-JS styling library //  ^5.3.10
import { Link, useNavigate, useLocation } from 'react-router-dom'; // Routing utilities //  ^6.4.0
import { FiBell, FiUser, FiSettings, FiLogOut, FiMenu, FiSun, FiMoon, FiMessageSquare, FiHelpCircle } from 'react-feather'; // Icon components //  ^2.0.10

import { useAuth } from '../../hooks/useAuth'; // Access authentication state and functions
import { useTheme } from '../../context/ThemeContext'; // Access theme state and toggle function
import { useOrganizationContext } from '../../context/OrganizationContext'; // Access current organization context
import { ROUTES } from '../../constants/routes'; // Application route constants
import Button from '../common/Button'; // Button component for actions
import Avatar from '../common/Avatar'; // Avatar component for user profile display
import NotificationCenter from './NotificationCenter'; // Notification dropdown panel component
import AIChatInterface from '../ai/AIChatInterface'; // AI chat interface component
import { useNotifications } from '../../hooks/useNotifications'; // Access notification counts and data
import { useWindowSize } from '../../hooks/useWindowSize'; // Detect window size for responsive adjustments

// LD1: Styled component for the header container
const HeaderContainer = styled.header`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  height: 70px;
  background-color: ${props => props.theme.colors.background};
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  transition: all 0.3s ease;
`;

// LD1: Styled component for the logo container
const LogoContainer = styled.div`
  display: flex;
  align-items: center;
  a { text-decoration: none; color: inherit; }
`;

// LD1: Styled component for the logo image
const Logo = styled.img`
  height: 32px;
  margin-right: 0.5rem;
`;

// LD1: Styled component for the application title
const AppTitle = styled.h1`
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
  color: ${props => props.theme.colors.primary.main};
  display: flex;
  align-items: center;
  @media (max-width: 768px) {
    display: none;
  }
`;

// LD1: Styled component for the navigation container
const NavigationContainer = styled.nav`
  display: flex;
  align-items: center;
  @media (max-width: 992px) {
    display: none;
  }
`;

// LD1: Styled component for the mobile menu container
const MobileMenuContainer = styled.div<{ open: boolean }>`
  display: none;
  position: absolute;
  top: 70px;
  left: 0;
  right: 0;
  background-color: ${props => props.theme.colors.background};
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 999;
  padding: 1rem;
  @media (max-width: 992px) {
    display: ${props => (props.open ? 'block' : 'none')};
  }
`;

// LD1: Styled component for the user controls container
const UserControlsContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

// LD1: Styled component for the icon button
const IconButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.theme.colors.text.primary};
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  transition: background-color 0.2s ease;
  &:hover {
    background-color: ${props => props.theme.colors.action.hover};
  }
  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px ${props => props.theme.colors.primary.light};
  }
`;

// LD1: Styled component for the badge
const Badge = styled.span`
  position: absolute;
  top: 0;
  right: 0;
  background-color: ${props => props.theme.colors.error.main};
  color: white;
  font-size: 0.7rem;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
`;

// LD1: Styled component for the user menu container
const UserMenuContainer = styled.div`
  position: absolute;
  top: 60px;
  right: 1rem;
  background-color: ${props => props.theme.colors.background};
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  z-index: 1000;
  overflow: hidden;
`;

// LD1: Styled component for the user menu item
const UserMenuItem = styled.div`
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: ${props => props.theme.colors.text.primary};
  transition: background-color 0.2s ease;
  cursor: pointer;
  &:hover {
    background-color: ${props => props.theme.colors.action.hover};
  }
`;

// LD1: Styled component for the user info
const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
`;

// LD1: Styled component for the user name
const UserName = styled.span`
  font-weight: 500;
  @media (max-width: 576px) {
    display: none;
  }
`;

// LD1: Styled component for the user role
const UserRole = styled.span`
  font-size: 0.8rem;
  color: ${props => props.theme.colors.text.secondary};
  @media (max-width: 576px) {
    display: none;
  }
`;

/**
 * Main header component for the application
 */
const Header: React.FC = () => {
  // LD1: Get authentication state (currentUser, isAuthenticated, userRole, logout) from useAuth
  const { currentUser, isAuthenticated, userRole, logout } = useAuth();

  // LD1: Get theme state (themeMode, toggleTheme) from useTheme
  const { themeMode, toggleTheme } = useTheme();

  // LD1: Get organization context (currentOrganization) from useOrganizationContext
  const { currentOrganization } = useOrganizationContext();

  // LD1: Get notification count (unreadCount) from useNotifications
  const { unreadCount } = useNotifications();

  // LD1: Get window dimensions from useWindowSize
  const windowSize = useWindowSize();

  // LD1: Initialize state for dropdowns (userMenuOpen, notificationOpen, mobileMenuOpen, aiChatOpen)
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [notificationOpen, setNotificationOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [aiChatOpen, setAiChatOpen] = useState(false);

  // LD1: Create refs for user menu and notification panel for click-outside handling
  const userMenuRef = useRef<HTMLDivElement>(null);
  const notificationRef = useRef<HTMLDivElement>(null);

  // LD1: Set up navigate function for programmatic navigation
  const navigate = useNavigate();

  // LD1: Define handleLogout function to log user out and redirect to login page
  const handleLogout = () => {
    logout();
    navigate(ROUTES.LOGIN);
  };

  // LD1: Define handleToggleUserMenu to open/close user profile dropdown
  const handleToggleUserMenu = () => {
    setUserMenuOpen(!userMenuOpen);
  };

  // LD1: Define handleToggleNotifications to open/close notification panel
  const handleToggleNotifications = () => {
    setNotificationOpen(!notificationOpen);
  };

  // LD1: Define handleToggleMobileMenu to open/close mobile menu on small screens
  const handleToggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  // LD1: Define handleToggleAIChat to open/close AI chat interface
  const handleToggleAIChat = () => {
    setAiChatOpen(!aiChatOpen);
  };

  // LD1: Set up click-outside effect for dropdowns
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuOpen && userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
      if (notificationOpen && notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setNotificationOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [userMenuOpen, notificationOpen]);

  // LD1: Render HeaderContainer with logo, navigation, and user controls
  return (
    <HeaderContainer>
      <LogoContainer>
        <Link to={userRole === 'SystemAdministrator' ? ROUTES.ADMIN_DASHBOARD : userRole === 'OrganizationAdministrator' ? ROUTES.CLIENT_DASHBOARD : ROUTES.LAW_FIRM_DASHBOARD}>
          <Logo src={themeMode === 'dark' ? '/logo-light.png' : '/logo-dark.png'} alt="Justice Bid Logo" />
          <AppTitle>Justice Bid</AppTitle>
        </Link>
      </LogoContainer>

      <NavigationContainer>
        {/* TODO: Implement navigation links based on user role and permissions */}
      </NavigationContainer>

      <UserControlsContainer>
        {/* Conditionally render mobile menu button on small screens */}
        {windowSize.width <= 992 && (
          <IconButton onClick={handleToggleMobileMenu} aria-label="Open Mobile Menu">
            <FiMenu />
          </IconButton>
        )}

        <IconButton onClick={handleToggleNotifications} aria-label="Notifications">
          <FiBell />
          {/* Include notification icon with badge showing unread count */}
          {unreadCount > 0 && <Badge>{unreadCount}</Badge>}
        </IconButton>

        {/* Include theme toggle button */}
        <IconButton onClick={toggleTheme} aria-label="Toggle Theme">
          {themeMode === 'light' ? <FiMoon /> : <FiSun />}
        </IconButton>

        {/* Include AI chat toggle button */}
        <IconButton onClick={handleToggleAIChat} aria-label="Toggle AI Chat">
          <FiMessageSquare />
        </IconButton>

        {/* Include user profile section with avatar and dropdown menu */}
        <UserInfo onClick={handleToggleUserMenu}>
          <Avatar name={currentUser?.name} imageUrl={currentUser?.avatarUrl} size="sm" />
          <UserName>{currentUser?.name}</UserName>
          <UserRole>{currentUser?.role}</UserRole>
        </UserInfo>

        {/* Conditionally render UserMenuContainer when menu is open */}
        {userMenuOpen && (
          <UserMenuContainer ref={userMenuRef}>
            <Link to={ROUTES.PROFILE} style={{ textDecoration: 'none' }}>
              <UserMenuItem>
                <FiUser size={16} />
                <span>Profile</span>
              </UserMenuItem>
            </Link>
            <Link to={ROUTES.SETTINGS} style={{ textDecoration: 'none' }}>
              <UserMenuItem>
                <FiSettings size={16} />
                <span>Settings</span>
              </UserMenuItem>
            </Link>
            <UserMenuItem onClick={handleLogout}>
              <FiLogOut size={16} />
              <span>Logout</span>
            </UserMenuItem>
          </UserMenuContainer>
        )}
      </UserControlsContainer>

      {/* Conditionally render NotificationCenter when notificationOpen is true */}
      {notificationOpen && (
        <NotificationCenter onClose={() => setNotificationOpen(false)} ref={notificationRef} />
      )}

      {/* Conditionally render AIChatInterface when aiChatOpen is true */}
      {aiChatOpen && (
        <AIChatInterface />
      )}
    </HeaderContainer>
  );
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default Header;