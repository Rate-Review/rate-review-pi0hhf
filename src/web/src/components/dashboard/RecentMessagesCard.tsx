import React, { useState, useEffect } from 'react';
import { Box, Typography, Divider, Link, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';

import Card, { CardHeader, CardContent } from '../common/Card';
import EmptyState from '../common/EmptyState';
import { Message, MessageFilter } from '../../types/message';
import messagesService from '../../services/messages';
import { formatDisplayDate } from '../../utils/date';
import { ROUTES } from '../../constants/routes';

/**
 * Renders a card displaying recent messages with sender info, subject, and message snippet
 */
const RecentMessagesCard: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchRecentMessages = async () => {
      try {
        setLoading(true);
        // Fetch most recent messages (limit to 5 for dashboard display)
        const response = await messagesService.getMessages(undefined, { page: 1, pageSize: 5 });
        if (response && response.items) {
          // Sort messages by creation date (newest first)
          const sortedMessages = [...response.items].sort(
            (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
          );
          setMessages(sortedMessages);
        }
        setError(null);
      } catch (err) {
        setError('Failed to load recent messages');
        console.error('Error fetching messages:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRecentMessages();
  }, []);

  const handleViewAllClick = () => {
    navigate(ROUTES.ALL_MESSAGES);
  };

  return (
    <Card>
      <CardHeader title="RECENT MESSAGES" />
      <CardContent>
        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" p={3}>
            <CircularProgress size={40} />
          </Box>
        ) : error ? (
          <Typography color="error" align="center" p={2}>
            {error}
          </Typography>
        ) : messages.length === 0 ? (
          <EmptyState
            title="No Recent Messages"
            message="Your recent messages will appear here."
            icon={<Box sx={{ fontSize: '3rem' }}>📨</Box>}
          />
        ) : (
          <Box>
            {messages.map((message, index) => (
              <React.Fragment key={message.id}>
                {index > 0 && <Divider sx={{ my: 2 }} />}
                <Box>
                  <Typography variant="subtitle2" component="div" fontWeight="medium">
                    From: {message.sender.name} ({message.sender.organization.name})
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Re: {
                      message.relatedEntityType
                        ? `${message.relatedEntityType} ${message.relatedEntityId?.substring(0, 8)}...`
                        : 'General Message'
                    }
                  </Typography>
                  <Typography variant="body2" color="text.primary" sx={{ mb: 1 }}>
                    {/* Truncate message content to show only a preview snippet */}
                    {message.content.length > 100
                      ? `${message.content.substring(0, 100)}...`
                      : message.content}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatDisplayDate(message.createdAt)}
                  </Typography>
                </Box>
              </React.Fragment>
            ))}
            
            <Box mt={2} display="flex" justifyContent="flex-end">
              <Link 
                component="button"
                variant="body2"
                onClick={handleViewAllClick}
                sx={{ textDecoration: 'none' }}
              >
                View All
              </Link>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default RecentMessagesCard;