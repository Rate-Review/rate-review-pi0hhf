import React, { useState, useEffect, useCallback } from 'react'; //  ^18.2.0
import { useDispatch, useSelector } from 'react-redux'; //  ^8.0.5
import { useForm, Controller } from 'react-hook-form'; //  ^7.43.0
import { object, string, array } from 'yup'; //  ^1.0.0
import { yupResolver } from '@hookform/resolvers/yup'; //  ^3.0.0
import TextField from '../common/TextField';
import Button from '../common/Button';
import Select from '../common/Select';
import FileUpload from '../common/FileUpload';
import { sendMessage, saveMessageDraft } from '../../store/messages/messagesThunks';
import { selectUsers } from '../../store/organizations/organizationsSlice';
import { RootState } from '../../store';
import { Message, MessageFormData, Attachment } from '../../types/message';
import useFileUpload from '../../hooks/useFileUpload';
import usePermissions from '../../hooks/usePermissions';

/**
 * @interface MessageFormProps
 * @description Props interface for the MessageForm component
 */
interface MessageFormProps {
  threadId?: string; // The ID of the message thread if replying within a thread
  parentId?: string; // The ID of the parent message if replying to a specific message
  recipientIds?: string[]; // Pre-selected recipient IDs
  initialValues?: MessageFormData; // Initial form values for editing drafts
  onSubmit?: (data: MessageFormData) => void; // Callback after successful submission
  onCancel?: () => void; // Callback when the form is cancelled
  isReply?: boolean; // Whether this form is for a reply (affects UI)
  saveDraft?: boolean; // Whether to enable draft saving feature
}

/**
 * @function MessageForm
 * @description A form component for composing new messages or replying to existing message threads
 * @param {MessageFormProps} props - The props for the component
 * @returns {ReactElement} The rendered form component
 */
const MessageForm: React.FC<MessageFormProps> = ({
  threadId,
  parentId,
  recipientIds,
  initialValues,
  onSubmit,
  onCancel,
  isReply,
  saveDraft = true,
}) => {
  // LD1: Define validation schema using yup with required content field (minimum length 2 chars)
  const validationSchema = object().shape({
    content: string().required('Message content is required').min(2, 'Message must be at least 2 characters'),
    recipientIds: array().of(string()).required('Please select at least one recipient').when('$isReply', {
      is: true,
      then: (schema) => schema.optional(),
      otherwise: (schema) => schema.required('Please select at least one recipient')
    }),
    attachments: array().of(object())
  });

  // LD1: Define form state using react-hook-form with yup resolver and defaultValues from initialValues
  const { control, handleSubmit, reset, formState: { errors, isDirty }, setValue } = useForm<MessageFormData>({
    resolver: yupResolver(validationSchema),
    defaultValues: initialValues || {},
    context: { isReply }
  });

  // LD1: Set up local state for attachments with useState
  const [attachments, setAttachments] = useState<Attachment[]>([]);

  // LD1: Set up local state for draft status (saved/saving) with useState
  const [draftStatus, setDraftStatus] = useState<'saved' | 'saving' | null>(null);

  // LD1: Set up file upload handlers with useFileUpload hook
  const {
    fileInputRef,
    file,
    fileError,
    isUploading,
    uploadProgress,
    uploadError,
    uploadResult,
    handleFileChange,
    handleFileDrop,
    uploadFile,
    cancelUpload,
    resetFileUpload
  } = useFileUpload({});

  // LD1: Set up Redux dispatch for sending messages and saving drafts
  const dispatch = useDispatch();

  // LD1: Use useSelector to get organization users for recipient selection
  const users = useSelector((state: RootState) => selectUsers(state.organizations));

  // LD1: Check messaging permissions with usePermissions hook
  const { can } = usePermissions();

  // LD1: Implement useEffect for auto-saving draft messages every 30 seconds when saveDraft is true
  useEffect(() => {
    if (saveDraft) {
      const intervalId = setInterval(() => {
        saveCurrentDraft();
      }, 30000);

      return () => clearInterval(intervalId);
    }
  }, [handleSubmit, threadId, parentId, saveDraft]);

  /**
   * @function handleSubmit
   * @description Function to handle form submission
   * @param {MessageFormData} data - The form data
   * @returns {Promise<void>} A promise that resolves when the submission is complete
   */
  const onSubmitHandler = async (data: MessageFormData) => {
    // LD1: Construct message object from form data and props
    const message: CreateMessageRequest = {
      content: data.content,
      threadId: threadId || null,
      parentId: parentId || null,
      recipientIds: data.recipientIds || [],
      attachments: [], // TODO: Implement attachment handling
      relatedEntityType: null, // TODO: Implement related entity handling
      relatedEntityId: null // TODO: Implement related entity handling
    };

    // LD1: Dispatch sendMessage action with message data
    dispatch(sendMessage(message));

    // LD1: Call onSubmit callback if provided
    if (onSubmit) {
      onSubmit(data);
    }

    // LD1: Reset form to initial state
    reset();

    // LD1: Clear attachments state
    setAttachments([]);
  };

  /**
   * @function handleAttachmentUpload
   * @description Function to handle file attachments
   * @param {File[]} files - The files to attach
   * @returns {void} No return value
   */
  const handleAttachmentUpload = (files: File[]) => {
    // LD1: Process each file through the file upload hook
    files.forEach(file => {
      // TODO: Implement file upload logic
      console.log('Uploading file:', file.name);
    });

    // LD1: Update attachments state with new files
    setAttachments([...attachments, ...files]);

    // LD1: Update form value for attachments field
    setValue('attachments', [...attachments, ...files]);
  };

  /**
   * @function handleAttachmentRemove
   * @description Function to remove file attachments
   * @param {number} index - The index of the attachment to remove
   * @returns {void} No return value
   */
  const handleAttachmentRemove = (index: number) => {
    // LD1: Create a copy of the current attachments array
    const newAttachments = [...attachments];

    // LD1: Remove the attachment at the specified index
    newAttachments.splice(index, 1);

    // LD1: Update attachments state with the new array
    setAttachments(newAttachments);

    // LD1: Update form value for attachments field
    setValue('attachments', newAttachments);
  };

  /**
   * @function handleCancel
   * @description Function to handle form cancellation
   * @returns {void} No return value
   */
  const handleCancel = () => {
    // LD1: Call onCancel prop if provided
    if (onCancel) {
      onCancel();
    } else {
      // LD1: Otherwise reset form to initial state
      reset();

      // LD1: Clear attachments state
      setAttachments([]);
    }
  };

  /**
   * @function saveCurrentDraft
   * @description Function to save the current draft state
   * @returns {void} No return value
   */
  const saveCurrentDraft = () => {
    // LD1: Get current form values
    const formValues = control._formValues;

    // LD1: If form is dirty (has changes)
    if (isDirty) {
      // LD1: Set draft status to 'saving'
      setDraftStatus('saving');

      // LD1: Construct draft message from form values and props
      const draftMessage: MessageFormData = {
        content: formValues.content,
        recipientIds: formValues.recipientIds
      };

      // LD1: Dispatch saveMessageDraft action
      dispatch(saveMessageDraft(draftMessage));

      // LD1: Set draft status to 'saved' after successful save
      setDraftStatus('saved');

      // LD1: Set timeout to reset draft status after 3 seconds
      setTimeout(() => {
        setDraftStatus(null);
      }, 3000);
    }
  };

  // LD1: Render form with Controller components for react-hook-form fields
  return (
    <form onSubmit={handleSubmit(onSubmitHandler)}>
      {/* LD1: Render TextField for message content with error handling */}
      <Controller
        name="content"
        control={control}
        render={({ field }) => (
          <TextField
            label="Message"
            multiline
            rows={4}
            fullWidth
            error={errors.content?.message}
            {...field}
          />
        )}
      />

      {/* LD1: Render Select for recipients with error handling if not replying to existing thread */}
      {!isReply && (
        <Controller
          name="recipientIds"
          control={control}
          render={({ field }) => (
            <Select
              label="Recipients"
              multiple
              fullWidth
              options={users.map(user => ({ value: user.id, label: user.name }))}
              error={errors.recipientIds?.message}
              {...field}
            />
          )}
        />
      )}

      {/* LD1: Render FileUpload for attachments with upload and remove handlers */}
      <FileUpload
        onUpload={handleAttachmentUpload}
        onCancel={handleAttachmentRemove}
      />

      {/* LD1: Render action buttons (Send, Cancel) with appropriate handlers */}
      <div>
        <Button type="submit" variant="primary">Send</Button>
        <Button type="button" variant="outline" onClick={handleCancel}>Cancel</Button>
      </div>

      {/* LD1: Show draft status indicator when auto-save is enabled and active */}
      {saveDraft && draftStatus === 'saving' && <p>Saving draft...</p>}
      {saveDraft && draftStatus === 'saved' && <p>Draft saved!</p>}
    </form>
  );
};

export default MessageForm;