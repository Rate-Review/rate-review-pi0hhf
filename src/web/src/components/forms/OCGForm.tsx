import React, { useState, useEffect, useCallback } from 'react'; //  ^18.2.0
import {
  Box,
  Card,
  CardContent,
  Typography,
  Divider,
  Stack,
  Grid,
  FormHelperText
} from '@mui/material'; //  ^5.14.0
import { toast } from 'react-toastify'; //  ^9.1.3
import { v4 as uuidv4 } from 'uuid'; //  ^9.0.0
import TextField from '../common/TextField';
import Button from '../common/Button';
import OCGSectionEditor from '../ocg/OCGSectionEditor';
import OCGAlternativeEditor from '../ocg/OCGAlternativeEditor';
import useOCG from '../../hooks/useOCG';
import {
  OCGDocument,
  CreateOCGRequest,
  UpdateOCGRequest,
  OCGSection,
  OCGStatus
} from '../../types/ocg';

/**
 * Interface defining the properties for the OCGForm component.
 * It includes initial data, submit and cancel handlers, update flag, and client ID.
 */
interface OCGFormProps {
  initialData?: OCGDocument | null;
  onSubmit: (ocg: OCGDocument) => void;
  onCancel?: () => void;
  isUpdate?: boolean;
  clientId?: string;
}

/**
 * Interface defining the internal state for the OCGForm component.
 * It includes the title, sections, total points, and default firm point budget.
 */
interface OCGFormState {
  title: string;
  sections: OCGSection[];
  totalPoints: number;
  defaultFirmPointBudget: number;
  clientId: string | null;
}

/**
 * Interface defining the error state for OCGForm validation.
 * It includes error messages for the title, sections, total points, and default firm point budget.
 */
interface OCGFormErrors {
  title: string | null;
  sections: string | null;
  totalPoints: string | null;
  defaultFirmPointBudget: string | null;
  general: string | null;
}

/**
 * Main component function for OCG form that handles creation and updates
 */
const OCGForm: React.FC<OCGFormProps> = ({ initialData, onSubmit, onCancel, isUpdate = false, clientId: clientIdProp }) => {
  // LD1: Destructure props to access initialData, onSubmit, onCancel, and isUpdate flags
  // LD1: Initialize form state using initialData or defaults (title, sections, totalPoints, etc.)
  const [formState, setFormState] = useState<OCGFormState>({
    title: initialData?.title || '',
    sections: initialData?.sections || [],
    totalPoints: initialData?.totalPoints || 100,
    defaultFirmPointBudget: initialData?.defaultFirmPointBudget || 50,
    clientId: clientIdProp || initialData?.clientId || null,
  });

  // LD1: Initialize error state for form validation
  const [errors, setErrors] = useState<OCGFormErrors>({
    title: null,
    sections: null,
    totalPoints: null,
    defaultFirmPointBudget: null,
    general: null,
  });

  // LD1: Initialize loading state for form submission
  const [loading, setLoading] = useState(false);

  // LD1: Use useOCG hook to access OCG management functions
  const { createOCG, updateOCG } = useOCG();

  /**
   * Updates form state when input values change
   */
  const handleInputChange = (field: string, value: any) => {
    // LD1: Update form state with the new value for the specified field
    setFormState({
      ...formState,
      [field]: value,
    });
    // LD1: Clear any related error messages
    setErrors({
      ...errors,
      [field]: null,
    });
  };

  /**
   * Updates a section in the form state
   */
  const handleSectionChange = (updatedSection: OCGSection) => {
    // LD1: Find the section in the sections array
    // LD1: Create updated sections array with the changed section
    const updatedSections = formState.sections.map(section =>
      section.id === updatedSection.id ? updatedSection : section
    );
    // LD1: Update the form state with the new sections array
    setFormState({
      ...formState,
      sections: updatedSections,
    });
    // LD1: Clear any section-related error messages
    setErrors({
      ...errors,
      sections: null,
    });
  };

  /**
   * Adds a new section to the OCG
   */
  const handleAddSection = () => {
    // LD1: Generate a unique ID for the new section using uuidv4
    const newSectionId = uuidv4();
    // LD1: Create a new section object with default values
    const newSection: OCGSection = {
      id: newSectionId,
      title: 'New Section',
      content: '',
      isNegotiable: false,
      alternatives: [],
      order: formState.sections.length,
    };
    // LD1: Add the new section to the sections array in form state
    setFormState({
      ...formState,
      sections: [...formState.sections, newSection],
    });
    // LD1: Clear any section-related error messages
    setErrors({
      ...errors,
      sections: null,
    });
  };

  /**
   * Removes a section from the OCG
   */
  const handleRemoveSection = (sectionId: string) => {
    // LD1: Filter out the section with the matching ID from the sections array
    const updatedSections = formState.sections.filter(section => section.id !== sectionId);
    // LD1: Update the form state with the new sections array
    setFormState({
      ...formState,
      sections: updatedSections,
    });
  };

  /**
   * Updates the totalPoints or defaultFirmPointBudget in form state
   */
  const handlePointBudgetChange = (field: string, value: number) => {
    // LD1: Validate that value is a positive number
    if (value < 0) {
      setErrors({
        ...errors,
        [field]: 'Value must be a positive number',
      });
      return;
    }

    // LD1: If field is defaultFirmPointBudget, validate it's not greater than totalPoints
    if (field === 'defaultFirmPointBudget' && value > formState.totalPoints) {
      setErrors({
        ...errors,
        [field]: 'Default firm point budget cannot exceed total points',
      });
      return;
    }

    // LD1: Update the form state with the new value
    setFormState({
      ...formState,
      [field]: value,
    });
    // LD1: Clear any related error messages
    setErrors({
      ...errors,
      [field]: null,
    });
  };

  /**
   * Validates the form data before submission
   */
  const validateForm = (): boolean => {
    // LD1: Initialize errors object
    let newErrors: OCGFormErrors = {
      title: null,
      sections: null,
      totalPoints: null,
      defaultFirmPointBudget: null,
      general: null,
    };

    // LD1: Check if title is provided
    if (!formState.title) {
      newErrors.title = 'Title is required';
    }

    // LD1: Check if at least one section exists
    if (formState.sections.length === 0) {
      newErrors.sections = 'At least one section is required';
    }

    // LD1: Check if totalPoints is a positive number
    if (formState.totalPoints <= 0) {
      newErrors.totalPoints = 'Total points must be a positive number';
    }

    // LD1: Check if defaultFirmPointBudget is valid and not greater than totalPoints
    if (formState.defaultFirmPointBudget > formState.totalPoints) {
      newErrors.defaultFirmPointBudget = 'Default firm point budget cannot exceed total points';
    }

    // LD1: Set error state with any validation errors
    setErrors(newErrors);

    // LD1: Return true if no errors, false otherwise
    return Object.values(newErrors).every(error => error === null);
  };

  /**
   * Processes form submission
   */
  const handleSubmit = async (event: React.FormEvent) => {
    // LD1: Prevent default form submission
    event.preventDefault();

    // LD1: Validate form data using validateForm
    if (!validateForm()) {
      // LD1: If form is invalid, show error toast and return
      toast.error('Please correct the errors below.');
      return;
    }

    // LD1: Set loading state to true
    setLoading(true);

    try {
      // LD1: Prepare submission data (CreateOCGRequest or UpdateOCGRequest)
      const submissionData: CreateOCGRequest | UpdateOCGRequest = {
        title: formState.title,
        sections: formState.sections,
        totalPoints: formState.totalPoints,
        clientId: formState.clientId || '',
      };

      let result: OCGDocument | undefined;

      // LD1: Call appropriate OCG function based on isUpdate flag
      if (isUpdate && initialData) {
        result = await updateOCG(initialData.id, submissionData as UpdateOCGRequest);
      } else {
        result = await createOCG(submissionData as CreateOCGRequest);
      }

      // LD1: On success, call onSubmit callback with result
      if (result) {
        onSubmit(result);
        toast.success(`OCG ${isUpdate ? 'updated' : 'created'} successfully!`);
      } else {
        throw new Error('Failed to create or update OCG');
      }
    } catch (error: any) {
      // LD1: On error, set error state and show error toast
      setErrors({
        ...errors,
        general: error.message,
      });
      toast.error(`Failed to ${isUpdate ? 'update' : 'create'} OCG: ${error.message}`);
    } finally {
      // LD1: Set loading state to false regardless of outcome
      setLoading(false);
    }
  };

  /**
   * Handles form cancellation
   */
  const handleCancel = () => {
    // LD1: Call onCancel callback if provided
    onCancel?.();
  };

  // LD1: Render form elements including title field, sections list, and point budget inputs
  return (
    <form onSubmit={handleSubmit}>
      <TextField
        label="Title"
        value={formState.title}
        onChange={(e) => handleInputChange('title', e.target.value)}
        error={errors.title}
        fullWidth
        required
      />
      {formState.sections.map(section => (
        <OCGSectionEditor
          key={section.id}
          section={section}
          onChange={handleSectionChange}
          onDelete={handleRemoveSection}
        />
      ))}
      <Button variant="outlined" onClick={handleAddSection}>Add Section</Button>
      {errors.sections && <FormHelperText error>{errors.sections}</FormHelperText>}

      <TextField
        label="Total Points"
        type="number"
        value={formState.totalPoints.toString()}
        onChange={(e) => handlePointBudgetChange('totalPoints', Number(e.target.value))}
        error={errors.totalPoints}
        fullWidth
        required
      />

      <TextField
        label="Default Firm Point Budget"
        type="number"
        value={formState.defaultFirmPointBudget.toString()}
        onChange={(e) => handlePointBudgetChange('defaultFirmPointBudget', Number(e.target.value))}
        error={errors.defaultFirmPointBudget}
        fullWidth
        required
      />

      {/* LD1: Render error messages for form validation */}
      {errors.general && <FormHelperText error>{errors.general}</FormHelperText>}

      {/* LD1: Render form action buttons (submit, cancel) */}
      <Stack direction="row" justifyContent="flex-end" spacing={2} mt={3}>
        <Button variant="outlined" onClick={handleCancel} disabled={loading}>
          Cancel
        </Button>
        <Button type="submit" variant="contained" disabled={loading}>
          {isUpdate ? 'Update' : 'Create'}
        </Button>
      </Stack>
    </form>
  );
};

export default OCGForm;