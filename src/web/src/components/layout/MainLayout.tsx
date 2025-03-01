import React, { useState, useEffect } from 'react'; // React library for building UI components //  ^18.0.0
import styled from 'styled-components'; // CSS-in-JS styling library //  ^5.3.6
import Header from './Header'; // Main navigation header component
import Sidebar from './Sidebar'; // Navigation sidebar component
import Footer from './Footer'; // Footer component with copyright and links
import AIChatInterface from '../ai/AIChatInterface'; // AI chat interface for persistent assistance
import { useWindowSize } from '../../hooks/useWindowSize'; // Hook to detect window size for responsive adjustments
import { useTheme } from '../../context/ThemeContext'; // Access theme context for styling
import { useSelector, useDispatch } from 'react-redux'; // Redux hooks for global state //  ^8.0.5

/**
 * @interface MainLayoutProps
 * @description Interface defining the props for the MainLayout component
 */
interface MainLayoutProps {
  /**
   * @description React children to be rendered within the layout
   */
  children: React.ReactNode;
}

/**
 * @const LayoutContainer
 * @description A styled div component that provides the base structure for the layout
 */
const LayoutContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: ${props => props.theme.colors.background};
  color: ${props => props.theme.colors.text.primary};
  transition: all 0.3s ease;
`;

/**
 * @const ContentWrapper
 * @description A styled div component that wraps the main content and sidebar
 */
const ContentWrapper = styled.div`
  display: flex;
  flex: 1;
  transition: all 0.3s ease;
`;

/**
 * @const MainContent
 * @description A styled main element that contains the main content of the page
 */
const MainContent = styled.main<{ sidebarOpen: boolean; isMobile: boolean }>`
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  margin-left: ${props => props.sidebarOpen ? (props.isMobile ? '0' : '240px') : '64px'};
  transition: margin-left 0.3s ease;
  @media (max-width: 768px) {
    margin-left: 0;
    padding: 16px;
  }
`;

/**
 * @const ChatContainer
 * @description A styled div component that contains the AI chat interface
 */
const ChatContainer = styled.div`
  position: fixed;
  bottom: 0;
  right: 24px;
  z-index: 1000;
  transition: all 0.3s ease;
  @media (max-width: 768px) {
    right: 16px;
  }
`;

/**
 * @function MainLayout
 * @param {MainLayoutProps} props - The props for the component
 * @returns {JSX.Element} - The rendered component
 * @description Main layout component that structures the application with header, sidebar, content area, and AI chat
 */
const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  // LD1: Destructure children from props
  
  // LD1: Initialize sidebarOpen state with useState, defaulting to true for larger screens
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // LD1: Get window width from useWindowSize hook for responsive adjustments
  const windowSize = useWindowSize();

  // LD1: Get theme object from useTheme hook
  const { theme } = useTheme();

  // LD1: Get AI chat minimized state from Redux store using useSelector
  const aiChatMinimized = useSelector((state: any) => state.ai.minimized);

  // LD1: Set up Redux dispatch function using useDispatch
  const dispatch = useDispatch();

  // LD1: Define toggleSidebar function to handle sidebar open/close state
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // LD1: Use useEffect to adjust sidebar based on screen size
  useEffect(() => {
    if (windowSize.width && windowSize.width < theme.breakpoints.values.md) {
      setSidebarOpen(false);
    } else {
      setSidebarOpen(true);
    }
  }, [windowSize.width, theme.breakpoints.values.md]);

  // LD1: Render LayoutContainer with Header, Sidebar, MainContent, and Footer
  return (
    <LayoutContainer>
      <Header toggleSidebar={toggleSidebar} />
      <ContentWrapper>
        <Sidebar isOpen={sidebarOpen} />
        <MainContent sidebarOpen={sidebarOpen} isMobile={windowSize.width < theme.breakpoints.values.md}>
          {children}
        </MainContent>
      </ContentWrapper>
      <Footer />
      {/* LD1: Include AIChatInterface component for persistent AI chat */}
      <ChatContainer>
        <AIChatInterface />
      </ChatContainer>
    </LayoutContainer>
  );
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default MainLayout;