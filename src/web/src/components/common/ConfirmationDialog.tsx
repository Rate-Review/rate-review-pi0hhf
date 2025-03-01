import React from 'react';
import styled from 'styled-components';
import { Modal } from './Modal';
import { Button } from './Button';

interface ConfirmationDialogProps {
  isOpen: boolean;
  title: string;
  message?: string;
  confirmText?: string;
  cancelText?: string;
  confirmButtonVariant?: 'primary' | 'secondary' | 'danger';
  onConfirm: () => void;
  onCancel: () => void;
  children?: React.ReactNode;
}

const DialogContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 500px;
  background-color: ${props => props.theme.colors.background};
  border-radius: ${props => props.theme.borderRadius.md};
  box-shadow: ${props => props.theme.shadows.md};
  overflow: hidden;
`;

const DialogTitle = styled.div`
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.md};
  border-bottom: 1px solid ${props => props.theme.colors.border};
  font-weight: ${props => props.theme.fontWeights.medium};
  font-size: ${props => props.theme.fontSizes.lg};
`;

const DialogContent = styled.div`
  padding: ${props => props.theme.spacing.md};
  flex-grow: 1;
  overflow-y: auto;
`;

const DialogActions = styled.div`
  display: flex;
  justify-content: flex-end;
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-top: 1px solid ${props => props.theme.colors.border};
  gap: ${props => props.theme.spacing.sm};
`;

/**
 * A reusable confirmation dialog component that prompts users to confirm or cancel actions.
 */
const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  isOpen,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  confirmButtonVariant = 'primary',
  onConfirm,
  onCancel,
  children
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onCancel}
      hideCloseButton
      size="auto"
    >
      <DialogContainer>
        <DialogTitle>{title}</DialogTitle>
        
        <DialogContent>
          {message ? <p>{message}</p> : children}
        </DialogContent>
        
        <DialogActions>
          <Button
            variant="outline"
            onClick={onCancel}
          >
            {cancelText}
          </Button>
          
          <Button
            variant={confirmButtonVariant}
            onClick={onConfirm}
            color={confirmButtonVariant === 'danger' ? 'error' : confirmButtonVariant}
          >
            {confirmText}
          </Button>
        </DialogActions>
      </DialogContainer>
    </Modal>
  );
};

export { ConfirmationDialog };