/**
 * Utility functions for browser storage operations, providing a type-safe interface
 * for storing and retrieving data with support for serialization, expiration, and namespacing.
 */

// Global constants
export const APP_STORAGE_PREFIX = 'justice_bid_';
export const FORM_DRAFT_EXPIRY_MS = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

/**
 * Enum for specifying which storage mechanism to use
 */
export enum StorageType {
  Local,
  Session
}

/**
 * Interface for storage items with expiration
 */
interface StorageItem<T> {
  value: T;
  expiry: number;
}

/**
 * Checks if a storage type is available in the current environment
 * 
 * @param type - The type of storage to check
 * @returns True if storage is available, false otherwise
 */
function isStorageAvailable(type: StorageType): boolean {
  const storage = type === StorageType.Local ? window.localStorage : window.sessionStorage;
  
  try {
    const testKey = `${APP_STORAGE_PREFIX}test`;
    storage.setItem(testKey, 'test');
    storage.removeItem(testKey);
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Stores a value in browser storage with optional expiration
 * 
 * @param key - The key to store the value under
 * @param value - The value to store
 * @param type - The type of storage to use (default: localStorage)
 * @param expirationMs - Optional expiration time in milliseconds
 * @returns True if storage was successful, false otherwise
 */
export function setItem<T>(
  key: string,
  value: T,
  type: StorageType = StorageType.Local,
  expirationMs?: number
): boolean {
  const prefixedKey = `${APP_STORAGE_PREFIX}${key}`;
  
  if (!isStorageAvailable(type)) {
    return false;
  }
  
  try {
    const storage = type === StorageType.Local ? window.localStorage : window.sessionStorage;
    
    let valueToStore: string;
    
    if (expirationMs) {
      // If expiration is provided, wrap the value with expiry timestamp
      const item: StorageItem<T> = {
        value: value,
        expiry: new Date().getTime() + expirationMs
      };
      valueToStore = JSON.stringify(item);
    } else {
      // Otherwise just store the value directly
      valueToStore = JSON.stringify(value);
    }
    
    storage.setItem(prefixedKey, valueToStore);
    return true;
  } catch (error) {
    // This could happen if quota is exceeded
    console.error('Storage error:', error);
    return false;
  }
}

/**
 * Retrieves a value from browser storage, handling expiration and deserialization
 * 
 * @param key - The key to retrieve the value for
 * @param defaultValue - Default value to return if item is not found or expired
 * @param type - The type of storage to use (default: localStorage)
 * @returns Retrieved value (type T) or defaultValue if not found or expired
 */
export function getItem<T>(
  key: string,
  defaultValue: T | null = null,
  type: StorageType = StorageType.Local
): T | null {
  const prefixedKey = `${APP_STORAGE_PREFIX}${key}`;
  
  if (!isStorageAvailable(type)) {
    return defaultValue;
  }
  
  try {
    const storage = type === StorageType.Local ? window.localStorage : window.sessionStorage;
    const item = storage.getItem(prefixedKey);
    
    // If the item doesn't exist, return the default value
    if (item === null) {
      return defaultValue;
    }
    
    // Try to parse the stored JSON
    let parsedItem: any;
    try {
      parsedItem = JSON.parse(item);
    } catch (error) {
      // If parsing fails, remove the corrupted item and return default
      console.error('Error parsing stored item:', error);
      storage.removeItem(prefixedKey);
      return defaultValue;
    }
    
    // Check if the item has an expiry property (is a StorageItem)
    if (parsedItem && typeof parsedItem === 'object' && 'expiry' in parsedItem) {
      // If the item has expired, remove it and return default
      if (new Date().getTime() > parsedItem.expiry) {
        storage.removeItem(prefixedKey);
        return defaultValue;
      }
      return parsedItem.value;
    }
    
    // If it's not a StorageItem, return the parsed value directly
    return parsedItem;
  } catch (error) {
    console.error('Error retrieving stored item:', error);
    return defaultValue;
  }
}

/**
 * Removes an item from browser storage
 * 
 * @param key - The key of the item to remove
 * @param type - The type of storage to use (default: localStorage)
 */
export function removeItem(
  key: string, 
  type: StorageType = StorageType.Local
): void {
  const prefixedKey = `${APP_STORAGE_PREFIX}${key}`;
  
  if (!isStorageAvailable(type)) {
    return;
  }
  
  try {
    const storage = type === StorageType.Local ? window.localStorage : window.sessionStorage;
    storage.removeItem(prefixedKey);
  } catch (error) {
    console.error('Error removing stored item:', error);
  }
}

/**
 * Clears all items from the specified storage or with a specific prefix
 * 
 * @param keyPrefix - Optional prefix to limit which keys to clear
 * @param type - The type of storage to use (default: localStorage)
 */
export function clearItems(
  keyPrefix?: string, 
  type: StorageType = StorageType.Local
): void {
  if (!isStorageAvailable(type)) {
    return;
  }
  
  try {
    const storage = type === StorageType.Local ? window.localStorage : window.sessionStorage;
    
    if (keyPrefix) {
      // Clear only items with the specified prefix
      const fullPrefix = `${APP_STORAGE_PREFIX}${keyPrefix}`;
      
      // We need to collect keys first because removing items changes the indices
      const keysToRemove: string[] = [];
      
      for (let i = 0; i < storage.length; i++) {
        const key = storage.key(i);
        if (key && key.startsWith(fullPrefix)) {
          keysToRemove.push(key);
        }
      }
      
      // Now remove the collected keys
      keysToRemove.forEach(key => storage.removeItem(key));
    } else {
      // Clear all items with APP_STORAGE_PREFIX
      const keysToRemove: string[] = [];
      
      for (let i = 0; i < storage.length; i++) {
        const key = storage.key(i);
        if (key && key.startsWith(APP_STORAGE_PREFIX)) {
          keysToRemove.push(key);
        }
      }
      
      keysToRemove.forEach(key => storage.removeItem(key));
    }
  } catch (error) {
    console.error('Error clearing stored items:', error);
  }
}

/**
 * Saves a form draft with automatic expiration
 * 
 * @param formId - Unique identifier for the form
 * @param formData - The form data to save
 * @returns True if storage was successful, false otherwise
 */
export function setFormDraft(formId: string, formData: any): boolean {
  const key = `form_draft_${formId}`;
  return setItem(key, formData, StorageType.Local, FORM_DRAFT_EXPIRY_MS);
}

/**
 * Retrieves a saved form draft
 * 
 * @param formId - Unique identifier for the form
 * @returns Retrieved form data or null if not found or expired
 */
export function getFormDraft(formId: string): any | null {
  const key = `form_draft_${formId}`;
  return getItem(key);
}

/**
 * Clears a saved form draft
 * 
 * @param formId - Unique identifier for the form
 */
export function clearFormDraft(formId: string): void {
  const key = `form_draft_${formId}`;
  removeItem(key);
}

/**
 * Saves an authentication token with expiration
 * 
 * @param token - The authentication token to save
 * @param expiresIn - Expiration time in milliseconds
 * @returns True if storage was successful, false otherwise
 */
export function setAuthToken(token: string, expiresIn: number): boolean {
  return setItem('auth_token', token, StorageType.Session, expiresIn);
}

/**
 * Retrieves the stored authentication token
 * 
 * @returns Retrieved token or null if not found or expired
 */
export function getAuthToken(): string | null {
  return getItem<string>('auth_token', null, StorageType.Session);
}

/**
 * Clears the stored authentication token
 */
export function clearAuthToken(): void {
  removeItem('auth_token', StorageType.Session);
}