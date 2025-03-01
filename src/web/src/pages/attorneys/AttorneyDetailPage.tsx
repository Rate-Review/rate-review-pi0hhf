import React, { useState, useEffect, useMemo } from 'react'; // React: ^18.0.0
import { useParams, useNavigate } from 'react-router-dom'; // react-router-dom: ^6.14.1
import { Grid, Typography, Box, Divider, CircularProgress, Alert } from '@mui/material'; // MUI components: ^5.14.0
import { EditOutlined, PersonOutline, HistoryOutlined, AssessmentOutlined, AttachMoneyOutlined } from '@mui/icons-material'; // MUI icons: ^5.14.0

import { Attorney } from '../../types/attorney';
import { Rate } from '../../types/rate';
import { getAttorneyById, getAttorneyRates, getAttorneyPerformance } from '../../services/attorneys';
import MainLayout from '../../components/layout/MainLayout';
import PageHeader from '../../components/layout/PageHeader';
import RateTable from '../../components/tables/RateTable';
import Card from '../../components/common/Card';
import Tabs from '../../components/common/Tabs';
import Button from '../../components/common/Button';
import Spinner from '../../components/common/Spinner';
import AttorneyPerformancePanel from '../../components/analytics/AttorneyPerformancePanel';
import RateHistoryTimeline from '../../components/negotiation/RateHistoryTimeline';
import RecommendationCard from '../../components/ai/RecommendationCard';
import { useAuth } from '../../hooks/useAuth';
import { usePermissions } from '../../hooks/usePermissions';

/**
 * Main component for the attorney detail page that displays comprehensive information about an attorney
 */
const AttorneyDetailPage: React.FC = () => {
  // LD1: Get attorney ID from URL parameters
  const { id } = useParams<{ id: string }>();

  // LD1: Initialize state for attorney data, rates, performance metrics, and loading state
  const [attorney, setAttorney] = useState<Attorney | null>(null);
  const [rates, setRates] = useState<Rate[]>([]);
  const [performanceData, setPerformanceData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // LD1: Set up navigate function for programmatic navigation
  const navigate = useNavigate();

  // LD1: Get authentication state and user role from useAuth hook
  const { isAuthenticated, userRole } = useAuth();

  // LD1: Get permission checking function from usePermissions hook
  const { can } = usePermissions();

  // LD1: Fetch attorney details, rates, and performance metrics on component mount
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        if (id) {
          const attorneyData = await getAttorneyById(id);
          setAttorney(attorneyData);

          const ratesData = await getAttorneyRates(id);
          setRates(ratesData);

          const performance = await getAttorneyPerformance(id);
          setPerformanceData(performance);
        }
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchData();
    }
  }, [id]);

  // LD1: Helper function to format the attorney's bar date for display
  const formatBarDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  };

  // LD1: Helper function to calculate the years of experience based on bar date
  const calculateYearsOfExperience = (barDate: string): number => {
    const bar = new Date(barDate);
    const now = new Date();
    return now.getFullYear() - bar.getFullYear();
  };

  // LD1: Function to render the attorney profile section
  const renderAttorneyProfile = (attorney: Attorney | null) => {
    if (!attorney) return <Typography>No attorney profile available.</Typography>;

    return (
      <Card title="Attorney Profile">
        <Typography variant="h6">
          <PersonOutline sx={{ marginRight: 1 }} />
          {attorney.name}
        </Typography>
        <Typography variant="body2">
          Bar Date: {formatBarDate(attorney.barDate)} ({calculateYearsOfExperience(attorney.barDate)} years of experience)
        </Typography>
        {/* Add more profile information here */}
      </Card>
    );
  };

  // LD1: Function to render the attorney's rate history section
  const renderRateHistory = (rates: Rate[]) => {
    if (!rates || rates.length === 0) return <Typography>No rate history available.</Typography>;

    return (
      <Card title="Rate History">
        <RateHistoryTimeline attorneyId={id} />
      </Card>
    );
  };

  // LD1: Function to render the attorney's performance metrics section
  const renderPerformanceMetrics = (performanceData: any) => {
    if (!performanceData) return <Typography>No performance metrics available.</Typography>;

    return (
      <Card title="Performance Metrics">
        <AttorneyPerformancePanel attorneyId={id} />
      </Card>
    );
  };

  // LD1: Function to render the attorney's current rates section
  const renderCurrentRates = (rates: Rate[]) => {
    if (!rates || rates.length === 0) return <Typography>No current rates available.</Typography>;

    return (
      <Card title="Current Rates">
        <RateTable rates={rates} mode="view" />
      </Card>
    );
  };

  // LD1: Handler function for editing attorney information
  const handleEditAttorney = () => {
    // Check user permissions for attorney editing
    if (can('update', 'attorneys', 'organization')) {
      // Navigate to the attorney edit form with the current attorney ID
      navigate(`/attorneys/${id}/edit`);
    } else {
      // Display a message if the user doesn't have permission
      alert('You do not have permission to edit this attorney.');
    }
  };

    // LD1: Handler function to return to the attorney list page
    const handleBackToList = () => {
        navigate('/attorneys/list');
    };

  // LD1: Render the component
  return (
    <MainLayout>
      <PageHeader
        title="Attorney Details"
        actions={
          <>
            {can('update', 'attorneys', 'organization') && (
              <Button variant="outlined" onClick={handleEditAttorney} startIcon={<EditOutlined />}>
                Edit Attorney
              </Button>
            )}
                        <Button variant="outlined" onClick={handleBackToList}>
                            Back to List
                        </Button>
          </>
        }
      />
      {loading && (
        <Box display="flex" justifyContent="center" alignItems="center" height={400}>
          <CircularProgress />
        </Box>
      )}
      {error && (
        <Alert severity="error">
          {error}
        </Alert>
      )}
      {!loading && !error && attorney && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            {renderAttorneyProfile(attorney)}
          </Grid>
          <Grid item xs={12} md={8}>
            <Tabs
              tabs={[
                { id: 'rates', label: 'Rates', icon: <AttachMoneyOutlined /> },
                { id: 'history', label: 'History', icon: <HistoryOutlined /> },
                { id: 'performance', label: 'Performance', icon: <AssessmentOutlined /> },
              ]}
              activeTab="rates"
              onChange={(tab) => console.log(`Switched to tab: ${tab}`)}
            />
            {renderCurrentRates(rates)}
            {renderRateHistory(rates)}
            {renderPerformanceMetrics(performanceData)}
          </Grid>
        </Grid>
      )}
    </MainLayout>
  );
};

export default AttorneyDetailPage;