import React, { useState, useEffect, useCallback } from 'react'; // React: ^18.0.0
import { useNavigate, useParams } from 'react-router-dom'; // React Router: ^6.4.0
import { Grid, Box, Typography, Card, MenuItem, FormControl, InputLabel, Select, Button, CircularProgress, Divider } from '@mui/material'; // MUI: ^5.14.0

import MainLayout from '../../components/layout/MainLayout';
import AttorneyPerformancePanel from '../../components/analytics/AttorneyPerformancePanel';
import AnalyticsFilters from '../../components/analytics/AnalyticsFilters';
import useAnalytics from '../../hooks/useAnalytics';
import useAuth from '../../hooks/useAuth';
import { AttorneyPerformanceData, AnalyticsFilters as AnalyticsFiltersType } from '../../types/analytics';
import { ROUTES } from '../../constants/routes';
import { getAttorneys } from '../../services/attorneys';

/**
 * React functional component that displays attorney performance analytics
 */
const AttorneyPerformancePage: React.FC = () => {
  // LD1: Initialize state for selectedAttorneyId, attorneys list, firms list, attorney performance data, and filters
  const [selectedAttorneyId, setSelectedAttorneyId] = useState<string | null>(null);
  const [attorneys, setAttorneys] = useState<any[]>([]);
  const [firms, setFirms] = useState<any[]>([]);
  const [attorneyPerformanceData, setAttorneyPerformanceData] = useState<AttorneyPerformanceData | null>(null);
  const [filters, setFilters] = useState<AnalyticsFiltersType>({});

  // LD1: Get authentication user information from useAuth hook
  const { currentUser } = useAuth();

  // LD1: Get analytics functions from useAnalytics hook
  const { fetchAttorneyPerformance } = useAnalytics();

  // LD1: Initialize navigation and URL parameters
  const navigate = useNavigate();
  const { attorneyId } = useParams<{ attorneyId: string }>();

  // LD1: Create effect to fetch attorneys and firms data on component mount
  useEffect(() => {
    // Fetch attorneys and firms data here
    const fetchInitialData = async () => {
      try {
        const attorneyData = await getAttorneys();
        setAttorneys(attorneyData.items);

        // TODO: Fetch firms data if needed
        // const firmsData = await getFirms();
        // setFirms(firmsData);
      } catch (error) {
        console.error('Error fetching initial data:', error);
      }
    };

    fetchInitialData();
  }, []);

  // LD1: Create effect to fetch attorney performance data when selection changes
  useEffect(() => {
    if (attorneyId) {
      setSelectedAttorneyId(attorneyId);
      // Fetch attorney performance data
      fetchAttorneyPerformance({
        attorneyId: attorneyId,
        filters: filters,
        metricTypes: [], // Specify metric types if needed
        includeUniCourtData: true,
      });
    }
  }, [attorneyId, fetchAttorneyPerformance, filters]);

  // LD1: Implement handler for attorney selection changes
  const handleAttorneyChange = (event: React.ChangeEvent<{ value: any }>) => {
    const newAttorneyId = event.target.value;
    setSelectedAttorneyId(newAttorneyId);
    navigate(ROUTES.ATTORNEY_PERFORMANCE.replace(':attorneyId', newAttorneyId));
  };

  // LD1: Implement handler for analytics filter changes
  const handleAnalyticsFilterChange = (newFilters: AnalyticsFiltersType) => {
    setFilters(newFilters);
  };

  // LD1: Render layout with filters, attorney selection, and performance panel
  return (
    <MainLayout>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Typography variant="h4">Attorney Performance Analytics</Typography>
        </Grid>
        <Grid item xs={12}>
          <Card>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth>
                  <InputLabel id="attorney-select-label">Select Attorney</InputLabel>
                  <Select
                    labelId="attorney-select-label"
                    id="attorney-select"
                    value={selectedAttorneyId || ''}
                    label="Select Attorney"
                    onChange={handleAttorneyChange}
                  >
                    {attorneys.map((attorney) => (
                      <MenuItem key={attorney.id} value={attorney.id}>
                        {attorney.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={8}>
                <AnalyticsFilters onFilterChange={handleAnalyticsFilterChange} />
              </Grid>
            </Grid>
          </Card>
        </Grid>
        <Grid item xs={12}>
          {selectedAttorneyId && (
            <AttorneyPerformancePanel attorneyId={selectedAttorneyId} initialFilters={filters} />
          )}
        </Grid>
      </Grid>
    </MainLayout>
  );
};

export default AttorneyPerformancePage;