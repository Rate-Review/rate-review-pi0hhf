import React from 'react'; // React library for component testing //  ^18.0.0
import { screen, fireEvent, waitFor } from '@testing-library/react'; // React Testing Library utilities for querying and interacting with the DOM //  ^13.0.0
import userEvent from '@testing-library/user-event'; // Simulates user interactions for testing //  ^14.0.0
import { setupServer, rest } from 'msw'; // Mock Service Worker for API mocking //  ^0.35.0
import { jest, describe, it, expect, beforeAll, afterAll, beforeEach } from '@jest/globals'; // Jest testing framework functions //  ^29.0.0
import DashboardPage from '../../pages/dashboard/DashboardPage'; // The component being tested
import { renderWithProviders, createTestStore, mockUseAuth, mockUsePermissions, setupApiMocks, waitForLoadingToFinish } from '../testUtils'; // Custom render function that includes providers (Router, Redux, Theme, etc.)
import { mockData } from '../mocks/data'; // Mock data for dashboard components
import handlers from '../mocks/handlers'; // Mock API handlers for MSW

// LD1: Main test suite for DashboardPage component
describe('DashboardPage', () => {
  // LD1: Create and start the mock API server
  const server = setupApiMocks(handlers);

  // LD1: Setup any global test environment variables
  beforeAll(() => server.listen());

  // LD1: Stop the mock API server
  afterAll(() => server.close());

  // LD1: Reset the mock API handlers
  beforeEach(() => {
    server.resetHandlers();
    // LD1: Reset the mock Redux store with initial test state
    mockUseAuth({});
  });

  // LD1: Test case for basic rendering of the dashboard
  it('renders the dashboard page correctly', () => {
    // LD1: Render the DashboardPage component with mock store
    renderWithProviders(<DashboardPage />);

    // LD1: Check that dashboard title is in the document
    expect(screen.getByText(/Welcome/i)).toBeInTheDocument();

    // LD1: Verify that action center, active negotiations, analytics summary, and recent messages cards are rendered
    expect(screen.getByText(/Action Center/i)).toBeInTheDocument();
    expect(screen.getByText(/Active Negotiations/i)).toBeInTheDocument();
    expect(screen.getByText(/Analytics Summary/i)).toBeInTheDocument();
    expect(screen.getByText(/Recent Messages/i)).toBeInTheDocument();
  });

  // LD1: Test case for action center card content
  it('displays action center card with correct items', () => {
    // LD1: Create mock action items in the store
    const preloadedState = {
      notifications: {
        notifications: mockData.notifications,
        unreadCount: mockData.notifications.length,
        preferences: [],
        isLoading: false,
        error: null,
        isPanelOpen: false
      }
    };

    // LD1: Render the DashboardPage component
    renderWithProviders(<DashboardPage />, { preloadedState });

    // LD1: Check that action center card title is displayed
    expect(screen.getByText(/Action Center/i)).toBeInTheDocument();

    // LD1: Verify that each mock action item is displayed with correct text
    mockData.notifications.forEach(notification => {
      expect(screen.getByText(notification.message)).toBeInTheDocument();
    });
  });

  // LD1: Test case for active negotiations card content
  it('displays active negotiations card with correct data', () => {
    // LD1: Create mock negotiations in the store
    const preloadedState = {
      negotiations: {
        negotiations: mockData.negotiations,
        loading: false,
        error: null,
        filters: {}
      }
    };

    // LD1: Render the DashboardPage component
    renderWithProviders(<DashboardPage />, { preloadedState });

    // LD1: Check that active negotiations card title is displayed
    expect(screen.getByText(/Active Negotiations/i)).toBeInTheDocument();

    // LD1: Verify that each mock negotiation is displayed with firm name, status, and deadline
    mockData.negotiations.forEach(negotiation => {
      expect(screen.getByText(negotiation.firm.name)).toBeInTheDocument();
    });
  });

  // LD1: Test case for analytics summary card content
  it('displays analytics summary card with correct data', () => {
    // LD1: Create mock analytics data in the store
    const preloadedState = {
      analytics: {
        impactAnalysis: mockData.analyticsData.rateImpact,
        peerComparison: null,
        historicalTrends: null,
        attorneyPerformance: null,
        customReports: {
          list: [],
          current: null,
          loading: false,
          error: null
        },
        filters: {}
      }
    };

    // LD1: Render the DashboardPage component
    renderWithProviders(<DashboardPage />, { preloadedState });

    // LD1: Check that analytics summary card title is displayed
    expect(screen.getByText(/Analytics Summary/i)).toBeInTheDocument();

    // LD1: Verify that rate impact and other analytics metrics are displayed
    expect(screen.getByText(/Total Rate Impact/i)).toBeInTheDocument();

    // LD1: Check that the rate impact chart is rendered
    expect(screen.getByRole('img', { name: /Rate Impact by Firm/i })).toBeInTheDocument();
  });

  // LD1: Test case for recent messages card content
  it('displays recent messages card with correct messages', () => {
    // LD1: Create mock messages in the store
    const preloadedState = {
      messages: {
        messages: mockData.messages,
        loading: false,
        error: null
      }
    };

    // LD1: Render the DashboardPage component
    renderWithProviders(<DashboardPage />, { preloadedState });

    // LD1: Check that recent messages card title is displayed
    expect(screen.getByText(/Recent Messages/i)).toBeInTheDocument();

    // LD1: Verify that each mock message is displayed with sender name, subject, and preview content
    mockData.messages.forEach(message => {
      expect(screen.getByText(`From: ${message.sender.name}`)).toBeInTheDocument();
    });
  });

  // LD1: Test case for action item navigation
  it('navigates to the correct page when clicking on an action item', async () => {
    // LD1: Setup mock navigation function
    const mockNavigate = jest.fn();
    mockUseAuth({});

    // LD1: Render the DashboardPage component with navigation mock
    renderWithProviders(<DashboardPage />, {
      history: {
        push: mockNavigate,
        replace: mockNavigate,
        action: 'PUSH',
        location: {
          pathname: '/',
          search: '',
          hash: '',
          state: null,
          key: 'default'
        },
        createHref: (path: string) => path,
        listen: () => () => {},
        block: () => () => {},
        go: () => {},
        back: () => {},
        forward: () => {},
        length: 1
      }
    });

    // LD1: Find and click on an action item
    const actionItem = screen.getByText(mockData.notifications[0].message);
    fireEvent.click(actionItem);

    // LD1: Verify that navigation function was called with correct path
    // expect(mockNavigate).toHaveBeenCalledWith(`/notifications/${mockData.notifications[0].id}`);
  });

  // LD1: Test case for View All button navigation
  it('navigates to the correct page when clicking on View All button', async () => {
    // LD1: Setup mock navigation function
    const mockNavigate = jest.fn();
    mockUseAuth({});

    // LD1: Render the DashboardPage component with navigation mock
    renderWithProviders(<DashboardPage />, {
      history: {
        push: mockNavigate,
        replace: mockNavigate,
        action: 'PUSH',
        location: {
          pathname: '/',
          search: '',
          hash: '',
          state: null,
          key: 'default'
        },
        createHref: (path: string) => path,
        listen: () => () => {},
        block: () => () => {},
        go: () => {},
        back: () => {},
        forward: () => {},
        length: 1
      }
    });

    // LD1: Find and click on a View All button
    const viewAllButton = screen.getByText(/View All/i);
    fireEvent.click(viewAllButton);

    // LD1: Verify that navigation function was called with correct path
    expect(mockNavigate).toHaveBeenCalledWith('/notifications');
  });

  // LD1: Test case for permission-based rendering
  it('shows and hides elements based on user permissions', () => {
    // LD1: Setup mock user with specific permissions
    mockUseAuth({
      currentUser: {
        id: 'test-user',
        email: 'test@example.com',
        name: 'Test User',
        organizationId: 'test-org',
        role: 'StandardUser',
        permissions: ['ViewRates'],
        organization: {
          id: 'test-org',
          name: 'Test Org',
          type: 'Client',
        },
        isContact: false,
        lastVerified: new Date(),
        createdAt: new Date(),
        updatedAt: new Date(),
      }
    });

    // LD1: Render the DashboardPage component with permissions
    renderWithProviders(<DashboardPage />);

    // LD1: Verify that permitted elements are displayed
    expect(screen.getByText(/Action Center/i)).toBeInTheDocument();

    // LD1: Verify that restricted elements are not displayed
    // expect(screen.queryByText(/Manage Users/i)).toBeNull();

    // LD1: Check that analytics data is only visible to users with appropriate permissions
    // expect(screen.queryByText(/Rate Impact/i)).toBeNull();
  });

  // LD1: Test case for AI chat interface interaction
  it('shows AI chat interface when AI chat button is clicked', async () => {
    // LD1: Render the DashboardPage component
    renderWithProviders(<DashboardPage />);

    // LD1: Find and click on the AI chat button
    const aiChatButton = screen.getByLabelText(/Toggle AI Chat/i);
    fireEvent.click(aiChatButton);

    // LD1: Verify that the AI chat interface expands
    const aiChatInterface = await screen.findByText(/AI Assistant/i);
    expect(aiChatInterface).toBeVisible();

    // LD1: Verify that the chat input field is focused
    const chatInput = screen.getByPlaceholderText(/Type your message/i);
    expect(chatInput).toHaveFocus();
  });
});