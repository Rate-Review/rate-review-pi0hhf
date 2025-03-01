// jest-dom adds custom jest matchers for working with the DOM.
// @ts-ignore - Ignoring because this package doesn't have types
import '@testing-library/jest-dom'; // version ^5.16.5
import { setupServer } from 'msw/node'; // version ^1.2.1
import { afterAll, afterEach, beforeAll } from 'jest';
import handlers from '../mocks/handlers';
import 'jest-localstorage-mock'; // version ^2.4.26

// Mock the window.scrollTo function as it's not available in the test environment
// This prevents errors when components try to scroll
window.scrollTo = jest.fn();

/**
 * setupMockServer: Configures the Mock Service Worker server for API mocking.
 * @returns {server} Configured MSW server instance
 */
function setupMockServer() {
  // LD1: Creates and configures the Mock Service Worker server for API mocking
  // Step 1: Import the setupServer function from msw/node
  // Already imported above

  // Step 2: Create a new server instance with the imported handlers
  const server = setupServer(...handlers);

  // Step 3: Return the configured server instance
  return server;
}

// LD1: Extends Jest with additional DOM element matchers like toBeInTheDocument, toHaveClass, toBeVisible
// Setting up configuration: jest_dom_extensions
// This is handled by the import '@testing-library/jest-dom' statement at the top of the file

// LD1: Configures MSW to intercept network requests and return mock responses
// Setting up configuration: mock_service_worker
const server = setupMockServer();

// LD1: Provides mock implementation of localStorage and sessionStorage APIs
// Setting up configuration: local_storage_mock
// This is handled by the import 'jest-localstorage-mock' statement at the top of the file

// LD1: Sets up any global mocks needed across all tests
// Setting up configuration: global_mocks
// Global Jest hook to initialize mock server before all tests run
beforeAll(() => {
  // IE1: Check that the imported items are used correctly based on the source files provided
  server.listen();
});

// Global Jest hook to reset mocks and handlers after each test
afterEach(() => {
  // LD2: Resetting handlers after each test
  server.resetHandlers();
  // Clear all mock implementations to prevent state from being shared
  jest.clearAllMocks();
});

// Global Jest hook to stop mock server after all tests complete
afterAll(() => {
  // LD2: Closing the server after all tests are done
  server.close();
});

// LD1: Configures jest-environment-jsdom for browser-like test environment
// Setting up configuration: test_environment
// This is configured in jest.config.js, not directly in this file