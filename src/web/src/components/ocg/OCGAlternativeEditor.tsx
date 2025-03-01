import React, { useState, useEffect, ChangeEvent } from 'react'; //  ^18.0.0
import {
  Card,
  CardContent,
  Typography,
  IconButton,
  Box,
  Divider
} from '@mui/material'; //  ^5.14.0
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon
} from '@mui/icons-material'; //  ^5.14.0
import { v4 as uuidv4 } from 'uuid'; //  ^9.0.0
import { OCGAlternative } from '../../types/ocg';
import Button from '../common/Button';
import TextField from '../common/TextField';

/**
 * Props for the OCGAlternativeEditor component
 */
interface OCGAlternativeEditorProps {
  alternatives: OCGAlternative[];
  onChange: (alternatives: OCGAlternative[]) => void;
  readOnly?: boolean;
}

/**
 * A component that allows editing of alternative options for negotiable OCG sections,
 * including adding, editing, and removing alternatives with point values.
 */
const OCGAlternativeEditor: React.FC<OCGAlternativeEditorProps> = ({
  alternatives,
  onChange,
  readOnly
}) => {
  // Initialize state for editing alternative
  const [editingAlternative, setEditingAlternative] = useState<OCGAlternative | null>(null);

  // Initialize state for form fields
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [editPoints, setEditPoints] = useState<number>(0);

  /**
   * Adds a new empty alternative to the list
   */
  const handleAddAlternative = () => {
    // Generate a new unique ID
    const newId = uuidv4();

    // Create a new alternative object with default values
    const newAlternative: OCGAlternative = {
      id: newId,
      title: 'New Alternative',
      content: 'Enter content here',
      points: 0,
      isDefault: false,
    };

    // Create a new array with existing alternatives plus the new one
    const updatedAlternatives = [...alternatives, newAlternative];

    // Call onChange prop with the updated alternatives array
    onChange(updatedAlternatives);
  };

  /**
   * Starts editing an existing alternative
   * @param alternative - The alternative to edit
   */
  const handleEditAlternative = (alternative: OCGAlternative) => {
    // Set the editingAlternative state to the selected alternative
    setEditingAlternative(alternative);

    // Initialize editTitle state with alternative.title
    setEditTitle(alternative.title);

    // Initialize editContent state with alternative.content
    setEditContent(alternative.content);

    // Initialize editPoints state with alternative.points
    setEditPoints(alternative.points);
  };

  /**
   * Saves the current edits to the alternative
   */
  const handleSaveEdit = () => {
    // Create a new alternatives array by mapping through existing alternatives
    const updatedAlternatives = alternatives.map(alt => {
      // When finding the editingAlternative.id, return an updated object with edited values
      if (alt.id === editingAlternative?.id) {
        return {
          ...alt,
          title: editTitle,
          content: editContent,
          points: editPoints,
        };
      }
      return alt;
    });

    // Call onChange prop with the updated alternatives array
    onChange(updatedAlternatives);

    // Reset editingAlternative to null and clear edit states
    setEditingAlternative(null);
    setEditTitle('');
    setEditContent('');
    setEditPoints(0);
  };

  /**
   * Cancels the current edit operation
   */
  const handleCancelEdit = () => {
    // Reset editingAlternative to null
    setEditingAlternative(null);

    // Clear editTitle, editContent, and editPoints states
    setEditTitle('');
    setEditContent('');
    setEditPoints(0);
  };

  /**
   * Deletes an alternative from the list
   * @param id - The ID of the alternative to delete
   */
  const handleDeleteAlternative = (id: string) => {
    // Filter the alternatives array to remove the one with the matching id
    const updatedAlternatives = alternatives.filter(alt => alt.id !== id);

    // Call onChange prop with the filtered alternatives array
    onChange(updatedAlternatives);
  };

  /**
   * Updates the editTitle state as user types
   * @param event - The change event from the title input
   */
  const handleTitleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    // Update the editTitle state with event.target.value
    setEditTitle(event.target.value);
  };

  /**
   * Updates the editContent state as user types
   * @param event - The change event from the content input
   */
  const handleContentChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    // Update the editContent state with event.target.value
    setEditContent(event.target.value);
  };

  /**
   * Updates the editPoints state as user types
   * @param event - The change event from the points input
   */
  const handlePointsChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    // Parse the input value as a number
    const parsedValue = Number(event.target.value);

    // Update the editPoints state with the parsed number value
    if (!isNaN(parsedValue)) {
      setEditPoints(parsedValue);
    } else {
      // If the input is not a valid number, set editPoints to 0
      setEditPoints(0);
    }
  };

  return (
    <Box>
      {/* Render alternatives list with edit controls */}
      {alternatives.map(alternative => (
        <Card key={alternative.id} sx={{ mb: 1 }}>
          <CardContent>
            <Typography variant="h6">{alternative.title}</Typography>
            <Typography variant="body2">{alternative.content}</Typography>
            <Typography variant="caption">Points: {alternative.points}</Typography>
            {!readOnly && (
              <Box sx={{ mt: 1, display: 'flex', justifyContent: 'flex-end' }}>
                <IconButton
                  aria-label="edit"
                  onClick={() => handleEditAlternative(alternative)}
                >
                  <EditIcon />
                </IconButton>
                <IconButton
                  aria-label="delete"
                  onClick={() => handleDeleteAlternative(alternative.id)}
                >
                  <DeleteIcon />
                </IconButton>
              </Box>
            )}
          </CardContent>
        </Card>
      ))}

      {/* Render edit form when an alternative is being edited */}
      {editingAlternative && (
        <Card sx={{ mt: 2 }}>
          <CardContent>
            <Typography variant="h6">Edit Alternative</Typography>
            <TextField
              label="Title"
              value={editTitle}
              onChange={handleTitleChange}
              fullWidth
            />
            <TextField
              label="Content"
              value={editContent}
              onChange={handleContentChange}
              fullWidth
              multiline
              rows={4}
            />
            <TextField
              label="Points"
              type="number"
              value={editPoints.toString()}
              onChange={handlePointsChange}
              fullWidth
            />
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button variant="outlined" onClick={handleCancelEdit}>
                Cancel
              </Button>
              <Button onClick={handleSaveEdit}>Save</Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Render add button when not in read-only mode */}
      {!readOnly && !editingAlternative && (
        <Button
          startIcon={<AddIcon />}
          onClick={handleAddAlternative}
          sx={{ mt: 2 }}
        >
          Add Alternative
        </Button>
      )}
    </Box>
  );
};

export default OCGAlternativeEditor;