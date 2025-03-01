import React, { ReactNode, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import styled from 'styled-components';

// Define the possible modal sizes
type ModalSize = 'small' | 'medium' | 'large' | 'auto';

// Define the props interface for the Modal component
interface ModalProps {
  /** Controls whether the modal is displayed */
  isOpen: boolean;
  /** Function called when the modal should close */
  onClose: () => void;
  /** Optional title text for the modal header */
  title?: string;
  /** Size of the modal - small, medium, large, or auto */
  size?: ModalSize;
  /** Optional class name for additional styling */
  className?: string;
  /** Whether to hide the close button in the header */
  hideCloseButton?: boolean;
  /** Whether to close the modal when clicking the overlay */
  closeOnOverlayClick?: boolean;
  /** Whether to close the modal when pressing the Escape key */
  closeOnEscapeKey?: boolean;
  /** Optional content for the header in addition to/instead of the title */
  headerContent?: ReactNode;
  /** Content to be displayed in the modal */
  children: ReactNode;
}

// Styled components for the modal
const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: ${props => props.theme.spacing.md || '16px'};
`;

const ModalContainer = styled.div<{ size?: ModalSize }>`
  background-color: ${props => props.theme.colors?.background || '#FFFFFF'};
  border-radius: ${props => props.theme.borderRadius?.md || '4px'};
  box-shadow: ${props => props.theme.shadows?.lg || '0 10px 15px rgba(0, 0, 0, 0.1)'};
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 32px);
  width: ${props => {
    switch (props.size) {
      case 'small': return '400px';
      case 'medium': return '600px';
      case 'large': return '800px';
      case 'auto': return 'auto';
      default: return '600px';
    }
  }};
  max-width: 100%;
  overflow: hidden;
  position: relative;
`;

const ModalHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing?.md || '16px'};
  border-bottom: ${props => `${props.theme.borderWidth || '1px'} solid ${props.theme.colors?.border || '#EEEEEE'}`};
`;

const ModalTitle = styled.h2`
  margin: 0;
  font-weight: ${props => props.theme.fontWeights?.medium || '500'};
  font-size: ${props => props.theme.fontSizes?.lg || '18px'};
  color: ${props => props.theme.colors?.text || '#333333'};
`;

const CloseButton = styled.button`
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing?.xs || '4px'};
  color: ${props => props.theme.colors?.neutral || '#718096'};
  border-radius: ${props => props.theme.borderRadius?.sm || '2px'};
  font-size: ${props => props.theme.fontSizes?.lg || '18px'};
  
  &:hover, &:focus {
    background-color: ${props => props.theme.colors?.backgroundLight || '#F7FAFC'};
    color: ${props => props.theme.colors?.text || '#333333'};
  }
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px ${props => props.theme.colors?.primaryLight || '#90CDF4'};
  }
`;

const ModalContent = styled.div`
  padding: ${props => props.theme.spacing?.md || '16px'};
  overflow-y: auto;
  flex: 1;
`;

/**
 * Modal component for displaying content in a dialog box with overlay
 */
const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  size = 'medium',
  className,
  hideCloseButton = false,
  closeOnOverlayClick = true,
  closeOnEscapeKey = true,
  headerContent,
  children
}) => {
  // Ref for the modal container
  const modalRef = useRef<HTMLDivElement>(null);

  // Handle Escape key press
  useEffect(() => {
    const handleEscapeKey = (event: KeyboardEvent) => {
      if (isOpen && closeOnEscapeKey && event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen && closeOnEscapeKey) {
      document.addEventListener('keydown', handleEscapeKey);
    }

    return () => {
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [isOpen, onClose, closeOnEscapeKey]);

  // Manage body scroll locking when modal is open
  useEffect(() => {
    if (isOpen) {
      // Save the current scroll position and body style
      const scrollY = window.scrollY;
      const bodyStyle = document.body.style.cssText;
      
      // Prevent scrolling on the body
      document.body.style.position = 'fixed';
      document.body.style.top = `-${scrollY}px`;
      document.body.style.width = '100%';
      
      return () => {
        // Restore body style and scroll position when modal closes
        document.body.style.cssText = bodyStyle;
        window.scrollTo(0, scrollY);
      };
    }
  }, [isOpen]);

  // Focus the modal container when it opens
  useEffect(() => {
    if (isOpen && modalRef.current) {
      // Find the first focusable element in the modal
      const focusableElements = modalRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      
      // Focus the first element or the container itself
      if (focusableElements.length > 0) {
        (focusableElements[0] as HTMLElement).focus();
      } else {
        modalRef.current.focus();
      }
    }
  }, [isOpen]);

  // Return null if the modal shouldn't be open
  if (!isOpen) {
    return null;
  }

  // Handle clicks on the overlay
  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (closeOnOverlayClick && e.target === e.currentTarget) {
      onClose();
    }
  };

  return createPortal(
    <ModalOverlay 
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? "modal-title" : undefined}
    >
      <ModalContainer
        ref={modalRef}
        size={size}
        className={className}
        tabIndex={-1}
        role="document"
      >
        <ModalHeader>
          {(title || headerContent) && (
            <>
              {title && <ModalTitle id="modal-title">{title}</ModalTitle>}
              {headerContent}
            </>
          )}
          {!hideCloseButton && (
            <CloseButton 
              onClick={onClose}
              aria-label="Close modal"
            >
              ×
            </CloseButton>
          )}
        </ModalHeader>
        <ModalContent>
          {children}
        </ModalContent>
      </ModalContainer>
    </ModalOverlay>,
    document.body
  );
};

export default Modal;