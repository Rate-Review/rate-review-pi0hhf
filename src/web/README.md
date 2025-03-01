# Justice Bid Rate Negotiation System - Web Frontend

## Overview

The Justice Bid Rate Negotiation System web frontend is a comprehensive React-based application designed to systematize the legal rate negotiation process between law firms and their clients. This application provides a structured, analytics-driven approach to rate proposals, negotiations, and approvals, replacing inefficient email-based processes currently used in the industry.

The frontend serves both law firms seeking to propose new rates to their clients and corporate legal departments evaluating, negotiating, and approving these rates. The application incorporates AI-driven analytics, third-party performance data, and automated workflows to deliver actionable recommendations while maintaining a complete audit trail of all negotiations.

## Technology Stack

- **Core Framework**: React.js 18.0+
- **Language**: TypeScript 5.0+
- **State Management**: Redux 4.2+ with Redux Toolkit
- **UI Components**: Material UI 5.14+
- **Data Visualization**: Chart.js 4.0+
- **Routing**: React Router 6.4+
- **Form Handling**: Formik 2.4+
- **HTTP Client**: Axios 1.4+
- **Build Tool**: Vite
- **Testing**: Jest, React Testing Library
- **Code Quality**: ESLint, Prettier

## Prerequisites

- Node.js 16.x or higher
- npm 8.x or yarn 1.22.x or higher
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/justicebid/rate-negotiation-system.git
cd rate-negotiation-system/src/web
```

2. Install dependencies:
```bash
npm install
# or with yarn
yarn install
```

3. Set up environment variables:
   - Copy the `.env.example` file to `.env.local`
   - Update the values according to your development environment

```bash
cp .env.example .env.local
```

4. Start the development server:
```bash
npm run dev
# or with yarn
yarn dev
```

## Project Structure

```
src/
├── assets/              # Static assets (images, fonts, etc.)
├── components/          # Reusable UI components
│   ├── common/          # Shared UI components
│   ├── layout/          # Layout components
│   ├── forms/           # Form components
│   ├── tables/          # Table components
│   ├── charts/          # Data visualization components
│   ├── modals/          # Modal dialog components
│   └── ai/              # AI-specific components
├── containers/          # Container components with business logic
├── context/             # React context definitions
├── hooks/               # Custom React hooks
├── pages/               # Page components
├── services/            # API service integrations
├── store/               # Redux store configuration
│   ├── auth/            # Authentication state
│   ├── rates/           # Rate data and negotiations
│   ├── analytics/       # Analytics state
│   ├── messages/        # Messaging state
│   ├── organizations/   # Organization data
│   └── index.ts         # Store configuration
├── types/               # TypeScript type definitions
├── utils/               # Utility functions
├── App.tsx              # Main application component
├── main.tsx             # Entry point
└── vite-env.d.ts        # Vite type definitions
```

### Key Directories

- **components/**: Reusable UI components organized by function
- **containers/**: Components that connect to Redux state
- **pages/**: Top-level page components corresponding to routes
- **services/**: API integration services
- **store/**: Redux store with domain-specific slices
- **hooks/**: Custom React hooks for shared logic

## Available Scripts

- **`npm run dev`**: Start the development server
- **`npm run build`**: Build the application for production
- **`npm run preview`**: Preview the production build locally
- **`npm run test`**: Run tests with Jest
- **`npm run test:watch`**: Run tests in watch mode
- **`npm run test:coverage`**: Run tests with coverage report
- **`npm run lint`**: Run ESLint to check for code issues
- **`npm run lint:fix`**: Fix linting issues automatically
- **`npm run format`**: Format code with Prettier
- **`npm run type-check`**: Run TypeScript type checking

## Development Guidelines

### Component Creation

1. **Component Types**:
   - **Presentational Components**: Focus on UI, receive data via props
   - **Container Components**: Connect to Redux, handle business logic
   - **Page Components**: Top-level components rendered by routes

2. **Component Structure**:
   - Create components in their respective directories
   - Use index.ts files to export components
   - Each component should have its own directory with the following structure:

```
ComponentName/
├── ComponentName.tsx     # Component implementation
├── ComponentName.test.tsx # Component tests
├── ComponentName.styles.ts # Component styles (if applicable)
└── index.ts              # Export file
```

3. **Props Typing**:
   - Define explicit interfaces for component props
   - Use descriptive names for prop interfaces (e.g., `RateTableProps`)
   - Document props with JSDoc comments

```tsx
interface ButtonProps {
  /** The label text for the button */
  label: string;
  /** Function called when button is clicked */
  onClick: () => void;
  /** Optional variant for styling */
  variant?: 'primary' | 'secondary' | 'outline';
  /** Whether the button is disabled */
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({ 
  label, 
  onClick, 
  variant = 'primary', 
  disabled = false 
}) => {
  // Component implementation
};
```

### State Management

1. **Redux Usage**:
   - Use Redux for global application state
   - Organize store by domain (auth, rates, analytics, etc.)
   - Use Redux Toolkit for simplified Redux development
   - Implement slice pattern for state management

2. **Local State**:
   - Use React's useState for component-specific state
   - Use useReducer for complex component state logic

3. **Context API**:
   - Use Context for themes, UI preferences, and feature flags
   - Avoid using Context for high-frequency updates

### API Integration

1. **Service Pattern**:
   - Create service modules for API integration
   - Use Axios for HTTP requests
   - Implement request/response interceptors for common handling

```tsx
// services/rateService.ts
import axios from 'axios';
import { Rate, RateSubmission } from '../types';

const API_URL = import.meta.env.VITE_API_URL;

export const rateService = {
  getRates: async (): Promise<Rate[]> => {
    const response = await axios.get(`${API_URL}/rates`);
    return response.data;
  },
  
  submitRates: async (submission: RateSubmission): Promise<void> => {
    await axios.post(`${API_URL}/rates`, submission);
  },
  
  // Other rate-related API calls
};
```

2. **Error Handling**:
   - Implement centralized error handling
   - Use try/catch blocks for async operations
   - Provide user-friendly error messages

### Style Guidelines

1. **Material UI Usage**:
   - Use Material UI components as the primary UI library
   - Customize the theme to match Justice Bid branding
   - Implement responsive design for all components

2. **CSS-in-JS**:
   - Use Material UI's styling solution for component styling
   - Create separate style files for complex components
   - Use theme variables for consistent styling

```tsx
// ComponentName.styles.ts
import { styled } from '@mui/material/styles';
import { Box, Paper } from '@mui/material';

export const StyledContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[2],
  [theme.breakpoints.down('md')]: {
    padding: theme.spacing(2),
  },
}));

export const HeaderSection = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
}));
```

### TypeScript Best Practices

1. **Type Definitions**:
   - Create clear interfaces for data models
   - Use type guards for runtime type checking
   - Avoid using `any` type - use `unknown` if type is uncertain

2. **Generics**:
   - Use generics for reusable components and functions
   - Apply constraints to generic type parameters when applicable

3. **Type Organization**:
   - Define core data models in `types/` directory
   - Co-locate component-specific types with their components
   - Use barrel exports (index.ts files) for type exports

## Testing

### Testing Strategy

1. **Unit Tests**:
   - Test individual components and functions
   - Focus on business logic and user interactions
   - Use Jest and React Testing Library

2. **Component Tests**:
   - Test component rendering and user interactions
   - Test common use cases and edge cases
   - Verify accessibility compliance

3. **Integration Tests**:
   - Test interactions between components
   - Verify Redux store integration
   - Test API service integration with mock servers

### Test Organization

- Place test files adjacent to implementation files
- Follow naming convention: `ComponentName.test.tsx`
- Group tests logically with `describe` blocks
- Use clear test descriptions with `it` or `test`

### Testing Examples

```tsx
// Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import Button from './Button';

describe('Button component', () => {
  it('renders with the provided label', () => {
    render(<Button label="Click me" onClick={() => {}} />);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button label="Click me" onClick={handleClick} />);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies disabled state correctly', () => {
    render(<Button label="Click me" onClick={() => {}} disabled />);
    expect(screen.getByText('Click me')).toBeDisabled();
  });
});
```

### Mock Strategies

1. **API Mocking**:
   - Use Mock Service Worker (MSW) for API mocking
   - Create mock handlers for each API endpoint
   - Define mock response data that matches API contracts

2. **Redux Mocking**:
   - Use a test store with preloaded state
   - Mock specific actions and reducers as needed
   - Test connected components with mock store providers

## Building and Deployment

### Build Process

The application uses Vite for build optimization, which includes:

1. Code splitting for improved load times
2. Asset optimization and minification
3. Environment-specific builds

To build the application for production:

```bash
npm run build
# or with yarn
yarn build
```

The build output will be in the `dist/` directory.

### Deployment

The application is deployed using GitHub Actions with the following workflow:

1. Code is pushed to a feature branch
2. Pull request is created to merge into main
3. CI runs tests and linting
4. After approval and merge, the deployment workflow:
   - Builds the application
   - Runs final tests
   - Deploys to the appropriate environment based on branch

#### Environment Variables

The following environment variables are required for deployment:

- `VITE_API_URL`: Base URL for the backend API
- `VITE_AUTH_DOMAIN`: Authentication domain
- `VITE_AUTH_CLIENT_ID`: Authentication client ID
- `VITE_AI_API_URL`: AI service API URL

## Contribution Guidelines

### Branching Strategy

- `main`: Production-ready code
- `dev`: Integration branch for development
- Feature branches: Created from `dev` for new features
- Hotfix branches: Created from `main` for critical fixes

### Pull Request Process

1. Create a feature branch from `dev` or a hotfix branch from `main`
2. Implement changes with appropriate tests
3. Ensure all tests pass and code meets quality standards
4. Open a pull request with a clear description of changes
5. Request review from at least one team member
6. Address review comments
7. Merge when approved and CI passes

### Code Review Standards

- Focus on code quality, performance, and security
- Verify test coverage for new features
- Check for TypeScript type safety
- Ensure adherence to project coding standards
- Verify accessibility compliance
- Review for responsive design considerations

### Documentation

- Update README.md when adding significant features
- Add JSDoc comments to functions and components
- Document props interfaces with clear descriptions
- Create or update examples for new components

## License

Copyright © 2023 Justice Bid, Inc. All rights reserved.