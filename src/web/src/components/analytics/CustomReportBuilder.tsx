import React, { useState, useEffect, useCallback } from 'react'; //  ^18.2.0
import { useDispatch, useSelector } from 'react-redux'; //  ^8.1.1
import {
  Grid, Box, Typography, Tab, Tabs, IconButton, Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material'; // @mui/material ^5.14.0
import {
  AddCircleOutline, Delete, Share, Visibility, Edit, Save
} from '@mui/icons-material'; // @mui/icons-material ^5.14.0

import Card from '../common/Card';
import TextField from '../common/TextField';
import Button from '../common/Button';
import Select from '../common/Select';
import Checkbox from '../common/Checkbox';
import AnalyticsFilters from './AnalyticsFilters';
import ExportControls from './ExportControls';
import BarChart from '../charts/BarChart';
import LineChart from '../charts/LineChart';
import PieChart from '../charts/PieChart';
import {
  createCustomReport, getCustomReports, updateCustomReport, deleteCustomReport, shareCustomReport
} from '../../store/analytics/analyticsThunks';
import {
  selectCustomReports, selectAvailableFields, selectIsLoading
} from '../../store/analytics/analyticsSlice';
import {
  CustomReport, ReportField, ReportFilter, VisualizationType
} from '../../types/analytics';
import Spinner from '../common/Spinner';
import Toast from '../common/Toast';

/**
 * A component for building, previewing, and managing custom analytics reports
 */
const CustomReportBuilder: React.FC = () => {
  // LD1: Initialize Redux dispatch
  const dispatch = useDispatch();

  // LD1: Select data from Redux store
  const customReports = useSelector(selectCustomReports);
  const availableFields = useSelector(selectAvailableFields);
  const isLoading = useSelector(selectIsLoading);

  // LD1: Define local state variables
  const [reportName, setReportName] = useState<string>('');
  const [reportDescription, setReportDescription] = useState<string>('');
  const [selectedFields, setSelectedFields] = useState<string[]>([]);
  const [reportFilters, setReportFilters] = useState<ReportFilter[]>([]);
  const [visualizationType, setVisualizationType] = useState<VisualizationType>('BAR_CHART');
  const [previewData, setPreviewData] = useState<any>(null);
  const [reportId, setReportId] = useState<string | null>(null);
  const [isShareDialogOpen, setIsShareDialogOpen] = useState<boolean>(false);
  const [shareUsers, setShareUsers] = useState<string[]>([]);
  const [toastOpen, setToastOpen] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string>('');
  const [toastSeverity, setToastSeverity] = useState<'success' | 'info' | 'warning' | 'error'>('info');

  /**
   * Handles the selection and deselection of fields to include in the report
   * @param {React.ChangeEvent<HTMLInputElement>} event
   * @returns {void} No return value
   */
  const handleFieldSelection = (event: React.ChangeEvent<HTMLInputElement>): void => {
    // Extract the field ID from the event target value
    const fieldId = event.target.value;

    // Check if the field is already selected
    const isSelected = selectedFields.includes(fieldId);

    // Update the report configuration with the new selectedFields array
    setSelectedFields(prevFields =>
      isSelected ? prevFields.filter(id => id !== fieldId) : [...prevFields, fieldId]
    );
  };

  /**
   * Handles changes to the report filters
   * @param {ReportFilter[]} filters
   * @returns {void} No return value
   */
  const handleFilterChange = (filters: ReportFilter[]): void => {
    // Update the report configuration with the new filters
    setReportFilters(filters);
  };

  /**
   * Handles changes to the visualization type for the report
   * @param {React.ChangeEvent<HTMLSelectElement>} event
   * @returns {void} No return value
   */
  const handleVisualizationChange = (event: React.ChangeEvent<HTMLSelectElement>): void => {
    // Extract the visualization type from the event target value
    const visualization = event.target.value as VisualizationType;

    // Update the report configuration with the new visualization type
    setVisualizationType(visualization);
  };

  /**
   * Saves the current report configuration
   * @returns {void} No return value
   */
  const handleSaveReport = (): void => {
    // Validate that the report has a name and at least one selected field
    if (!reportName || selectedFields.length === 0) {
      setToastMessage('Report name and at least one selected field are required.');
      setToastSeverity('warning');
      setToastOpen(true);
      return;
    }

    // If reportId exists, dispatch updateCustomReport action
    if (reportId) {
      dispatch(updateCustomReport({
        id: reportId,
        name: reportName,
        description: reportDescription,
        reportType: 'custom', // TODO: Define report types
        filters: reportFilters,
        chartType: visualizationType,
        dimensions: [], // TODO: Implement dimensions
        metrics: selectedFields,
        sortBy: '', // TODO: Implement sorting
        sortDirection: '', // TODO: Implement sorting direction
        limit: 100 // TODO: Implement limit
      } as CustomReport));
      setToastMessage('Report updated successfully.');
      setToastSeverity('success');
    } else {
      // If reportId doesn't exist, dispatch createCustomReport action
      dispatch(createCustomReport({
        name: reportName,
        description: reportDescription,
        reportType: 'custom', // TODO: Define report types
        filters: reportFilters,
        chartType: visualizationType,
        dimensions: [], // TODO: Implement dimensions
        metrics: selectedFields,
        sortBy: '', // TODO: Implement sorting
        sortDirection: '', // TODO: Implement sorting direction
        limit: 100 // TODO: Implement limit
      }));
      setToastMessage('Report created successfully.');
      setToastSeverity('success');
    }
    setToastOpen(true);
  };

  /**
   * Opens a dialog to share the report with other users
   * @returns {void} No return value
   */
  const handleShareReport = (): void => {
    // Check if the report has been saved (has an ID)
    if (!reportId) {
      setToastMessage('Please save the report before sharing.');
      setToastSeverity('warning');
      setToastOpen(true);
      return;
    }

    // If saved, open the share dialog
    setIsShareDialogOpen(true);
  };

  /**
   * Generates a preview of the report with current configuration
   * @returns {void} No return value
   */
  const handleGeneratePreview = (): void => {
    // Set preview mode to true
    // Generate the visualization based on the selected fields, filters, and visualization type
    // Update the previewData state with the result
    console.log('Generating preview with:', {
      reportName,
      reportDescription,
      selectedFields,
      reportFilters,
      visualizationType
    });
  };

  /**
   * Renders the appropriate visualization component based on type
   * @param {VisualizationType} type
   * @param {any} data
   * @returns {ReactNode} The rendered visualization component
   */
  const renderVisualization = (type: VisualizationType, data: any): React.ReactNode => {
    switch (type) {
      case 'BAR_CHART':
        return <BarChart data={data} />;
      case 'LINE_CHART':
        return <LineChart data={data} />;
      case 'PIE_CHART':
        return <PieChart data={data} />;
      default:
        return <Typography>Select visualization type</Typography>;
    }
  };

  /**
   * Handles the submission of the share dialog
   * @param {string[]} users
   * @returns {void} No return value
   */
  const handleShareSubmit = (users: string[]): void => {
    // Dispatch the shareCustomReport action with the reportId and users array
    dispatch(shareCustomReport({ reportId, users }));

    // Handle success/error responses with appropriate toast messages
    setIsShareDialogOpen(false);
  };

  return (
    <Card>
      <Typography variant="h5">Custom Report Builder</Typography>
      <Grid container spacing={2} mt={2}>
        <Grid item xs={12} md={6}>
          <TextField
            label="Report Name"
            value={reportName}
            onChange={(e) => setReportName(e.target.value)}
            fullWidth
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            label="Report Description"
            value={reportDescription}
            onChange={(e) => setReportDescription(e.target.value)}
            fullWidth
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <Select
            label="Visualization Type"
            value={visualizationType}
            onChange={handleVisualizationChange}
            options={[
              { value: 'BAR_CHART', label: 'Bar Chart' },
              { value: 'LINE_CHART', label: 'Line Chart' },
              { value: 'PIE_CHART', label: 'Pie Chart' },
            ]}
            fullWidth
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle1">Select Fields</Typography>
          {availableFields && availableFields.map((field) => (
            <Checkbox
              key={field}
              label={field}
              value={field}
              checked={selectedFields.includes(field)}
              onChange={handleFieldSelection}
            />
          ))}
        </Grid>
        <Grid item xs={12}>
          <AnalyticsFilters onFilterChange={handleFilterChange} />
        </Grid>
        <Grid item xs={12}>
          <Button variant="contained" onClick={handleGeneratePreview} disabled={isLoading}>
            Generate Preview
          </Button>
        </Grid>
        <Grid item xs={12}>
          {previewData && renderVisualization(visualizationType, previewData)}
        </Grid>
        <Grid item xs={12}>
          <ExportControls
            data={previewData}
            title={reportName}
            onExport={(format) => console.log(`Exporting as ${format}`)}
            isLoading={isLoading}
            onSaveReport={handleSaveReport}
            onShareReport={handleShareReport}
          />
        </Grid>
      </Grid>

      {/* Share Dialog */}
      <Dialog open={isShareDialogOpen} onClose={() => setIsShareDialogOpen(false)}>
        <DialogTitle>Share Report</DialogTitle>
        <DialogContent>
          {/* TODO: Implement user selection component */}
          <Typography>Select users to share with:</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsShareDialogOpen(false)}>Cancel</Button>
          <Button onClick={() => handleShareSubmit(shareUsers)}>Share</Button>
        </DialogActions>
      </Dialog>

      {/* Toast Notification */}
      <Toast
        open={toastOpen}
        message={toastMessage}
        severity={toastSeverity}
        onClose={() => setToastOpen(false)}
      />
    </Card>
  );
};

export default CustomReportBuilder;