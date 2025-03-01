import React, { useState, useEffect, useCallback } from 'react'; //  ^18.2.0
import { useDispatch, useSelector } from 'react-redux'; //  ^8.1.1
import {
  Box,
  Typography,
  Grid,
  IconButton,
  Tooltip,
  Divider
} from '@mui/material'; //  ^5.14.0
import {
  Add,
  Edit,
  Delete,
  Visibility,
  VisibilityOff,
  ContentCopy
} from '@mui/icons-material'; //  ^5.14.0
import Button from '../common/Button';
import TextField from '../common/TextField';
import Select from '../common/Select';
import Card from '../common/Card';
import ConfirmationDialog from '../common/ConfirmationDialog';
import Toast from '../common/Toast';
import {
  IntegrationType,
  APIKey as APIKeyType,
  AuthMethodType
} from '../../types/integration';
import {
  addApiKey,
  updateApiKey,
  deleteApiKey,
  fetchApiKeys
} from '../../store/integrations/integrationsThunks';
import {
  selectApiKeys,
  selectApiKeyLoading
} from '../../store/integrations/integrationsSlice';

/**
 * Utility function to mask sensitive API key for display
 * @param apiKey - The API key to mask
 * @returns Masked API key
 */
const maskApiKey = (apiKey: string): string => {
  if (apiKey.length < 8) {
    return '*'.repeat(apiKey.length);
  }
  const visibleChars = 4;
  const maskedLength = apiKey.length - (visibleChars * 2);
  return `${apiKey.substring(0, visibleChars)}${'*'.repeat(maskedLength)}${apiKey.substring(apiKey.length - visibleChars)}`;
};

/**
 * Utility function to group API keys by their integration type
 * @param apiKeys - Array of API keys
 * @returns Grouped API keys
 */
const groupApiKeysByType = (apiKeys: APIKeyType[]): Record<IntegrationType, APIKeyType[]> => {
  return apiKeys.reduce((groupedKeys: Record<IntegrationType, APIKeyType[]>, key) => {
    if (!groupedKeys[key.integrationType]) {
      groupedKeys[key.integrationType] = [];
    }
    groupedKeys[key.integrationType].push(key);
    return groupedKeys;
  }, {} as Record<IntegrationType, APIKeyType[]>);
};

/**
 * Custom hook for managing API key form state
 * @param initialKey - Initial API key
 * @returns Form state and handlers
 */
const useAPIKeyForm = (initialKey: APIKeyType | null = null) => {
  const [name, setName] = useState(initialKey?.name || '');
  const [integrationType, setIntegrationType] = useState<IntegrationType>(initialKey?.integrationType || IntegrationType.EBILLING);
  const [authMethod, setAuthMethod] = useState<AuthMethodType>(initialKey?.authMethod || AuthMethodType.API_KEY);
  const [apiKey, setApiKey] = useState(initialKey?.apiKey || '');
  const [clientId, setClientId] = useState(initialKey?.clientId || '');
  const [clientSecret, setClientSecret] = useState(initialKey?.clientSecret || '');
  const [username, setUsername] = useState(initialKey?.username || '');
  const [password, setPassword] = useState(initialKey?.password || '');

  const resetForm = useCallback(() => {
    setName('');
    setIntegrationType(IntegrationType.EBILLING);
    setAuthMethod(AuthMethodType.API_KEY);
    setApiKey('');
    setClientId('');
    setClientSecret('');
    setUsername('');
    setPassword('');
  }, []);

  return {
    name, setName,
    integrationType, setIntegrationType,
    authMethod, setAuthMethod,
    apiKey, setApiKey,
    clientId, setClientId,
    clientSecret, setClientSecret,
    username, setUsername,
    password, setPassword,
    resetForm
  };
};

/**
 * Component for displaying an individual API key with actions
 * @param props - API key card properties
 * @returns The rendered component
 */
const APIKeyCard: React.FC<{ apiKey: APIKeyType; onEdit: (apiKey: APIKeyType) => void; onDelete: (apiKey: APIKeyType) => void }> = ({ apiKey, onEdit, onDelete }) => {
  const [visible, setVisible] = useState(false);

  const toggleVisibility = () => {
    setVisible(!visible);
  };

  const copyKeyToClipboard = () => {
    navigator.clipboard.writeText(apiKey.apiKey);
  };

  return (
    <Card>
      <Typography variant="h6">{apiKey.name}</Typography>
      <Typography variant="subtitle2">Type: {apiKey.integrationType}</Typography>
      <Typography variant="body2">
        Key: {visible ? apiKey.apiKey : maskApiKey(apiKey.apiKey)}
        <IconButton onClick={toggleVisibility} size="small" aria-label="toggle visibility">
          {visible ? <VisibilityOff /> : <Visibility />}
        </IconButton>
        <IconButton onClick={copyKeyToClipboard} size="small" aria-label="copy to clipboard">
          <ContentCopy />
        </IconButton>
      </Typography>
      <Typography variant="caption">Created: {apiKey.createdAt}</Typography>
      <Typography variant="caption">Updated: {apiKey.updatedAt}</Typography>
      <Box mt={2}>
        <Button variant="outlined" size="small" onClick={() => onEdit(apiKey)}>
          <Edit fontSize="small" /> Edit
        </Button>
        <Button variant="text" size="small" color="error" onClick={() => onDelete(apiKey)}>
          <Delete fontSize="small" /> Delete
        </Button>
      </Box>
    </Card>
  );
};

/**
 * Form component for adding or editing an API key
 * @param props - API key form properties
 * @returns The rendered component
 */
const APIKeyForm: React.FC<{ integrationType: IntegrationType; authMethod: AuthMethodType; apiKey: string; clientId: string; clientSecret: string; username: string; password: string; name: string; setName: (name: string) => void; setIntegrationType: (integrationType: IntegrationType) => void; setAuthMethod: (authMethod: AuthMethodType) => void; setApiKey: (apiKey: string) => void; setClientId: (clientId: string) => void; setClientSecret: (clientSecret: string) => void; setUsername: (username: string) => void; setPassword: (password: string) => void; onSubmit: () => void; onCancel: () => void }> = ({ integrationType, authMethod, apiKey, clientId, clientSecret, username, password, name, setName, setIntegrationType, setAuthMethod, setApiKey, setClientId, setClientSecret, setUsername, setPassword, onSubmit, onCancel }) => {
  return (
    <Box>
      <TextField
        label="Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
        fullWidth
      />
      <Select
        label="Integration Type"
        value={integrationType}
        onChange={(value) => setIntegrationType(value as IntegrationType)}
        options={[
          { value: IntegrationType.EBILLING, label: 'eBilling System' },
          { value: IntegrationType.LAWFIRM, label: 'Law Firm Billing System' },
          { value: IntegrationType.UNICOURT, label: 'UniCourt' },
        ]}
        required
        fullWidth
      />
      <Select
        label="Authentication Method"
        value={authMethod}
        onChange={(value) => setAuthMethod(value as AuthMethodType)}
        options={[
          { value: AuthMethodType.API_KEY, label: 'API Key' },
          { value: AuthMethodType.OAUTH, label: 'OAuth 2.0' },
          { value: AuthMethodType.BASIC, label: 'Basic Auth' },
        ]}
        required
        fullWidth
      />
      {authMethod === AuthMethodType.API_KEY && (
        <TextField
          label="API Key"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          required
          fullWidth
        />
      )}
      {authMethod === AuthMethodType.OAUTH && (
        <>
          <TextField
            label="Client ID"
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            required
            fullWidth
          />
          <TextField
            label="Client Secret"
            type="password"
            value={clientSecret}
            onChange={(e) => setClientSecret(e.target.value)}
            required
            fullWidth
          />
        </>
      )}
      {authMethod === AuthMethodType.BASIC && (
        <>
          <TextField
            label="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            fullWidth
          />
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            fullWidth
          />
        </>
      )}
      <Box mt={2} display="flex" justifyContent="flex-end">
        <Button variant="outlined" onClick={onCancel}>Cancel</Button>
        <Button onClick={onSubmit}>Submit</Button>
      </Box>
    </Box>
  );
};

/**
 * Main component for managing API keys and authentication credentials for external system integrations
 * @param props - Component properties (none defined)
 * @returns The rendered component
 */
const APIKeyManager: React.FC = () => {
  // Redux dispatch and selectors
  const dispatch = useDispatch();
  const apiKeys = useSelector(selectApiKeys);
  const apiKeyLoading = useSelector(selectApiKeyLoading);

  // Local state for managing the selected integration type and form visibility
  const [selectedIntegrationType, setSelectedIntegrationType] = useState<IntegrationType>(IntegrationType.EBILLING);
  const [showForm, setShowForm] = useState(false);
  const [editingKey, setEditingKey] = useState<APIKeyType | null>(null);
  const [confirmDeleteDialogOpen, setConfirmDeleteDialogOpen] = useState(false);
  const [keyToDelete, setKeyToDelete] = useState<APIKeyType | null>(null);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastSeverity, setToastSeverity] = useState<'success' | 'info' | 'warning' | 'error'>('info');

  // Form state using custom hook
  const {
    name, setName,
    integrationType, setIntegrationType,
    authMethod, setAuthMethod,
    apiKey, setApiKey,
    clientId, setClientId,
    clientSecret, setClientSecret,
    username, setUsername,
    password, setPassword,
    resetForm
  } = useAPIKeyForm(editingKey);

  // Fetch API keys on component mount
  useEffect(() => {
    dispatch(fetchApiKeys());
  }, [dispatch]);

  // Group API keys by integration type
  const groupedApiKeys = groupApiKeysByType(apiKeys);

  // Handlers for form submission, edit, delete, and copy
  const handleSubmit = () => {
    const apiKeyData: Partial<APIKeyType> = {
      name,
      integrationType,
      authMethod,
      apiKey,
      clientId,
      clientSecret,
      username,
      password
    };

    if (editingKey) {
      dispatch(updateApiKey({ apiKeyId: editingKey.id, apiKeyData }));
    } else {
      dispatch(addApiKey(apiKeyData));
    }

    setShowForm(false);
    setEditingKey(null);
    resetForm();
    setToastMessage('API Key saved successfully!');
    setToastSeverity('success');
    setToastOpen(true);
  };

  const handleEdit = (apiKey: APIKeyType) => {
    setEditingKey(apiKey);
    setName(apiKey.name);
    setIntegrationType(apiKey.integrationType);
    setAuthMethod(apiKey.authMethod);
    setApiKey(apiKey.apiKey);
    setClientId(apiKey.clientId);
    setClientSecret(apiKey.clientSecret);
    setUsername(apiKey.username);
    setPassword(apiKey.password);
    setShowForm(true);
  };

  const handleDelete = (apiKey: APIKeyType) => {
    setKeyToDelete(apiKey);
    setConfirmDeleteDialogOpen(true);
  };

  const handleConfirmDelete = () => {
    if (keyToDelete) {
      dispatch(deleteApiKey(keyToDelete.id));
      setConfirmDeleteDialogOpen(false);
      setKeyToDelete(null);
      setToastMessage('API Key deleted successfully!');
      setToastSeverity('success');
      setToastOpen(true);
    }
  };

  const handleCancelDelete = () => {
    setConfirmDeleteDialogOpen(false);
    setKeyToDelete(null);
  };

  const handleCloseToast = (event: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setToastOpen(false);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingKey(null);
    resetForm();
  };

  // Render the component
  return (
    <Box>
      <Typography variant="h4" gutterBottom>API Key Management</Typography>
      <Select
        label="Integration Type"
        value={selectedIntegrationType}
        onChange={(value) => setSelectedIntegrationType(value as IntegrationType)}
        options={[
          { value: IntegrationType.EBILLING, label: 'eBilling System' },
          { value: IntegrationType.LAWFIRM, label: 'Law Firm Billing System' },
          { value: IntegrationType.UNICOURT, label: 'UniCourt' },
        ]}
        fullWidth
      />
      <Box mt={2} display="flex" justifyContent="flex-end">
        <Button variant="contained" onClick={() => setShowForm(true)}>
          <Add fontSize="small" /> Add API Key
        </Button>
      </Box>
      <Divider style={{ margin: '16px 0' }} />
      <Grid container spacing={2}>
        {groupedApiKeys[selectedIntegrationType]?.map((apiKey) => (
          <Grid item xs={12} sm={6} md={4} key={apiKey.id}>
            <APIKeyCard apiKey={apiKey} onEdit={handleEdit} onDelete={handleDelete} />
          </Grid>
        ))}
      </Grid>
      {showForm && (
        <Box mt={3}>
          <Card>
            <Typography variant="h5" gutterBottom>{editingKey ? 'Edit API Key' : 'Add API Key'}</Typography>
            <APIKeyForm
              name={name}
              setName={setName}
              integrationType={integrationType}
              setIntegrationType={setIntegrationType}
              authMethod={authMethod}
              setAuthMethod={setAuthMethod}
              apiKey={apiKey}
              setApiKey={setApiKey}
              clientId={clientId}
              setClientId={setClientId}
              clientSecret={clientSecret}
              setClientSecret={setClientSecret}
              username={username}
              setUsername={setUsername}
              password={password}
              setPassword={setPassword}
              onSubmit={handleSubmit}
              onCancel={handleCancelForm}
            />
          </Card>
        </Box>
      )}
      <ConfirmationDialog
        isOpen={confirmDeleteDialogOpen}
        title="Delete API Key"
        message="Are you sure you want to delete this API key? This action cannot be undone."
        confirmText="Delete"
        confirmButtonVariant="danger"
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
      />
      <Toast
        open={toastOpen}
        message={toastMessage}
        severity={toastSeverity}
        onClose={handleCloseToast}
      />
    </Box>
  );
};

export default APIKeyManager;