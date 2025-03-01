/**
 * Configures and exports the React Query client for data fetching, caching, and state management
 * in the Justice Bid Rate Negotiation System frontend application.
 * 
 * This central configuration ensures consistent handling of API requests, error management,
 * and data caching across the entire application.
 * 
 * @version 4.29.0 - @tanstack/react-query version
 */

import { QueryClient, DefaultOptions } from '@tanstack/react-query';
import { handleApiError } from './errorHandling';

/**
 * Creates and configures a new QueryClient instance with custom settings 
 * optimized for the Justice Bid application
 */
export function createQueryClient(): QueryClient {
  // Define common default options for all queries
  const defaultOptions: DefaultOptions = {
    queries: {
      // Default stale time of 2 minutes for general data
      staleTime: 2 * 60 * 1000,
      // Cache for 30 minutes before garbage collection
      cacheTime: 30 * 60 * 1000,
      // Retry failed queries 3 times
      retry: 3,
      // Exponential backoff for retries
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      // Handle errors consistently
      onError: (err) => handleApiError(err),
      // Default to show error notifications for failed queries
      useErrorBoundary: false,
      // Default to keep previous data when refetching
      keepPreviousData: true,
      // Default to refetch on window focus
      refetchOnWindowFocus: true,
      // Default to not refetch on mount if data is already cached
      refetchOnMount: true,
    },
    mutations: {
      // Handle mutation errors consistently
      onError: (err) => handleApiError(err),
      // Default to not retry failed mutations
      retry: false,
    },
  };

  // Create query client with specialized query specific settings
  const queryClient = new QueryClient({
    defaultOptions,
    queryCache: {
      onError: (error, query) => {
        // Only report errors once for a specific query
        if (query.state.error === error) {
          handleApiError(error);
        }
      },
    },
  });

  // Configure specialized query types
  queryClient.setQueryDefaults(['rates'], {
    // Rate data changes frequently during negotiations
    staleTime: 1 * 60 * 1000, // 1 minute
  });

  queryClient.setQueryDefaults(['negotiations', 'active'], {
    // Active negotiations need frequent updates
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Poll every minute for updates
  });

  queryClient.setQueryDefaults(['analytics'], {
    // Analytics data can be cached longer
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2, // Less aggressive retry for heavy analytics queries
  });

  queryClient.setQueryDefaults(['messages'], {
    // Messages need frequent updates
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 30 * 1000, // Poll every 30 seconds for new messages
  });

  queryClient.setQueryDefaults(['ai'], {
    // AI recommendations have longer computation time
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 1, // Minimal retry for AI operations
  });

  queryClient.setMutationDefaults(['rates'], {
    // Optimistic updates for rate changes
    onMutate: async (variables) => {
      // Return context for potential rollback
      return { previousData: null };
    },
    onError: (err, variables, context) => {
      // Handle error and potentially roll back optimistic updates
      handleApiError(err);
    },
    onSuccess: (data, variables, context) => {
      // Invalidate relevant queries to refresh data
      queryClient.invalidateQueries(['rates']);
      queryClient.invalidateQueries(['negotiations']);
    },
  });

  return queryClient;
}

/**
 * Singleton QueryClient instance for use throughout the application
 */
const queryClient = createQueryClient();

export default queryClient;