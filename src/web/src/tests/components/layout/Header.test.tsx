import React from 'react'; // React library for component creation //  ^18.0.0
import { screen, fireEvent, waitFor } from '@testing-library/react'; // React Testing Library utilities for querying DOM and simulating events //  ^14.0.0
import userEvent from '@testing-library/user-event'; // Simulates user interactions more realistically than fireEvent //  ^14.0.0
import { renderWithProviders, mockUseAuth } from '../../testUtils'; // Testing utilities for rendering with providers and mocking authentication
import { ROUTES } from '../../../constants/routes'; // Route constants for navigation testing
import Header from '../../../components/layout/Header'; // The component being tested
import jest from 'jest'; // Testing framework for assertions and mocks

jest.mock('../../../hooks/useNotifications', () => ({
  useNotifications: () => ({ unreadCount: 3 })
}));
jest.mock('../../../hooks/useWindowSize', () => ({
  useWindowSize: () => ({ width: 1200, height: 800 })
}));

describe('Header component', () => {
  test('renders without crashing', () => {
    mockUseAuth({});
    renderWithProviders(<Header />);

    expect(screen.getByText('Justice Bid')).toBeInTheDocument();
    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Notifications' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Toggle Theme' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Toggle AI Chat' })).toBeInTheDocument();
  });

  test('displays user information correctly', () => {
    mockUseAuth({
      currentUser: {
        id: 'test-user',
        email: 'test@example.com',
        name: 'John Doe',
        organizationId: 'test-org',
        role: 'StandardUser',
        permissions: [],
        organization: {
          id: 'test-org',
          name: 'Test Org',
          type: 'Client',
        },
        isContact: false,
        lastVerified: new Date(),
        createdAt: new Date(),
        updatedAt: new Date(),
      },
    });
    renderWithProviders(<Header />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('StandardUser')).toBeInTheDocument();
  });

  test('toggles user menu when clicked', async () => {
    mockUseAuth({});
    renderWithProviders(<Header />);

    const avatarButton = screen.getByRole('button', { name: 'Test User' });
    await userEvent.click(avatarButton);

    expect(screen.getByText('Profile')).toBeVisible();

    await userEvent.click(avatarButton);
    await waitFor(() => {
      expect(screen.queryByText('Profile')).not.toBeInTheDocument();
    });
  });

  test('triggers logout when logout option clicked', async () => {
    const mockLogout = jest.fn();
    mockUseAuth({ logout: mockLogout });
    renderWithProviders(<Header />);

    const avatarButton = screen.getByRole('button', { name: 'Test User' });
    await userEvent.click(avatarButton);

    const logoutButton = screen.getByRole('menuitem', { name: 'Logout' });
    await userEvent.click(logoutButton);

    expect(mockLogout).toHaveBeenCalled();
  });

  test('displays notification badge with correct count', () => {
    mockUseAuth({});
    renderWithProviders(<Header />);

    const notificationButton = screen.getByRole('button', { name: 'Notifications' });
    expect(notificationButton).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  test('toggles theme when theme button is clicked', async () => {
    const mockToggleTheme = jest.fn();
    jest.mock('../../../context/ThemeContext', () => ({
      useTheme: () => ({
        themeMode: 'light',
        toggleTheme: mockToggleTheme,
      }),
    }));
    renderWithProviders(<Header />);

    const themeButton = screen.getByRole('button', { name: 'Toggle Theme' });
    await userEvent.click(themeButton);

    expect(mockToggleTheme).toHaveBeenCalled();
  });

  test('shows mobile menu on small screens', async () => {
    jest.mock('../../../hooks/useWindowSize', () => ({
      useWindowSize: () => ({ width: 600, height: 800 }),
    }));
    mockUseAuth({});
    renderWithProviders(<Header />);

    const mobileMenuButton = screen.getByRole('button', { name: 'Open Mobile Menu' });
    expect(mobileMenuButton).toBeVisible();

    await userEvent.click(mobileMenuButton);
    expect(screen.getByRole('link', { name: 'Dashboard' })).toBeVisible();
  });

  test('navigates correctly when links are clicked', async () => {
    mockUseAuth({});
    const mockNavigate = jest.fn();
    const { rerender } = renderWithProviders(<Header />, {
      history: { push: mockNavigate, location: { pathname: '/' }, action: 'PUSH' } as any,
    });

    const logoLink = screen.getByRole('link', { name: 'Justice Bid' });
    await userEvent.click(logoLink);

    expect(mockNavigate).toHaveBeenCalledWith(ROUTES.CLIENT_DASHBOARD);
  });

  test('toggles AI chat interface when AI button clicked', async () => {
    mockUseAuth({});
    renderWithProviders(<Header />);

    const aiChatButton = screen.getByRole('button', { name: 'Toggle AI Chat' });
    await userEvent.click(aiChatButton);

    expect(screen.getByText('AI Assistant')).toBeVisible();

    await userEvent.click(aiChatButton);
    await waitFor(() => {
      expect(screen.queryByText('AI Assistant')).not.toBeInTheDocument();
    });
  });
});