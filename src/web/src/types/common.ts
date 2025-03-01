/**
 * Common TypeScript types, interfaces, and enums shared across the Justice Bid application.
 * This file includes API response structures, entity status enums, common data structures
 * for pagination/sorting/filtering, and other shared types.
 */

// Basic Types
export type ID = string;

// API Response Types
export interface ApiResponse<T> {
  data?: T;
  error?: ErrorResponse;
  meta?: ResponseMetadata;
}

export interface ErrorResponse {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface ResponseMetadata {
  timestamp: string;
  requestId: string;
}

// Pagination Types
export interface PaginationParams {
  page: number;
  pageSize: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Sorting Types
export type SortDirection = 'asc' | 'desc';

export interface SortParams {
  field: string;
  direction: SortDirection;
}

// Filter Types
export type FilterOperator = 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'contains' | 'in' | 'between';

export interface FilterParams {
  field: string;
  operator: FilterOperator;
  value: any;
}

// Entity Status Enums
export enum OrganizationType {
  CLIENT = 'CLIENT',
  LAW_FIRM = 'LAW_FIRM',
  ADMIN = 'ADMIN',
}

export enum RateType {
  STANDARD = 'STANDARD',
  APPROVED = 'APPROVED',
  PROPOSED = 'PROPOSED',
  COUNTER_PROPOSED = 'COUNTER_PROPOSED',
}

export enum RateStatus {
  DRAFT = 'DRAFT',
  SUBMITTED = 'SUBMITTED',
  UNDER_REVIEW = 'UNDER_REVIEW',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
}

export enum NegotiationStatus {
  REQUESTED = 'REQUESTED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  REJECTED = 'REJECTED',
}

export enum ApprovalStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
}

export enum OCGStatus {
  DRAFT = 'DRAFT',
  PUBLISHED = 'PUBLISHED',
  NEGOTIATING = 'NEGOTIATING',
  SIGNED = 'SIGNED',
}

// Common Metadata
export interface AuditMetadata {
  createdAt: string;
  createdBy: ID;
  updatedAt: string;
  updatedBy: ID;
}

// Date and Currency Types
export interface EffectiveDateRange {
  effectiveDate: string;
  expirationDate: string;
}

export type CurrencyCode = string; // Using ISO 4217 currency codes (e.g., 'USD', 'EUR', 'GBP')

export interface CurrencyAmount {
  amount: number;
  currency: CurrencyCode;
}

export interface DateRange {
  startDate: string;
  endDate: string;
}

// Integration Types
export enum IntegrationType {
  EBILLING = 'EBILLING',
  LAW_FIRM = 'LAW_FIRM',
  UNICOURT = 'UNICOURT',
  AI_PROVIDER = 'AI_PROVIDER',
  FILE_IMPORT = 'FILE_IMPORT',
  FILE_EXPORT = 'FILE_EXPORT',
}

export enum EBillingSystemType {
  ONIT = 'ONIT',
  TEAM_CONNECT = 'TEAM_CONNECT',
  LEGAL_TRACKER = 'LEGAL_TRACKER',
  BRIGHT_FLAG = 'BRIGHT_FLAG',
}

// Notification Types
export enum NotificationPriority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL',
}

export enum NotificationType {
  RATE_REQUEST = 'RATE_REQUEST',
  RATE_SUBMISSION = 'RATE_SUBMISSION',
  COUNTER_PROPOSAL = 'COUNTER_PROPOSAL',
  APPROVAL_REQUIRED = 'APPROVAL_REQUIRED',
  APPROVAL_COMPLETED = 'APPROVAL_COMPLETED',
  MESSAGE_RECEIVED = 'MESSAGE_RECEIVED',
  OCG_UPDATE = 'OCG_UPDATE',
  SYSTEM = 'SYSTEM',
}

// Redux Types
export interface ReduxStateSlice<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export interface ThunkApiConfig {
  rejectValue: { message: string };
}

// Common Data Structures
export interface Address {
  line1: string;
  line2?: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
}

export interface Office {
  id: ID;
  name: string;
  address: Address;
  isHeadquarters: boolean;
}

export interface HistoryEntry<T> {
  value: T;
  timestamp: string;
  userId: ID;
  message?: string;
}

export interface FileObject {
  id: ID;
  name: string;
  size: number;
  type: string;
  url: string;
  uploadProgress?: number;
}

// AI Types
export interface AIRecommendation<T = any> {
  recommendation: string;
  confidence: number;
  rationale: string;
  suggestedValue?: T;
}

// Analytics Types
export enum TimeframeSelection {
  LAST_7_DAYS = 'LAST_7_DAYS',
  LAST_30_DAYS = 'LAST_30_DAYS',
  LAST_90_DAYS = 'LAST_90_DAYS',
  LAST_12_MONTHS = 'LAST_12_MONTHS',
  YEAR_TO_DATE = 'YEAR_TO_DATE',
  CUSTOM = 'CUSTOM',
}

export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

export interface ChartDataSeries {
  name: string;
  data: ChartDataPoint[];
  color?: string;
}

// Error Types
export enum ErrorType {
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR = 'AUTHORIZATION_ERROR',
  NOT_FOUND_ERROR = 'NOT_FOUND_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR',
}