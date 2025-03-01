import React, { useCallback, useMemo } from 'react'; // React library for building UI components ^18.0+
import { useDispatch, useSelector } from 'react-redux'; // For accessing and updating Redux state ^8.0+
import {
  Box,
  Typography,
  Chip,
  IconButton,
} from '@mui/material'; // Material UI components for layout and display ^5.14+
import {
  VisibilityOutlined,
  MarkEmailReadOutlined,
  DeleteOutline,
  Reply,
  ChatOutlined,
} from '@mui/icons-material'; // Material UI icons for action buttons ^5.14+
import { useNavigate } from 'react-router-dom'; // For navigation to message detail or thread pages ^6.4+

import DataTable, { ColumnDef } from './DataTable'; // Base table component for displaying data with sorting, filtering, and pagination
import Tooltip from '../common/Tooltip'; // For displaying additional information on hover
import Badge from '../common/Badge'; // For highlighting unread messages
import Button from '../common/Button'; // For action buttons in the table
import Avatar from '../common/Avatar'; // For displaying user avatars
import {
  Message,
  MessageThread,
  RelatedEntityType,
} from '../../types/message'; // Type definitions for message data
import {
  fetchMessages,
  markMessageAsRead,
  deleteMessage,
} from '../../store/messages/messagesThunks'; // Redux thunks for message operations
import { messagesActions } from '../../store/messages/messagesSlice'; // Redux actions for updating message state
import { formatDate } from '../../utils/date'; // For formatting date values
import { usePermissions } from '../../hooks/usePermissions'; // For checking user permissions
import { useAuth } from '../../hooks/useAuth'; // For accessing current user information

/**
 * Type definition for MessageTable component props
 */
export interface MessageTableProps {
  messages: Message[];
  isLoading: boolean;
  onRowClick?: (row: Message) => void;
  filters: any; // TODO: Replace 'any' with a specific type for message filters
  onFilterChange: (filters: any) => void; // TODO: Replace 'any' with a specific type for filter change handler
  pagination: any; // TODO: Replace 'any' with a specific type for pagination
  onPaginationChange: (pagination: any) => void; // TODO: Replace 'any' with a specific type for pagination change handler
  selectable?: boolean;
  onSelectionChange?: (selectedRows: Message[]) => void;
}

/**
 * Helper function to get a human-readable label for a related entity type
 * @param entityType - The related entity type
 * @returns Human-readable entity label
 */
const getRelatedEntityLabel = (entityType: RelatedEntityType): string => {
  switch (entityType) {
    case RelatedEntityType.Negotiation:
      return 'Negotiation';
    case RelatedEntityType.Rate:
      return 'Rate';
    case RelatedEntityType.OCG:
      return 'OCG';
    default:
      return 'Unknown';
  }
};

/**
 * Component for displaying message data in a table format
 * @param props - Props for the component
 * @returns Rendered table component
 */
const MessageTable: React.FC<MessageTableProps> = ({
  messages,
  isLoading,
  onRowClick,
  filters,
  onFilterChange,
  pagination,
  onPaginationChange,
  selectable,
  onSelectionChange,
}) => {
  // IE1: Initialize useNavigate hook for navigation
  const navigate = useNavigate();

  // IE1: Initialize useDispatch for dispatching Redux actions
  const dispatch = useDispatch();

  // IE1: Initialize useSelector to access messages state from Redux
  const currentUserId = useSelector((state: any) => state.auth.user?.id);

  // IE1: Initialize useAuth to get current user information
  const { currentUser } = useAuth();

  // IE1: Initialize usePermissions to check user permissions
  const { can } = usePermissions();

  /**
   * Handles marking a message as read
   * @param messageId - ID of the message to mark as read
   */
  const handleMarkAsRead = useCallback(
    (messageId: string) => {
      dispatch(markMessageAsRead(messageId));
      dispatch(messagesActions.updateMessageReadStatus({ messageId, isRead: true }));
    },
    [dispatch]
  );

  /**
   * Handles deleting a message
   * @param messageId - ID of the message to delete
   */
  const handleDelete = useCallback(
    (messageId: string) => {
      if (window.confirm('Are you sure you want to delete this message?')) {
        dispatch(deleteMessage(messageId));
      }
    },
    [dispatch]
  );

  /**
   * Handles replying to a message
   * @param messageId - ID of the message to reply to
   */
  const handleReply = useCallback(
    (messageId: string) => {
      // TODO: Implement reply functionality
      console.log(`Reply to message ${messageId}`);
    },
    []
  );

  /**
   * Handles viewing a message thread
   * @param threadId - ID of the message thread to view
   */
  const handleViewThread = useCallback(
    (threadId: string) => {
      navigate(`/messages/thread/${threadId}`);
    },
    [navigate]
  );

  // LD1: Define table columns with appropriate cell renderers for message data
  const columns: ColumnDef<Message>[] = useMemo(
    () => [
      {
        id: 'sender',
        label: 'Sender',
        accessor: 'sender.name',
        renderCell: (row) => (
          <Box display="flex" alignItems="center">
            <Avatar name={row.sender.name} imageUrl={row.sender.avatarUrl} size="sm" />
            <Box ml={1}>
              <Typography variant="body2">
                {row.sender.name}
                {row.senderId === currentUserId && <Typography variant="caption">(You)</Typography>}
              </Typography>
            </Box>
          </Box>
        ),
        sortable: true,
        filterable: true,
      },
      {
        id: 'content',
        label: 'Message',
        accessor: 'content',
        renderCell: (row) => (
          <Box>
            <Typography variant="body2" noWrap>
              {row.content}
            </Typography>
            {!row.isRead && <Badge variant="secondary" content="Unread" />}
          </Box>
        ),
        sortable: false,
        filterable: true,
      },
      {
        id: 'relatedEntity',
        label: 'Related To',
        accessor: 'relatedEntityType',
        renderCell: (row) => (
          <Chip
            label={`${getRelatedEntityLabel(row.relatedEntityType)} ${row.relatedEntityId}`}
            size="small"
          />
        ),
        sortable: true,
        filterable: true,
      },
      {
        id: 'recipients',
        label: 'Recipients',
        accessor: 'recipientIds',
        renderCell: (row) => (
          <Tooltip content={row.recipientIds.length.toString()}>
            <Typography variant="body2">{row.recipientIds.length} recipients</Typography>
          </Tooltip>
        ),
        sortable: false,
        filterable: false,
      },
      {
        id: 'hasAttachments',
        label: 'Attachments',
        accessor: 'attachments',
        renderCell: (row) => (
          <Typography variant="body2">{row.attachments.length > 0 ? 'Yes' : 'No'}</Typography>
        ),
        sortable: true,
        filterable: false,
      },
      {
        id: 'createdAt',
        label: 'Date',
        accessor: 'createdAt',
        renderCell: (row) => <Typography variant="body2">{formatDate(row.createdAt)}</Typography>,
        sortable: true,
        filterable: false,
      },
      {
        id: 'actions',
        label: 'Actions',
        accessor: null,
        renderCell: (row) => (
          <Box>
            {can('read', 'messages', 'organization') && (
              <IconButton aria-label="view" onClick={() => onRowClick(row)}>
                <VisibilityOutlined />
              </IconButton>
            )}
            {can('read', 'messages', 'organization') && (
              <IconButton aria-label="view thread" onClick={() => handleViewThread(row.threadId)}>
                <ChatOutlined />
              </IconButton>
            )}
            {can('update', 'messages', 'organization') && !row.isRead && (
              <IconButton aria-label="mark as read" onClick={() => handleMarkAsRead(row.id)}>
                <MarkEmailReadOutlined />
              </IconButton>
            )}
            {can('create', 'messages', 'organization') && (
              <IconButton aria-label="reply" onClick={() => handleReply(row.id)}>
                <Reply />
              </IconButton>
            )}
            {can('delete', 'messages', 'organization') && (
              <IconButton aria-label="delete" onClick={() => handleDelete(row.id)}>
                <DeleteOutline />
              </IconButton>
            )}
          </Box>
        ),
        sortable: false,
        filterable: false,
      },
    ],
    [can, currentUserId, handleMarkAsRead, handleDelete, handleReply, handleViewThread, navigate, onRowClick]
  );

  // LD1: Define custom row rendering to highlight unread messages
  const getRowClassName = (row: Message) => {
    return !row.isRead ? 'unread-message' : '';
  };

  // LD1: Handle filtering and search functionality
  const handleFilterChange = (newFilters: any) => {
    dispatch(messagesActions.setFilters(newFilters));
    onFilterChange(newFilters);
  };

  // LD1: Use DataTable component with defined columns and message data
  return (
    <DataTable
      title="Messages"
      data={messages}
      columns={columns}
      isLoading={isLoading}
      onRowClick={onRowClick}
      getRowClassName={getRowClassName}
      filters={filters}
      onFilterChange={handleFilterChange}
      pagination={pagination}
      onPaginationChange={onPaginationChange}
      selectable={selectable}
      onSelectionChange={onSelectionChange}
    />
  );
};

export default MessageTable;