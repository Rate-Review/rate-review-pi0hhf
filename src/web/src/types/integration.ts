/**
 * @file Type definitions for integration-related functionality in the Justice Bid Rate Negotiation System.
 * @version 1.0.0
 */

/**
 * Enumeration of integration types supported by the system.
 */
export enum IntegrationType {
  /** Integration with client eBilling systems */
  EBILLING = 'ebilling',
  /** Integration with law firm billing systems */
  LAWFIRM = 'lawfirm',
  /** Integration with UniCourt for attorney performance data */
  UNICOURT = 'unicourt',
  /** File-based data import/export */
  FILE = 'file'
}

/**
 * Enumeration of supported eBilling systems.
 */
export enum EBillingSystemType {
  /** Onit eBilling system */
  ONIT = 'onit',
  /** TeamConnect eBilling system */
  TEAMCONNECT = 'teamconnect',
  /** Legal Tracker eBilling system */
  LEGAL_TRACKER = 'legal_tracker',
  /** BrightFlag eBilling system */
  BRIGHTFLAG = 'brightflag',
  /** Custom or other eBilling systems */
  OTHER = 'other'
}

/**
 * Enumeration of supported authentication methods for API integrations.
 */
export enum AuthMethodType {
  /** Authentication using API key */
  API_KEY = 'api_key',
  /** Authentication using OAuth 2.0 */
  OAUTH = 'oauth',
  /** Authentication using Basic Auth */
  BASIC = 'basic'
}

/**
 * Enumeration of data synchronization directions.
 */
export enum SyncDirection {
  /** Data import from external system to Justice Bid */
  IMPORT = 'import',
  /** Data export from Justice Bid to external system */
  EXPORT = 'export'
}

/**
 * Enumeration of synchronization job statuses.
 */
export enum SyncStatus {
  /** Job is pending execution */
  PENDING = 'pending',
  /** Job is currently running */
  IN_PROGRESS = 'in_progress',
  /** Job completed successfully */
  COMPLETED = 'completed',
  /** Job failed entirely */
  FAILED = 'failed',
  /** Job completed with some failures */
  PARTIAL = 'partial'
}

/**
 * Enumeration of supported file types for import/export.
 */
export enum FileType {
  /** Comma-separated values */
  CSV = 'csv',
  /** Microsoft Excel */
  EXCEL = 'excel',
  /** JSON format */
  JSON = 'json',
  /** XML format */
  XML = 'xml'
}

/**
 * Base interface for all integration configurations.
 */
export interface IntegrationConfig {
  /** Unique identifier for the integration */
  id: string;
  /** Display name for the integration */
  name: string;
  /** Organization that owns this integration */
  organizationId: string;
  /** Type of integration */
  type: IntegrationType;
  /** Current status of the integration (enabled/disabled) */
  status: string;
  /** Date when the integration was created */
  createdAt: Date;
  /** Date when the integration was last updated */
  updatedAt: Date;
  /** Date of the last successful synchronization */
  lastSyncDate: Date | null;
  /** Integration-specific configuration */
  configuration: unknown;
}

/**
 * Interface for eBilling system integration configuration.
 * Used for integrating with client eBilling systems like Onit, TeamConnect, etc.
 */
export interface EBillingIntegrationConfig extends IntegrationConfig {
  configuration: {
    /** Type of eBilling system */
    systemType: EBillingSystemType;
    /** Base URL for the eBilling system API */
    apiUrl: string;
    /** Authentication method used for the integration */
    authMethod: AuthMethodType;
    /** Authentication credentials */
    credentials: {
      /** API key if using API_KEY auth method */
      apiKey?: string;
      /** Client ID if using OAuth */
      clientId?: string;
      /** Client secret if using OAuth */
      clientSecret?: string;
      /** Username if using Basic auth */
      username?: string;
      /** Password if using Basic auth */
      password?: string;
      /** Additional authentication parameters */
      [key: string]: string | undefined;
    };
  };
}

/**
 * Interface for law firm billing system integration configuration.
 * Used for integrating with law firm billing systems.
 */
export interface LawFirmBillingIntegrationConfig extends IntegrationConfig {
  configuration: {
    /** Type of law firm billing system */
    systemType: string;
    /** Base URL for the law firm billing system API */
    apiUrl: string;
    /** Authentication method used for the integration */
    authMethod: AuthMethodType;
    /** Authentication credentials */
    credentials: {
      /** API key if using API_KEY auth method */
      apiKey?: string;
      /** Client ID if using OAuth */
      clientId?: string;
      /** Client secret if using OAuth */
      clientSecret?: string;
      /** Username if using Basic auth */
      username?: string;
      /** Password if using Basic auth */
      password?: string;
      /** Additional authentication parameters */
      [key: string]: string | undefined;
    };
  };
}

/**
 * Interface for UniCourt API integration configuration.
 * Used for retrieving attorney performance data from UniCourt.
 */
export interface UniCourtIntegrationConfig extends IntegrationConfig {
  configuration: {
    /** Base URL for the UniCourt API */
    apiUrl: string;
    /** API key for UniCourt authentication */
    apiKey: string;
    /** Schedule for refreshing data (cron expression) */
    refreshSchedule: string;
  };
}

/**
 * Interface for file import/export integration configuration.
 * Used for importing/exporting data via files.
 */
export interface FileIntegrationConfig extends IntegrationConfig {
  configuration: {
    /** Type of file for import/export */
    fileType: FileType;
    /** Default template ID for file import/export */
    defaultTemplateId: string | null;
  };
}

/**
 * Interface for mapping fields between Justice Bid and external systems.
 */
export interface FieldMapping {
  /** Unique identifier for the mapping */
  id: string;
  /** Field name in the source system */
  sourceField: string;
  /** Field name in the target system */
  targetField: string;
  /** Optional transformation function to apply during mapping */
  transformFunction: string | null;
  /** Whether this field is required */
  required: boolean;
  /** Description of the field mapping */
  description: string | null;
}

/**
 * Interface for a collection of field mappings for an integration.
 */
export interface FieldMappingSet {
  /** Unique identifier for the mapping set */
  id: string;
  /** Display name for the mapping set */
  name: string;
  /** Integration this mapping set belongs to */
  integrationId: string;
  /** Direction of data flow (import/export) */
  direction: SyncDirection;
  /** Collection of field mappings */
  mappings: FieldMapping[];
  /** Whether this is the default mapping set for the integration */
  isDefault: boolean;
  /** Date when the mapping set was created */
  createdAt: Date;
  /** Date when the mapping set was last updated */
  updatedAt: Date;
}

/**
 * Interface for test connection request payload.
 */
export interface TestConnectionRequest {
  /** Type of integration to test */
  type: IntegrationType;
  /** Integration configuration to test */
  configuration: {
    /** Type-specific configuration properties */
    [key: string]: unknown;
  };
}

/**
 * Interface for connection test result.
 */
export interface ConnectionTestResult {
  /** Whether the connection test was successful */
  success: boolean;
  /** Message describing the test result */
  message: string;
  /** When the test was performed */
  timestamp: Date;
  /** Additional details about the test result */
  details: object | null;
}

/**
 * Interface for data import request.
 */
export interface ImportDataRequest {
  /** Integration ID to import from */
  integrationId: string;
  /** Type of data to import (rates, attorneys, etc.) */
  dataType: string;
  /** Mapping set ID to use for the import */
  mappingSetId: string;
  /** Optional filters to apply to the import */
  filters: object | null;
  /** Additional import options */
  options: object | null;
}

/**
 * Interface for data export request.
 */
export interface ExportDataRequest {
  /** Integration ID to export to */
  integrationId: string;
  /** Type of data to export (rates, attorneys, etc.) */
  dataType: string;
  /** Mapping set ID to use for the export */
  mappingSetId: string;
  /** Optional filters to apply to the export */
  filters: object | null;
  /** Additional export options */
  options: object | null;
}

/**
 * Interface for tracking synchronization jobs.
 */
export interface SyncJob {
  /** Unique identifier for the sync job */
  id: string;
  /** Integration this job belongs to */
  integrationId: string;
  /** Direction of synchronization (import/export) */
  direction: SyncDirection;
  /** Type of data being synchronized */
  dataType: string;
  /** Current status of the sync job */
  status: SyncStatus;
  /** When the job started */
  startTime: Date;
  /** When the job ended (null if still running) */
  endTime: Date | null;
  /** Total number of records processed */
  recordsProcessed: number;
  /** Number of records successfully processed */
  recordsSucceeded: number;
  /** Number of records that failed processing */
  recordsFailed: number;
  /** Details about any errors encountered */
  errorDetails: string | null;
  /** User who created the sync job */
  createdBy: string;
}

/**
 * Interface for file templates used in import/export.
 */
export interface FileTemplate {
  /** Unique identifier for the template */
  id: string;
  /** Display name for the template */
  name: string;
  /** Description of the template */
  description: string;
  /** File type of the template */
  fileType: FileType;
  /** Type of data the template is for */
  dataType: string;
  /** URL to download the template */
  url: string;
}