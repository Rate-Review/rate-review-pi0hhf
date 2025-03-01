import React, { useState, useEffect, useCallback } from 'react'; // React library for building UI components //  ^18.0.0
import { useDispatch, useSelector } from 'react-redux'; // Redux hooks for state management //  ^8.0.0
import { useNavigate, useParams } from 'react-router-dom'; // React Router hooks for navigation and URL parameters //  ^6.4.0
import {
  Grid,
  Box,
  Paper,
  Typography,
  Button,
  Divider,
  useMediaQuery,
} from '@mui/material'; // Material UI components for layout and styling //  ^5.14.0
import { AddCircleOutline, FilterList } from '@mui/icons-material'; // Material UI icons for UI elements //  ^5.14.0

import MainLayout from '../../components/layout/MainLayout'; // Main application layout with header, sidebar, and content area
import PageHeader from '../../components/layout/PageHeader'; // Page header component with title and actions
import MessageThreadList from '../../components/messaging/MessageThreadList'; // Component for displaying message thread list
import MessageThread from '../../components/messaging/MessageThread'; // Component for displaying a single message thread
import MessageFilters from '../../components/messaging/MessageFilters'; // Component for message filtering controls
import EmptyState from '../../components/common/EmptyState'; // Empty state display when no messages are found
import Spinner from '../../components/common/Spinner'; // Loading indicator for async operations
import SearchBar from '../../components/common/SearchBar'; // Search input for filtering messages
import useQueryParams from '../../hooks/useQueryParams'; // Hook for managing URL query parameters
import {
  fetchThreads,
} from '../../store/messages/messagesThunks'; // Redux thunk to fetch message threads
import {
  fetchThreadById,
} from '../../store/messages/messagesThunks'; // Redux thunk to fetch a specific thread
import {
  selectThreads, selectThreadsLoading, selectThreadsError, selectCurrentThread
} from '../../store/messages/messagesSlice'; // Redux selectors for message thread state
import { messagesActions } from '../../store/messages/messagesSlice'; // Redux actions for message state management
import { MessageThread as MessageThreadType, MessageFilter } from '../../types/message'; // TypeScript interfaces for message data

/**
 * React functional component that renders the All Messages page
 */
const AllMessagesPage: React.FC = () => {
  // LD1: Initialize Redux dispatch function with useDispatch hook
  const dispatch = useDispatch();

  // LD1: Get URL parameters using useParams hook for potential threadId
  const { threadId: paramThreadId } = useParams<{ threadId?: string }>();

  // LD1: Set up navigation with useNavigate hook
  const navigate = useNavigate();

  // LD1: Initialize state for searchQuery, filters, pagination and selectedThreadId
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<MessageFilter>({});
  const [selectedThreadId, setSelectedThreadId] = useState<string | null>(paramThreadId || null);

  // LD1: Retrieve message threads from Redux store using useSelector
  const messageThreads = useSelector(selectThreads);
  const loading = useSelector(selectThreadsLoading);
  const error = useSelector(selectThreadsError);
  const currentThread = useSelector(selectCurrentThread);

  // LD1: Check if viewing on mobile with useMediaQuery hook
  const isMobile = useMediaQuery((theme: any) => theme.breakpoints.down('md'));

  // LD1: Set up initial filter values and URL query parameter handling
  const { params, mergeParams } = useQueryParams({
    threadId: null,
    searchText: null,
  });

  // LD1: Fetch message threads on component mount and when filters change
  useEffect(() => {
    dispatch(fetchThreads(params));
  }, [dispatch, params]);

  // LD1: Define handler functions for search, filter, and thread selection
  const handleSearchChange = (searchText: string) => {
    setSearchQuery(searchText);
    mergeParams({ searchText });
  };

  const handleFilterChange = (newFilters: MessageFilter) => {
    setFilters(newFilters);
    mergeParams(newFilters);
  };

  const handleThreadSelect = (threadId: string) => {
    setSelectedThreadId(threadId);
    dispatch(fetchThreadById(threadId));
    if (isMobile) {
      navigate(`/messages/${threadId}`);
    } else {
      mergeParams({ threadId });
    }
  };

  const handleCreateThread = () => {
    navigate('/messages/new');
  };

  const handlePageChange = (page: number) => {
    mergeParams({ page });
  };

  const handleCloseThread = () => {
    setSelectedThreadId(null);
    dispatch(messagesActions.clearCurrentThread());
    mergeParams({ threadId: null });
  };

  // LD1: Render MainLayout with appropriate PageHeader showing title and action buttons
  return (
    <MainLayout>
      <PageHeader
        title="Messages"
        actions={
          <Button variant="contained" startIcon={<AddCircleOutline />} onClick={handleCreateThread}>
            New Message
          </Button>
        }
      />

      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Paper style={{ padding: 16 }}>
            <SearchBar placeholder="Search messages" onSearch={handleSearchChange} />
            <MessageFilters filters={filters} onFilterChange={handleFilterChange} />
            <Divider style={{ margin: '16px 0' }} />
            {loading && <Spinner />}
            {error && <Typography color="error">{error}</Typography>}
            {!loading && !error && messageThreads.length === 0 && (
              <EmptyState title="No messages found" message="Try adjusting your search or filter options." />
            )}
            {!loading && messageThreads.length > 0 && (
              <MessageThreadList onThreadSelect={handleThreadSelect} />
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          {selectedThreadId ? (
            <Paper style={{ padding: 16 }}>
              <MessageThread threadId={selectedThreadId} />
            </Paper>
          ) : (
            <EmptyState title="Select a message to view" message="Choose a message from the list to see the details." />
          )}
        </Grid>
      </Grid>
    </MainLayout>
  );
};

// IE3: Be generous about your exports so long as it doesn't create a security risk.
export default AllMessagesPage;