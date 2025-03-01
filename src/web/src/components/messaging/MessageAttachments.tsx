import React from 'react';
import {
  Box,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  AttachFile as AttachFileIcon,
  Description as DocumentIcon,
  Image as ImageIcon,
  PictureAsPdf as PdfIcon,
  InsertDriveFile as GenericFileIcon,
  GetApp as DownloadIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';

import { formatFileSize } from '../../utils/file';
import { Attachment } from '../../types/message';

/**
 * Props for the MessageAttachments component
 */
interface MessageAttachmentsProps {
  attachments: Attachment[];
  editable?: boolean;
  onRemove?: (attachmentId: string) => void;
  onDownload?: (attachment: Attachment) => void;
  className?: string;
}

/**
 * Determines the appropriate icon based on file type
 *
 * @param fileType - The MIME type of the file
 * @returns The appropriate icon component
 */
const getFileIcon = (fileType: string): JSX.Element => {
  if (fileType.startsWith('image/')) {
    return <ImageIcon color="primary" />;
  } else if (fileType === 'application/pdf') {
    return <PdfIcon color="error" />;
  } else if (
    fileType.includes('document') ||
    fileType.includes('sheet') ||
    fileType.includes('presentation')
  ) {
    return <DocumentIcon color="primary" />;
  }
  
  return <GenericFileIcon color="action" />;
};

/**
 * Component that displays and manages file attachments for messages in the Justice Bid
 * Rate Negotiation System. Shows attachment lists with appropriate file type icons,
 * allows downloading attachments, and supports removing attachments in editable mode.
 */
const MessageAttachments: React.FC<MessageAttachmentsProps> = ({
  attachments,
  editable = false,
  onRemove,
  onDownload,
  className
}) => {
  /**
   * Handles attachment download action
   *
   * @param attachment - The attachment to download
   */
  const handleDownload = (attachment: Attachment): void => {
    // Check if the attachment is currently uploading
    if (!attachment.fileUrl) {
      return;
    }

    if (onDownload) {
      onDownload(attachment);
    } else if (attachment.fileUrl) {
      window.open(attachment.fileUrl, '_blank');
    }
  };

  if (!attachments || attachments.length === 0) {
    return null;
  }

  return (
    <Box className={className} sx={{ mt: 1 }}>
      <Box display="flex" alignItems="center" sx={{ mb: 0.5 }}>
        <AttachFileIcon fontSize="small" sx={{ mr: 0.5 }} />
        <Typography variant="body2" color="text.secondary">
          Attachments ({attachments.length})
        </Typography>
      </Box>
      <List dense disablePadding>
        {attachments.map((attachment) => {
          const isUploading = !attachment.fileUrl;
          
          return (
            <ListItem
              key={attachment.id}
              disablePadding
              sx={{
                borderRadius: 1,
                mb: 0.5,
                '&:hover': {
                  bgcolor: 'action.hover',
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>
                {getFileIcon(attachment.fileType)}
              </ListItemIcon>
              <ListItemText
                primary={attachment.fileName}
                secondary={formatFileSize(attachment.fileSize)}
                primaryTypographyProps={{
                  variant: 'body2',
                  noWrap: true,
                }}
                secondaryTypographyProps={{
                  variant: 'caption',
                }}
              />
              {isUploading ? (
                <CircularProgress size={24} />
              ) : (
                <>
                  <Tooltip title="Download">
                    <IconButton
                      size="small"
                      onClick={() => handleDownload(attachment)}
                      aria-label="download file"
                    >
                      <DownloadIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  {editable && onRemove && (
                    <Tooltip title="Remove">
                      <IconButton
                        size="small"
                        onClick={() => onRemove(attachment.id)}
                        aria-label="remove file"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                </>
              )}
            </ListItem>
          );
        })}
      </List>
    </Box>
  );
};

export default MessageAttachments;