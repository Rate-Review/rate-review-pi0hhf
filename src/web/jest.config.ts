import type { Config } from '@jest/types';

/**
 * Factory function that returns the Jest configuration object
 * @returns Jest configuration object
 */
const createJestConfig = (): Config.InitialOptions => {
  return {
    // Use jsdom environment for testing React components
    testEnvironment: 'jsdom',
    
    // Specify root directory for tests
    roots: ['<rootDir>/src'],
    
    // Setup files to run after environment is setup but before tests
    setupFilesAfterEnv: ['<rootDir>/src/tests/setupTests.ts'],
    
    // Mock static assets and CSS modules
    moduleNameMapper: {
      // Mock CSS imports
      '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
      // Mock image imports
      '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/src/tests/__mocks__/fileMock.ts',
      // Absolute path resolution
      '^src/(.*)$': '<rootDir>/src/$1',
    },
    
    // Patterns to detect test files
    testMatch: [
      '**/__tests__/**/*.+(ts|tsx)',
      '**/?(*.)+(spec|test).+(ts|tsx)',
    ],
    
    // Transform TypeScript files with ts-jest
    transform: {
      '^.+\\.(ts|tsx)$': 'ts-jest',
    },
    
    // Files to collect coverage from
    collectCoverageFrom: [
      'src/**/*.{ts,tsx}',
      '!src/**/*.d.ts',
      '!src/tests/**/*',
      '!src/index.tsx',
      '!**/node_modules/**',
    ],
    
    // Coverage thresholds
    coverageThreshold: {
      global: {
        branches: 80,
        functions: 85,
        lines: 85,
        statements: 85,
      },
      // UI Components specific thresholds
      './src/components/': {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80,
      },
      // Core Business Logic specific thresholds
      './src/utils/': {
        branches: 90,
        functions: 90,
        lines: 90,
        statements: 90,
      },
    },
    
    // Additional module directories
    moduleDirectories: ['node_modules', 'src'],
    
    // Additional configuration
    verbose: true,
    testTimeout: 10000,
    clearMocks: true,
    restoreMocks: true,
  };
};

// Export the configuration
export default createJestConfig();