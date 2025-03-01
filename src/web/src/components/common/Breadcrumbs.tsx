import React from 'react';
import { styled } from '@mui/material/styles';
import { Breadcrumbs as MUIBreadcrumbs, Typography, Link } from '@mui/material';
import { NavigateNext } from '@mui/icons-material';
import { useLocation, Link as RouterLink } from 'react-router-dom';
import colors from '../../../theme/colors';

/**
 * Interface representing a route configuration
 */
export interface Route {
  path: string;
  label: string;
  children?: Route[];
}

/**
 * Interface representing a breadcrumb item
 */
export interface BreadcrumbItem {
  path: string;
  label: string;
  isActive?: boolean;
}

/**
 * Props for the Breadcrumbs component
 */
export interface BreadcrumbsProps {
  /**
   * Array of route configurations used to generate breadcrumbs
   */
  routes: Route[];
  /**
   * Optional custom breadcrumbs to override automatic generation
   */
  custom?: BreadcrumbItem[];
  /**
   * Optional CSS class name
   */
  className?: string;
}

/**
 * Generates breadcrumb items based on the current location path and route configuration
 * @param pathname Current location pathname
 * @param routes Array of route configurations
 * @returns Array of breadcrumb items with path, label, and isActive properties
 */
const generateBreadcrumbs = (pathname: string, routes: Route[]): BreadcrumbItem[] => {
  // Remove query parameters if present
  const path = pathname.split('?')[0];
  const segments = path.split('/').filter(segment => segment !== '');
  const breadcrumbs: BreadcrumbItem[] = [];
  let currentPath = '';

  // Add dashboard as the first breadcrumb
  const dashboardRoute = routes.find(route => 
    route.path === '/' || 
    route.path === '/dashboard' || 
    route.path === 'dashboard'
  );
  
  if (dashboardRoute) {
    breadcrumbs.push({
      path: dashboardRoute.path,
      label: dashboardRoute.label,
      isActive: segments.length === 0
    });
  }

  // Generate breadcrumbs for each path segment
  segments.forEach((segment, index) => {
    currentPath += `/${segment}`;
    
    // Try to find a matching route for this path segment
    const matchingRoute = findMatchingRoute(currentPath, routes);
    
    if (matchingRoute) {
      breadcrumbs.push({
        path: currentPath,
        label: matchingRoute.label,
        isActive: index === segments.length - 1
      });
    } else {
      // If no match found in routes, use the segment itself (capitalized)
      breadcrumbs.push({
        path: currentPath,
        label: segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' '),
        isActive: index === segments.length - 1
      });
    }
  });

  return breadcrumbs;
};

/**
 * Finds a matching route configuration for a given path
 * @param path The current path to match
 * @param routes Array of route configurations
 * @returns Matching route or undefined if no match found
 */
const findMatchingRoute = (path: string, routes: Route[]): Route | undefined => {
  // Direct match
  const directMatch = routes.find(route => route.path === path);
  if (directMatch) return directMatch;

  // Check for dynamic route matches (e.g., /rates/:id)
  for (const route of routes) {
    // Skip non-dynamic routes
    if (!route.path.includes(':')) continue;

    // Create a regex pattern that replaces route params with capture groups
    const pattern = route.path
      .split('/')
      .map(segment => {
        if (segment.startsWith(':')) {
          return '([^/]+)'; // Capture anything except /
        }
        return segment;
      })
      .join('/');
      
    const routePathRegex = new RegExp(`^${pattern}$`);
    
    if (routePathRegex.test(path)) return route;
    
    // Check children routes if present
    if (route.children) {
      const childMatch = findMatchingRoute(path, route.children);
      if (childMatch) return childMatch;
    }
  }

  return undefined;
};

// Styled component for the MUI Breadcrumbs
const StyledBreadcrumbs = styled(MUIBreadcrumbs)(({ theme }) => ({
  padding: theme.spacing(1, 0),
  '& .MuiBreadcrumbs-ol': {
    flexWrap: 'wrap',
  },
  '& .MuiBreadcrumbs-separator': {
    color: colors.neutral.light,
  },
  // Responsive styles
  [theme.breakpoints.down('sm')]: {
    padding: theme.spacing(0.5, 0),
    '& .MuiBreadcrumbs-separator': {
      margin: theme.spacing(0, 0.5),
    },
  }
}));

/**
 * Breadcrumbs component for showing the current location within the application hierarchy
 * and providing navigation links to previous levels.
 */
const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ routes, custom, className }) => {
  const location = useLocation();
  const breadcrumbs = custom || generateBreadcrumbs(location.pathname, routes);

  // If there's only one breadcrumb or none, don't render the component
  if (breadcrumbs.length <= 1) {
    return null;
  }

  return (
    <StyledBreadcrumbs 
      separator={<NavigateNext fontSize="small" />}
      aria-label="breadcrumb navigation"
      className={className}
    >
      {breadcrumbs.map((breadcrumb, index) => {
        const isLast = index === breadcrumbs.length - 1;

        return isLast ? (
          <Typography 
            key={breadcrumb.path} 
            color="textPrimary"
            aria-current="page"
            variant="body2"
            sx={{ color: colors.primary.main, fontWeight: 500 }}
          >
            {breadcrumb.label}
          </Typography>
        ) : (
          <Link
            key={breadcrumb.path}
            component={RouterLink}
            to={breadcrumb.path}
            color="textSecondary"
            underline="hover"
            sx={{ 
              color: colors.neutral.main,
              '&:hover': {
                color: colors.primary.main
              }
            }}
            variant="body2"
          >
            {breadcrumb.label}
          </Link>
        );
      })}
    </StyledBreadcrumbs>
  );
};

export default Breadcrumbs;