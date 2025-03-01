import React, { useState, useEffect, useCallback } from 'react'; // React library for building UI components //  ^18.2.0
import { useDispatch, useSelector } from 'react-redux'; //  ^8.1.1
import {
  Grid, Box, Typography, IconButton, Dialog, DialogTitle, DialogContent, DialogActions,
} from '@mui/material'; // @mui/material ^5.14.0
import {
  AddOutlined, DeleteOutlined, VisibilityOutlined, EditOutlined, ShareOutlined,
} from '@mui/icons-material'; // @mui/icons-material ^5.14.0

import MainLayout from '../../components/layout/MainLayout';
import PageHeader from '../../components/layout/PageHeader';
import CustomReportBuilder from '../../components/analytics/CustomReportBuilder';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import SearchBar from '../../components/common/SearchBar';
import Spinner from '../../components/common/Spinner';
import Toast from '../../components/common/Toast';
import EmptyState from '../../components/common/EmptyState';
import AIChatInterface from '../../components/ai/AIChatInterface';
import { Tab, Tabs } from '../../components/common/Tabs';
import { CustomReport } from '../../types/analytics';
import { fetchCustomReports, deleteCustomReport, shareCustomReport } from '../../store/analytics/analyticsThunks';
import { analyticsSelectors } from '../../store/analytics/analyticsSlice';
import { usePermissions } from '../../hooks/usePermissions';

/**
 * Main component for the Custom Reports page
 */
const CustomReportsPage: React.FC = () => {
  // LD1: Initialize state for activeTab with useState, default to 'list'
  const [activeTab, setActiveTab] = useState<'list' | 'builder'>('list');

  // LD1: Initialize state for searchQuery with useState, default to empty string
  const [searchQuery, setSearchQuery] = useState<string>('');

  // LD1: Initialize state for selectedReport with useState, default to null
  const [selectedReport, setSelectedReport] = useState<CustomReport | null>(null);

  // LD1: Initialize state for isCreateMode with useState, default to false
  const [isCreateMode, setIsCreateMode] = useState<boolean>(false);

  // LD1: Initialize state for shareDialogOpen with useState, default to false
  const [shareDialogOpen, setShareDialogOpen] = useState<boolean>(false);

  // LD1: Initialize state for deleteDialogOpen with useState, default to false
  const [deleteDialogOpen, setDeleteDialogOpen] = useState<boolean>(false);

  // LD1: Check permissions using usePermissions hook to verify user can access custom reports
  const { can } = usePermissions();

  // LD1: Use useSelector with selectCustomReports to get reports data from Redux
  const reports = useSelector(analyticsSelectors.selectCustomReports);

  // LD1: Set up dispatch function using useDispatch
  const dispatch = useDispatch();

  // LD1: Define handleTabChange function to switch between reports list and report builder
  const handleTabChange = (newTabValue: 'list' | 'builder') => {
    setActiveTab(newTabValue);
    if (newTabValue === 'list') {
      setSelectedReport(null);
      setIsCreateMode(false);
    }
  };

  // LD1: Define handleCreateNew function to enter create mode for a new report
  const handleCreateNew = () => {
    setIsCreateMode(true);
    setSelectedReport(null);
    setActiveTab('builder');
  };

  // LD1: Define handleEditReport function to edit an existing report
  const handleEditReport = (report: CustomReport) => {
    setSelectedReport(report);
    setIsCreateMode(false);
    setActiveTab('builder');
  };

  // LD1: Define handleViewReport function to view a report in read-only mode
  const handleViewReport = (report: CustomReport) => {
    setSelectedReport(report);
    setIsCreateMode(false);
    setActiveTab('builder');
  };

  // LD1: Define handleDeleteReport function to delete a report after confirmation
  const handleDeleteReport = (report: CustomReport) => {
    setSelectedReport(report);
    setDeleteDialogOpen(true);
  };

  // LD1: Define handleShareReport function to share a report with other users
  const handleShareReport = (report: CustomReport) => {
    setSelectedReport(report);
    setShareDialogOpen(true);
  };

  // LD1: Define handleSearch function to filter reports based on search query
  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  // LD1: Implement useEffect to fetch reports list on component mount
  useEffect(() => {
    dispatch(fetchCustomReports());
  }, [dispatch]);

  // LD1: Implement filtered reports logic based on searchQuery
  const filteredReports = reports
    ? reports.filter((report) => report.name.toLowerCase().includes(searchQuery.toLowerCase()))
    : [];

  // LD1: Define confirmDelete function to dispatch delete action
  const confirmDelete = () => {
    if (selectedReport) {
      dispatch(deleteCustomReport(selectedReport.id));
      setDeleteDialogOpen(false);
      setToastOpen(true);
    }
  };

  // LD1: Define confirmShare function to dispatch share action
  const confirmShare = (userIds: string[]) => {
    if (selectedReport) {
      dispatch(shareCustomReport({ reportId: selectedReport.id, userIds }));
      setShareDialogOpen(false);
      setToastOpen(true);
    }
  };

  // LD1: Render JSX with MainLayout as the outer container
  return (
    <MainLayout>
      {/* LD1: Include PageHeader with 'Custom Reports' title and Create button */}
      <PageHeader
        title="Custom Reports"
        actions={
          can('create', 'reports', 'organization') && (
            <Button variant="contained" startIcon={<AddOutlined />} onClick={handleCreateNew}>
              Create New Report
            </Button>
          )
        }
      />

      {/* LD1: Include Tabs component for navigation between list and builder views */}
      <Tabs
        tabs={[
          { id: 'list', label: 'Reports List' },
          { id: 'builder', label: 'Report Builder' },
        ]}
        activeTab={activeTab}
        onChange={handleTabChange}
      />

      {/* LD1: Conditionally render reports list or report builder based on activeTab */}
      {activeTab === 'list' ? (
        renderReportsList()
      ) : (
        renderReportBuilder()
      )}

      {/* LD1: Confirmation dialog for delete action */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Report</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to delete this report?</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={confirmDelete} variant="contained" color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* LD1: Confirmation dialog for share action */}
      <Dialog open={shareDialogOpen} onClose={() => setShareDialogOpen(false)}>
        <DialogTitle>Share Report</DialogTitle>
        <DialogContent>
          <Typography>Select users to share this report with:</Typography>
          {/* TODO: Implement user selection component */}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShareDialogOpen(false)}>Cancel</Button>
          <Button onClick={() => confirmShare([])} variant="contained" color="primary">
            Share
          </Button>
        </DialogActions>
      </Dialog>

      {/* LD1: Toast component for displaying success/error messages */}
      <Toast open={toastOpen} message="Action completed successfully" severity="success" onClose={() => setToastOpen(false)} />
    </MainLayout>
  );

  // LD1: Define renderReportsList function to render the list of custom reports
  function renderReportsList() {
    // LD1: Calculate filtered reports based on searchQuery
    const reportsToDisplay = filteredReports;

    // LD1: Return JSX with Card component as container
    return (
      <Card>
        {/* LD1: Include SearchBar component for filtering reports */}
        <SearchBar placeholder="Search reports" onSearch={handleSearch} />

        {/* LD1: Show loading spinner when loading state is true */}
        {isLoading && <Spinner />}

        {/* LD1: Show EmptyState component when no reports exist or all are filtered out */}
        {reportsToDisplay.length === 0 ? (
          <EmptyState title="No custom reports found" message="Create a new report to start analyzing your data." icon={<BarChart />} />
        ) : (
          <Grid container spacing={2} mt={2}>
            {/* LD1: Render reports list with Grid layout when reports exist */}
            {reportsToDisplay.map((report) => (
              <Grid item xs={12} sm={6} md={4} key={report.id}>
                <Card>
                  <Typography variant="h6">{report.name}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    {report.description}
                  </Typography>
                  <Box mt={2} display="flex" justifyContent="flex-end">
                    {/* LD1: Include action buttons for each report (view, edit, share, delete) */}
                    <IconButton aria-label="View" onClick={() => handleViewReport(report)}>
                      <VisibilityOutlined />
                    </IconButton>
                    <IconButton aria-label="Edit" onClick={() => handleEditReport(report)}>
                      <EditOutlined />
                    </IconButton>
                    <IconButton aria-label="Share" onClick={() => handleShareReport(report)}>
                      <ShareOutlined />
                    </IconButton>
                    <IconButton aria-label="Delete" onClick={() => handleDeleteReport(report)}>
                      <DeleteOutlined />
                    </IconButton>
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
        {/* LD1: Include 'Create New Report' button at the bottom */}
        <Box mt={2} display="flex" justifyContent="center">
          <Button variant="contained" startIcon={<AddOutlined />} onClick={handleCreateNew}>
            Create New Report
          </Button>
        </Box>
      </Card>
    );
  }

  // LD1: Define renderReportBuilder function to render the custom report builder/viewer component
  function renderReportBuilder() {
    // LD1: Return JSX with CustomReportBuilder component
    return (
      <CustomReportBuilder
        selectedReport={selectedReport}
        isCreateMode={isCreateMode}
        onSave={(report) => {
          // TODO: Implement save report logic
          console.log('Saving report:', report);
        }}
        onCancel={() => {
          // TODO: Implement cancel report logic
          setActiveTab('list');
          setSelectedReport(null);
          setIsCreateMode(false);
        }}
      />
    );
  }
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default CustomReportsPage;