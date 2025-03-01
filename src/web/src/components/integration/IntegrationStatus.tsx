/**
 * IntegrationStatus.tsx
 * 
 * A React component that displays the status of an external system integration,
 * including connection status, last sync time, and error information.
 * Provides visual indicators and action buttons for testing connections and syncing data.
 */

import React from 'react'; // ^18.0.0
import { useSelector, useDispatch } from 'react-redux'; // ^8.0.5
import { StatusIndicator } from '../common/StatusIndicator';
import { Button } from '../common/Button';
import { Card } from '../common/Card';
import { Tooltip } from '../common/Tooltip';
import { formatDate } from '../../utils/date';
import { 
  Integration, 
  IntegrationStatus as IntegrationStatusEnum,
  IntegrationType
} from '../../types/integration';
import { 
  selectIntegrationById 
} from '../../store/integrations/integrationsSlice';
import { 
  testConnection, 
  syncData 
} from '../../store/integrations/integrationsThunks';

/**
 * Returns the appropriate color based on the integration status
 * @param status The integration status
 * @returns A color string for the status
 */
const getStatusColor = (status: IntegrationStatusEnum): string => {
  switch (status) {
    case IntegrationStatusEnum.CONNECTED:
      return 'success';
    case IntegrationStatusEnum.ERROR:
      return 'error';
    case IntegrationStatusEnum.SYNCING:
    case IntegrationStatusEnum.TESTING:
      return 'warning';
    case IntegrationStatusEnum.DISCONNECTED:
    default:
      return 'neutral';
  }
};

/**
 * Returns a human-readable text description for the integration status
 * @param status The integration status
 * @returns A string representation of the status
 */
const getStatusText = (status: IntegrationStatusEnum): string => {
  switch (status) {
    case IntegrationStatusEnum.CONNECTED:
      return 'Connected';
    case IntegrationStatusEnum.ERROR:
      return 'Error';
    case IntegrationStatusEnum.SYNCING:
      return 'Syncing...';
    case IntegrationStatusEnum.TESTING:
      return 'Testing...';
    case IntegrationStatusEnum.DISCONNECTED:
      return 'Disconnected';
    default:
      return 'Unknown';
  }
};

/**
 * Props interface for the IntegrationStatus component
 */
interface IntegrationStatusProps {
  integrationId: string;
  onSync?: () => void;
  onTest?: () => void;
  showActions?: boolean;
}

/**
 * Component that displays the status of an integration and provides actions to test or sync
 * 
 * @param props Component properties
 * @returns JSX element
 */
const IntegrationStatus: React.FC<IntegrationStatusProps> = ({
  integrationId,
  onSync,
  onTest,
  showActions = true
}) => {
  const dispatch = useDispatch();
  const integration = useSelector(state => selectIntegrationById(state, integrationId));

  if (!integration) {
    return (
      <Card padding="sm">
        <div>Integration not found</div>
      </Card>
    );
  }

  /**
   * Handles the test connection button click
   */
  const handleTestConnection = () => {
    dispatch(testConnection({ 
      type: integration.type,
      configuration: integration.configuration
    }));
    if (onTest) onTest();
  };

  /**
   * Handles the sync data button click
   */
  const handleSync = () => {
    if (integration.type === IntegrationType.EBILLING || 
        integration.type === IntegrationType.LAWFIRM) {
      dispatch(syncData({ 
        integrationId, 
        importRequest: {
          integrationId,
          dataType: 'all',
          mappingSetId: 'default', // Use default mapping set
          filters: null,
          options: null
        }
      }));
    }
    if (onSync) onSync();
  };

  // Get status color and text
  const statusColor = integration.status ? 
    getStatusColor(integration.status as IntegrationStatusEnum) : 'neutral';
  const statusText = integration.status ? 
    getStatusText(integration.status as IntegrationStatusEnum) : 'Unknown';

  // Format the last sync date if available
  const lastSyncFormatted = integration.lastSyncDate ? 
    formatDate(integration.lastSyncDate, 'MMM d, yyyy h:mm a') : 'Never';

  return (
    <Card>
      <div style={{ padding: '16px' }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          marginBottom: '16px'
        }}>
          <div>
            <h3 style={{ margin: 0, marginBottom: '4px' }}>{integration.name}</h3>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <StatusIndicator status={statusText} color={statusColor} showDot={true} />
              {integration.status === IntegrationStatusEnum.ERROR && integration.error && (
                <Tooltip content={integration.error} position="right">
                  <span style={{ marginLeft: '8px', cursor: 'help', color: '#E53E3E' }}>
                    <i>Info</i>
                  </span>
                </Tooltip>
              )}
            </div>
          </div>
          {showActions && (
            <div style={{ display: 'flex', gap: '8px' }}>
              <Button 
                size="small" 
                variant="outline" 
                onClick={handleTestConnection}
                disabled={integration.status === IntegrationStatusEnum.TESTING || 
                          integration.status === IntegrationStatusEnum.SYNCING}
                aria-label="Test connection"
              >
                Test Connection
              </Button>
              <Button 
                size="small" 
                variant="primary" 
                onClick={handleSync}
                disabled={integration.status === IntegrationStatusEnum.TESTING || 
                          integration.status === IntegrationStatusEnum.SYNCING ||
                          integration.status === IntegrationStatusEnum.DISCONNECTED}
                aria-label="Sync data"
              >
                Sync Data
              </Button>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Type:</span>
            <span style={{ fontWeight: 'bold' }}>
              {integration.type.charAt(0).toUpperCase() + integration.type.slice(1)}
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Last Sync:</span>
            <span>{lastSyncFormatted}</span>
          </div>
          {integration.configuration && 'systemType' in integration.configuration && (
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>System:</span>
              <span>{(integration.configuration as any).systemType}</span>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};

export default IntegrationStatus;