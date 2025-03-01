import React, { useState, useRef, useEffect } from 'react'; //  ^18.2.0
import { useDispatch } from 'react-redux'; // ^8.0.5
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material'; //  ^5.14.0
import {
  Send as SendIcon,
  AttachFile as AttachFileIcon,
  EmojiEmotions as EmojiIcon,
  FormatBold as BoldIcon,
  FormatItalic as ItalicIcon,
  FormatListBulleted as BulletListIcon,
  FormatListNumbered as NumberedListIcon,
} from '@mui/icons-material'; //  ^5.14.0

import Button from '../common/Button';
import TextField from '../common/TextField';
import MessageAttachments from './MessageAttachments';
import useForm from '../../hooks/useForm';
import useAI from '../../hooks/useAI';
import {
  createMessage,
} from '../../store/messages/messagesThunks';
import {
  Attachment,
  AttachmentUpload,
  CreateMessageRequest,
  RelatedEntityType
} from '../../types/message';

/**
 * @interface MessageComposerProps
 * @description Props for the MessageComposer component
 */
interface MessageComposerProps {
  threadId?: string;
  parentId?: string;
  recipientIds?: string[];
  relatedEntityType?: RelatedEntityType;
  relatedEntityId?: string;
  onMessageSent?: () => void;
  initialContent?: string;
  placeholder?: string;
  className?: string;
  disableFormatting?: boolean;
  disableAttachments?: boolean;
  disableAI?: boolean;
  buttonText?: string;
}

/**
 * @interface MessageFormValues
 * @description Form values for the message composer
 */
interface MessageFormValues {
  content: string;
  attachments: AttachmentUpload[];
}

/**
 * @component MessageComposer
 * @description Component for composing and sending messages
 */
const MessageComposer: React.FC<MessageComposerProps> = ({
  threadId,
  parentId,
  recipientIds,
  relatedEntityType,
  relatedEntityId,
  onMessageSent,
  initialContent,
  placeholder = 'Type your message here...',
  className,
  disableFormatting = false,
  disableAttachments = false,
  disableAI = false,
  buttonText = 'Send',
}) => {
  // LD1: Initialize Redux dispatch
  const dispatch = useDispatch();

  // LD1: Initialize AI hook
  const { sendChatMessage } = useAI();

  // LD1: Initialize form state using custom hook
  const {
    values,
    handleChange,
    handleSubmit,
    setFieldValue,
  } = useForm<MessageFormValues>({
    initialValues: {
      content: initialContent || '',
      attachments: [],
    },
    onSubmit: async (values) => {
      // LD1: Create CreateMessageRequest object from form values
      const createMessageRequest: CreateMessageRequest = {
        content: values.content,
        threadId: threadId || null,
        parentId: parentId || null,
        recipientIds: recipientIds || [],
        attachments: values.attachments || null,
        relatedEntityType: relatedEntityType || null,
        relatedEntityId: relatedEntityId || null,
      };

      // LD1: Dispatch createMessage thunk action
      await dispatch(createMessage(createMessageRequest));

      // LD1: Reset form after successful submission
      setFieldValue('content', '');
      setFieldValue('attachments', []);

      // LD1: Call onMessageSent callback if provided
      if (onMessageSent) {
        onMessageSent();
      }
    },
  });

  // LD1: useRef for textarea element
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // LD1: Function to handle file selection for attachments
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    // Check if files are selected
    if (event.target.files && event.target.files.length > 0) {
      // Convert FileList to AttachmentUpload[] array
      const files = Array.from(event.target.files);
      const attachmentUploads: AttachmentUpload[] = files.map((file) => ({
        fileName: file.name,
        fileType: file.type,
        fileSize: file.size,
        file: file,
      }));

      // Update form state with the new attachments
      setFieldValue('attachments', attachmentUploads);
    }
  };

  // LD1: Function to remove an attachment from the current draft
  const handleRemoveAttachment = (attachmentId: string) => {
    // Filter out the attachment with the specified ID
    const updatedAttachments = values.attachments.filter(
      (attachment) => attachment.fileName !== attachmentId
    );

    // Update form state with the filtered attachments
    setFieldValue('attachments', updatedAttachments);
  };

  // LD1: Function to apply formatting to selected text (bold, italic, list)
  const handleApplyFormatting = (formatType: string) => {
    // Get the current selection in the textarea
    const textarea = textareaRef.current;
    if (!textarea) return;

    const selectionStart = textarea.selectionStart;
    const selectionEnd = textarea.selectionEnd;
    const selectedText = textarea.value.substring(selectionStart, selectionEnd);

    let formattedText = selectedText;

    // Apply appropriate markdown formatting based on formatType
    switch (formatType) {
      case 'bold':
        formattedText = `**${selectedText}**`;
        break;
      case 'italic':
        formattedText = `*${selectedText}*`;
        break;
      case 'bulletList':
        formattedText = selectedText
          .split('\n')
          .map((line) => `- ${line}`)
          .join('\n');
        break;
      case 'numberedList':
        formattedText = selectedText
          .split('\n')
          .map((line, index) => `${index + 1}. ${line}`)
          .join('\n');
        break;
      default:
        break;
    }

    // Update the message content in form state
    const updatedContent =
      textarea.value.substring(0, selectionStart) +
      formattedText +
      textarea.value.substring(selectionEnd);
    setFieldValue('content', updatedContent);

    // Re-focus the textarea
    textarea.focus();
  };

  // LD1: Function to apply an AI suggestion to the message content
  const handleSuggestionSelect = (suggestion: string) => {
    // Set the suggested text as the message content
    setFieldValue('content', suggestion);

    // Focus the textarea
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  return (
    <Paper className={className} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Compose Message
      </Typography>
      <form onSubmit={handleSubmit}>
        <TextField
          id="message-content"
          name="content"
          label="Message"
          placeholder={placeholder}
          multiline
          rows={4}
          fullWidth
          value={values.content}
          onChange={handleChange}
          inputRef={textareaRef}
        />
        {!disableFormatting && (
          <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
            <Tooltip title="Bold">
              <IconButton onClick={() => handleApplyFormatting('bold')} aria-label="bold">
                <BoldIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Italic">
              <IconButton onClick={() => handleApplyFormatting('italic')} aria-label="italic">
                <ItalicIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Bulleted List">
              <IconButton onClick={() => handleApplyFormatting('bulletList')} aria-label="bullet list">
                <BulletListIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Numbered List">
              <IconButton onClick={() => handleApplyFormatting('numberedList')} aria-label="numbered list">
                <NumberedListIcon />
              </IconButton>
            </Tooltip>
          </Box>
        )}
        {!disableAttachments && (
          <>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <IconButton component="label" aria-label="add attachments">
                <AttachFileIcon />
                <input
                  type="file"
                  hidden
                  multiple
                  onChange={handleFileUpload}
                />
              </IconButton>
              <Typography variant="body2" color="text.secondary">
                Add Attachments
              </Typography>
            </Box>
            <MessageAttachments
              attachments={values.attachments as Attachment[]}
              editable
              onRemove={handleRemoveAttachment}
            />
          </>
        )}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
          <Button type="submit">{buttonText}</Button>
          {!disableAI && (
            <Box>
              {/* AI Suggestions Placeholder */}
              <Typography variant="caption" color="text.secondary">
                AI Suggestions: (Coming Soon)
              </Typography>
            </Box>
          )}
        </Box>
      </form>
    </Paper>
  );
};

export default MessageComposer;