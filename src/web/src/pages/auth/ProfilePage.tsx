import React, { useState, useEffect } from 'react'; // React library for building the component //  ^18.0.0
import { Link } from 'react-router-dom'; // Router link component for navigation //  ^6.0+
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Container,
  Grid,
  Typography,
  Divider,
  Switch,
  FormControlLabel,
  Tab, // Material UI components for layout and styling //  5.14+
} from '@mui/material';
import { toast } from 'react-hot-toast'; // Toast notifications for success/error messages //  2.4+

import { useAuth } from '../../../hooks/useAuth'; // Hook for accessing authentication state and profile management functions
import { ProfileForm } from '../../../components/forms/ProfileForm'; // Form component for editing personal profile information
import { PasswordForm } from '../../../components/forms/PasswordForm'; // Form component for changing user password
import { Tabs } from '../../../components/common/Tabs'; // Component for tabbed navigation
import { MainLayout } from '../../../components/layout/MainLayout'; // Main application layout component
import { Button } from '../../../components/common/Button'; // Button component for actions
import { Alert } from '../../../components/common/Alert'; // Alert component for displaying status messages
import { ROUTES } from '../../../constants/routes'; // Route constants for navigation
import { useOrganization } from '../../../hooks/useOrganizations'; // Hook for accessing current organization context
import { UserProfileResponse } from '../../../types/user'; // Type definition for user profile data

/**
 * React component for the user profile page that allows viewing and editing profile information,
 * changing password, and managing MFA settings
 */
const ProfilePage: React.FC = () => {
  // LD1: Initialize state for the active tab with useState
  const [activeTab, setActiveTab] = useState('profile');

  // LD1: Initialize state for success and error messages with useState
  const [alert, setAlert] = useState<{ type: 'success' | 'error' | null; message: string | null }>({
    type: null,
    message: null,
  });

  // LD1: Get user data, updateProfile, changePassword, and isMfaEnabled from useAuth hook
  const { user, updateProfile, changePassword, isMfaEnabled } = useAuth();

  // LD1: Get currentOrganization from useOrganization hook
  const { currentOrganization } = useOrganization();

  // LD1: Define handleProfileSubmit function to handle profile form submission
  const handleProfileSubmit = async (profileData: UserProfileResponse) => {
    try {
      // LD1: Call updateProfile function with profile data
      await updateProfile(profileData);
      // LD1: Display success message using toast
      toast.success('Profile updated successfully!');
      // LD1: Set success alert
      setAlert({ type: 'success', message: 'Profile updated successfully!' });
    } catch (error: any) {
      // LD1: Display error message using toast
      toast.error(error.message || 'Failed to update profile.');
      // LD1: Set error alert
      setAlert({ type: 'error', message: error.message || 'Failed to update profile.' });
    }
  };

  // LD1: Define handlePasswordSubmit function to handle password form submission
  const handlePasswordSubmit = async (passwordData: any) => {
    try {
      // LD1: Call changePassword function with password data
      await changePassword(passwordData);
      // LD1: Display success message using toast
      toast.success('Password changed successfully!');
      // LD1: Set success alert
      setAlert({ type: 'success', message: 'Password changed successfully!' });
    } catch (error: any) {
      // LD1: Display error message using toast
      toast.error(error.message || 'Failed to change password.');
      // LD1: Set error alert
      setAlert({ type: 'error', message: error.message || 'Failed to change password.' });
    }
  };

  // LD1: Define handleTabChange function to handle tab navigation
  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    // LD1: Clear any existing alerts when changing tabs
    setAlert({ type: null, message: null });
  };

  // LD1: Define handleToggleMfa function to handle MFA toggle
  const handleToggleMfa = () => {
    // TODO: Implement MFA toggle logic
    console.log('Toggling MFA');
  };

  // LD1: Define handleToggleNotifications function to handle notification preferences
  const handleToggleNotifications = () => {
    // TODO: Implement notification preferences logic
    console.log('Toggling notifications');
  };

  // LD1: Render MainLayout component with profile content
  return (
    <MainLayout>
      {/* LD1: Render a Container with a page heading */}
      <Container maxWidth="md">
        <Typography variant="h4" component="h1" gutterBottom>
          Profile
        </Typography>

        {/* LD1: Render Tabs component with Profile, Security, and Notifications tabs */}
        <Tabs
          tabs={[
            { id: 'profile', label: 'Profile' },
            { id: 'security', label: 'Security' },
            { id: 'notifications', label: 'Notifications' },
          ]}
          activeTab={activeTab}
          onChange={handleTabChange}
        />

        {/* LD1: Render a Card component for the active tab content */}
        <Card>
          <CardContent>
            {/* LD1: In Profile tab: Render ProfileForm with user data and handleProfileSubmit handler */}
            {activeTab === 'profile' && (
              <ProfileForm
                onSuccess={() => setAlert({ type: 'success', message: 'Profile updated successfully!' })}
              />
            )}

            {/* LD1: In Security tab: Render PasswordForm with handlePasswordSubmit handler */}
            {activeTab === 'security' && (
              <>
                <PasswordForm
                  onSuccess={() => setAlert({ type: 'success', message: 'Password changed successfully!' })}
                />
                <Divider style={{ margin: '20px 0' }} />
                <Typography variant="h6" gutterBottom>
                  Multi-Factor Authentication
                </Typography>
                <FormControlLabel
                  control={<Switch checked={isMfaEnabled} onChange={handleToggleMfa} />}
                  label="Enable Multi-Factor Authentication"
                />
                <Typography variant="body2" color="textSecondary">
                  Protect your account with an extra layer of security.
                </Typography>
                <Button component={Link} to={ROUTES.MFA_SETUP}>
                  Setup MFA
                </Button>
              </>
            )}

            {/* LD1: In Notifications tab: Render notification preference toggles */}
            {activeTab === 'notifications' && (
              <>
                <Typography variant="h6" gutterBottom>
                  Notification Preferences
                </Typography>
                <FormControlLabel
                  control={<Switch onChange={handleToggleNotifications} />}
                  label="Email Notifications"
                />
                <FormControlLabel
                  control={<Switch onChange={handleToggleNotifications} />}
                  label="In-App Notifications"
                />
              </>
            )}
          </CardContent>
        </Card>

        {/* LD1: Render Alert component for success or error messages */}
        {alert.message && (
          <Alert severity={alert.type === 'success' ? 'success' : 'error'} message={alert.message} />
        )}
      </Container>
    </MainLayout>
  );
};

export default ProfilePage;