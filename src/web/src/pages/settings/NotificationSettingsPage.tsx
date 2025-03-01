import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Grid,
  Typography,
  Checkbox,
  FormControlLabel,
  CircularProgress,
  Card,
  Button,
  Select,
  MenuItem,
  FormControl,
} from '@mui/material';
import { notificationCategories, deliveryMethods, urgencyLevels } from '@app/constants';

/**
 * Main component for the notification settings page that allows users to configure their notification preferences.
 * @returns The rendered notification settings page component
 */
const NotificationSettingsPage: React.FC = () => {
  const dispatch = useDispatch();
  
  // Get current user notification settings from Redux store
  const notificationSettings = useSelector((state: any) => state.settings.notificationSettings);
  
  // Loading and error states
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  
  // Form state for notification settings
  const [formState, setFormState] = useState<any>({});
  
  // Initialize form with current settings when available
  useEffect(() => {
    if (notificationSettings) {
      setFormState(notificationSettings);
    } else {
      // Initialize default settings if none exist
      const defaultSettings: any = {};
      
      // Create default settings for each notification category/event
      Object.entries(notificationCategories).forEach(([categoryKey, category]) => {
        Object.entries(category.events).forEach(([eventKey, event]) => {
          defaultSettings[eventKey] = {
            enabled: true,
            deliveryMethod: event.defaultDelivery || 'in-app',
            urgencyLevel: event.defaultUrgency || 'medium',
          };
        });
      });
      
      setFormState(defaultSettings);
    }
  }, [notificationSettings]);
  
  /**
   * Handler function for form field changes that updates the form state.
   * @param event - The change event from the input or select element
   * @param category - The notification category being updated
   * @param field - The specific field being updated (enabled, deliveryMethod, urgencyLevel)
   */
  const handleFormChange = (
    event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
    category: string,
    field: string
  ) => {
    const target = event.target as HTMLInputElement;
    const value = field === 'enabled' ? target.checked : target.value;
    
    setFormState((prevState: any) => ({
      ...prevState,
      [category]: {
        ...prevState[category],
        [field]: value,
      },
    }));
  };
  
  /**
   * Handler function for form submission that saves the notification settings.
   * @param event - The form submission event
   */
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);
    
    try {
      // Dispatch Redux action to save notification settings
      await dispatch({
        type: 'settings/updateNotificationSettings',
        payload: formState,
      });
      
      setSuccess(true);
      setTimeout(() => setSuccess(false), 6000); // Hide success message after 6 seconds
    } catch (err) {
      console.error('Failed to update notification settings:', err);
      setError('Failed to save notification settings. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h4" gutterBottom>
          Notification Settings
        </Typography>
        <Typography variant="body1" color="textSecondary" paragraph>
          Configure how and when you receive notifications about rate negotiations,
          approvals, messages, and system updates. You can choose to receive notifications
          in the application, via email, or both.
        </Typography>
      </Grid>
      
      <Grid item xs={12}>
        <form onSubmit={handleSubmit}>
          {Object.entries(notificationCategories).map(([categoryKey, category]) => (
            <Card key={categoryKey} sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                {category.title}
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                {category.description}
              </Typography>
              
              {Object.entries(category.events).map(([eventKey, event]) => {
                const isEnabled = formState[eventKey]?.enabled ?? true;
                const deliveryMethod = formState[eventKey]?.deliveryMethod || 'in-app';
                const urgencyLevel = formState[eventKey]?.urgencyLevel || 'medium';
                
                return (
                  <Grid container spacing={2} key={eventKey} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={4}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={isEnabled}
                            onChange={(e) => handleFormChange(e, eventKey, 'enabled')}
                            name={`${eventKey}-enabled`}
                          />
                        }
                        label={event.label}
                      />
                    </Grid>
                    
                    <Grid item xs={12} sm={4}>
                      <FormControl fullWidth disabled={!isEnabled} size="small">
                        <Typography variant="caption" gutterBottom>
                          Delivery Method
                        </Typography>
                        <Select
                          value={deliveryMethod}
                          onChange={(e) => handleFormChange(e, eventKey, 'deliveryMethod')}
                          name={`${eventKey}-deliveryMethod`}
                        >
                          {Object.entries(deliveryMethods).map(([methodKey, method]) => (
                            <MenuItem key={methodKey} value={methodKey}>
                              {method.label}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    
                    <Grid item xs={12} sm={4}>
                      <FormControl fullWidth disabled={!isEnabled} size="small">
                        <Typography variant="caption" gutterBottom>
                          Urgency Level
                        </Typography>
                        <Select
                          value={urgencyLevel}
                          onChange={(e) => handleFormChange(e, eventKey, 'urgencyLevel')}
                          name={`${eventKey}-urgencyLevel`}
                        >
                          {Object.entries(urgencyLevels).map(([levelKey, level]) => (
                            <MenuItem key={levelKey} value={levelKey}>
                              {level.label}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    
                    {event.description && (
                      <Grid item xs={12}>
                        <Typography variant="caption" color="textSecondary">
                          {event.description}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                );
              })}
            </Card>
          ))}
          
          {error && (
            <Typography color="error" sx={{ mt: 2, mb: 2 }}>
              {error}
            </Typography>
          )}
          
          {success && (
            <Typography color="success.main" sx={{ mt: 2, mb: 2 }}>
              Notification settings updated successfully
            </Typography>
          )}
          
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading}
            sx={{ mt: 2 }}
          >
            {loading ? <CircularProgress size={24} sx={{ mr: 1 }} /> : null}
            {loading ? 'Saving...' : 'Save Settings'}
          </Button>
        </form>
      </Grid>
    </Grid>
  );
};

export default NotificationSettingsPage;