import React, { useState, useCallback } from 'react'; // React v18.0.0
import { DownloadIcon, ShareIcon, SaveIcon } from '@mui/icons-material'; // @mui/icons-material v5.14.0
import { Box, Menu, MenuItem, Typography } from '@mui/material'; // @mui/material v5.14.0

import Button from '../common/Button';
import Select from '../common/Select';
import Tooltip from '../common/Tooltip';
import useAnalytics from '../../hooks/useAnalytics';
import usePermissions from '../../hooks/usePermissions';

/**
 * Type definition for the ExportControlsProps
 */
interface ExportControlsProps {
  data: any;
  title: string;
  onExport: (format: string) => void;
  isLoading: boolean;
  onSaveReport?: () => void;
  onShareReport?: () => void;
}

/**
 * Type definition for the ExportFormat enum
 */
type ExportFormat = 'CSV' | 'EXCEL' | 'PDF' | 'IMAGE';

/**
 * A functional component that renders export controls for analytics data
 * @param {ExportControlsProps} props - The component props
 * @returns {JSX.Element} The rendered export controls component
 */
const ExportControls: React.FC<ExportControlsProps> = (props) => {
  // LD1: Define state for export format selection
  const [format, setFormat] = useState<ExportFormat>('CSV');

  // LD1: Define state for export menu anchor element
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);

  // LD1: Define state for tracking whether an export operation is in progress
  const [isExporting, setIsExporting] = useState<boolean>(false);

  // IE1: Access the usePermissions hook
  const { can } = usePermissions();

  // LD1: Handle opening the export format menu
  const handleOpenMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  // LD1: Handle closing the export format menu
  const handleCloseMenu = () => {
    setAnchorEl(null);
  };

  // LD1: Handle format selection
  const handleFormatChange = (selectedFormat: ExportFormat) => {
    setFormat(selectedFormat);
    handleCloseMenu();
  };

  // LD1: Handle export action based on selected format
  const handleExport = useCallback(() => {
    setIsExporting(true);
    props.onExport(format);
    setTimeout(() => setIsExporting(false), 1000);
  }, [format, props]);

  // LD1: Handle save report action
  const handleSaveReport = () => {
    if (props.onSaveReport) {
      props.onSaveReport();
    }
  };

  // LD1: Handle share report action
  const handleShareReport = () => {
    if (props.onShareReport) {
      props.onShareReport();
    }
  };

  // LD1: Render export button with dropdown menu
  return (
    <Box display="flex" alignItems="center">
      <Button
        variant="outlined"
        color="primary"
        onClick={handleOpenMenu}
        disabled={props.isLoading}
        aria-controls={anchorEl ? 'export-menu' : undefined}
        aria-haspopup="true"
        aria-expanded={anchorEl ? 'true' : undefined}
      >
        Export
        <DownloadIcon sx={{ ml: 1 }} />
      </Button>
      <Menu
        id="export-menu"
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleCloseMenu}
        MenuListProps={{
          'aria-labelledby': 'export-button',
        }}
      >
        <MenuItem onClick={() => handleFormatChange('CSV')}>CSV</MenuItem>
        <MenuItem onClick={() => handleFormatChange('EXCEL')}>Excel</MenuItem>
        <MenuItem onClick={() => handleFormatChange('PDF')}>PDF</MenuItem>
        <MenuItem onClick={() => handleFormatChange('IMAGE')}>Image</MenuItem>
      </Menu>

      {/* LD1: Render export button */}
      <Tooltip content="Download data in selected format">
        <Button
          variant="contained"
          color="primary"
          onClick={handleExport}
          disabled={props.isLoading || isExporting}
          sx={{ ml: 2 }}
        >
          {props.isLoading || isExporting ? 'Exporting...' : 'Export'}
        </Button>
      </Tooltip>

      {/* LD1: Render save report button */}
      {props.onSaveReport && can('create', 'reports', 'organization') && (
        <Tooltip content="Save current report configuration">
          <Button
            variant="contained"
            color="secondary"
            onClick={handleSaveReport}
            disabled={props.isLoading}
            sx={{ ml: 2 }}
          >
            Save
            <SaveIcon sx={{ ml: 1 }} />
          </Button>
        </Tooltip>
      )}

      {/* LD1: Render share report button */}
      {props.onShareReport && can('share', 'reports', 'organization') && (
        <Tooltip content="Share current report with other users">
          <Button
            variant="contained"
            color="info"
            onClick={handleShareReport}
            disabled={props.isLoading}
            sx={{ ml: 2 }}
          >
            Share
            <ShareIcon sx={{ ml: 1 }} />
          </Button>
        </Tooltip>
      )}
    </Box>
  );
};

export default ExportControls;