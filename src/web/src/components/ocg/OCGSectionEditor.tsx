import React, { useState, useEffect, ChangeEvent } from 'react'; //  ^18.0.0
import {
  Card,
  CardContent,
  Typography,
  Divider,
  Box,
  Switch,
  FormControlLabel
} from '@mui/material'; //  ^5.14.0
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  ExpandMore,
  ExpandLess
} from '@mui/icons-material'; //  ^5.14.0
import { v4 as uuidv4 } from 'uuid'; //  ^9.0.0
import { OCGSection, OCGAlternative } from '../../types/ocg';
import TextField from '../common/TextField';
import Button from '../common/Button';
import OCGAlternativeEditor from './OCGAlternativeEditor';

/**
 * Props for the OCGSectionEditor component
 */
interface OCGSectionEditorProps {
  section: OCGSection;
  onChange: (updatedSection: OCGSection) => void;
  onDelete: (sectionId: string) => void;
  readOnly?: boolean;
}

/**
 * A component for editing OCG sections, including title, content, negotiability status, and alternatives.
 */
const OCGSectionEditor: React.FC<OCGSectionEditorProps> = ({
  section,
  onChange,
  onDelete,
  readOnly
}) => {
  // Initialize state for section data
  const [title, setTitle] = useState(section.title);
  const [content, setContent] = useState(section.content);
  const [isNegotiable, setIsNegotiable] = useState(section.isNegotiable);
  const [alternatives, setAlternatives] = useState<OCGAlternative[]>(section.alternatives);

  // Initialize state for UI controls
  const [isExpanded, setIsExpanded] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [showAlternatives, setShowAlternatives] = useState(false);

  // Use useEffect to update state when section prop changes
  useEffect(() => {
    setTitle(section.title);
    setContent(section.content);
    setIsNegotiable(section.isNegotiable);
    setAlternatives(section.alternatives);
  }, [section]);

  /**
   * Toggles the expanded state of the section
   */
  const handleToggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  /**
   * Toggles the editing state of the section
   */
  const handleToggleEdit = () => {
    if (!isEditing) {
      setIsExpanded(true);
    } else {
      setTitle(section.title);
      setContent(section.content);
      setIsNegotiable(section.isNegotiable);
      setAlternatives(section.alternatives);
    }
    setIsEditing(!isEditing);
  };

  /**
   * Updates the section title as user types
   * @param value - The new title value
   */
  const handleTitleChange = (value: string | React.ChangeEvent<HTMLInputElement>) => {
    const newTitle = typeof value === 'string' ? value : value.target.value;
    setTitle(newTitle);
  };

  /**
   * Updates the section content as user types
   * @param value - The new content value
   */
  const handleContentChange = (value: string | React.ChangeEvent<HTMLInputElement>) => {
    const newContent = typeof value === 'string' ? value : value.target.value;
    setContent(newContent);
  };

  /**
   * Toggles whether the section is negotiable
   * @param event - The change event from the toggle
   */
  const handleNegotiableChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const checked = event.target.checked;

    if (!checked && alternatives.length > 0) {
      const confirmResult = window.confirm(
        "Are you sure you want to disable negotiability? All alternatives will be removed."
      );
      if (!confirmResult) {
        event.preventDefault();
        return;
      }
      setAlternatives([]);
      setIsNegotiable(false);
      return;
    }

    if (checked && alternatives.length === 0) {
      const defaultAlternative = createDefaultAlternative();
      setAlternatives([defaultAlternative]);
    }

    setIsNegotiable(checked);
  };

  /**
   * Updates the alternatives list when changes are made in the OCGAlternativeEditor
   * @param newAlternatives - The updated alternatives array
   */
  const handleAlternativesChange = (newAlternatives: OCGAlternative[]) => {
    setAlternatives(newAlternatives);
  };

  /**
   * Handles deletion of the section
   */
  const handleDelete = () => {
    if (content.length > 0) {
      const confirmResult = window.confirm(
        "Are you sure you want to delete this section? All content will be lost."
      );
      if (!confirmResult) {
        return;
      }
    }
    onDelete(section.id);
  };

  /**
   * Saves the current section changes
   */
  const handleSave = () => {
    const updatedSection: OCGSection = {
      ...section,
      title: title,
      content: content,
      isNegotiable: isNegotiable,
      alternatives: alternatives,
    };
    onChange(updatedSection);
    setIsEditing(false);
  };

  /**
   * Creates a default alternative when a section becomes negotiable
   */
  const createDefaultAlternative = (): OCGAlternative => {
    const newId = uuidv4();
    return {
      id: newId,
      title: 'Standard',
      content: 'Default language',
      points: 0,
      isDefault: true,
    };
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            {section.title}
          </Typography>
          <Box>
            {!readOnly && (
              <>
                <Button
                  size="small"
                  variant="text"
                  onClick={handleToggleEdit}
                  aria-label={isEditing ? "Cancel Edit" : "Edit Section"}
                >
                  {isEditing ? 'Cancel' : 'Edit'}
                </Button>
                <Button
                  size="small"
                  variant="text"
                  color="error"
                  onClick={handleDelete}
                  aria-label="Delete Section"
                >
                  Delete
                </Button>
              </>
            )}
          </Box>
        </Box>
        {isEditing ? (
          <>
            <TextField
              label="Title"
              value={title}
              onChange={handleTitleChange}
              fullWidth
            />
            <TextField
              label="Content"
              value={content}
              onChange={handleContentChange}
              fullWidth
              multiline
              rows={4}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={isNegotiable}
                  onChange={handleNegotiableChange}
                  name="negotiable"
                  disabled={readOnly}
                />
              }
              label="Negotiable"
            />
            {isNegotiable && (
              <OCGAlternativeEditor
                alternatives={alternatives}
                onChange={handleAlternativesChange}
                readOnly={readOnly}
              />
            )}
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button variant="outlined" onClick={handleToggleEdit}>
                Cancel
              </Button>
              <Button onClick={handleSave}>Save</Button>
            </Box>
          </>
        ) : (
          <>
            <Typography variant="body1">{section.content}</Typography>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default OCGSectionEditor;