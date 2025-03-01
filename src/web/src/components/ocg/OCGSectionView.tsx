import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Radio,
  RadioGroup,
  FormControlLabel,
  Collapse,
  IconButton,
  Paper,
  Divider
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { ExpandMore, ExpandLess, Edit } from '@mui/icons-material';

import Card from '../common/Card';
import Button from '../common/Button';
import Badge from '../common/Badge';
import Tooltip from '../common/Tooltip';
import { OCGSectionType, OCGAlternativeType } from '../../types/ocg';

/**
 * Props for the OCGSectionView component
 */
interface OCGSectionViewProps {
  /**
   * The OCG section data to display
   */
  section: OCGSectionType;
  
  /**
   * Whether the component is in edit mode
   * @default false
   */
  editMode?: boolean;
  
  /**
   * Whether the component is in negotiation mode
   * @default false
   */
  negotiationMode?: boolean;
  
  /**
   * Whether the section is being negotiated by the law firm
   * @default false
   */
  lawFirmView?: boolean;
  
  /**
   * The currently selected alternative ID
   */
  selectedAlternativeId?: string;
  
  /**
   * Remaining points available for selection
   */
  remainingPoints?: number;
  
  /**
   * Callback for when edit button is clicked
   */
  onEdit?: (sectionId: string) => void;
  
  /**
   * Callback for when an alternative is selected
   */
  onAlternativeSelect?: (sectionId: string, alternativeId: string) => void;
  
  /**
   * Additional class name
   */
  className?: string;
}

// Styled components
const SectionHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: theme.spacing(2),
  cursor: 'pointer',
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
}));

const SectionContent = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
}));

const AlternativeOption = styled(Paper, {
  shouldForwardProp: (prop) => prop !== 'isSelected' && prop !== 'isSelectable'
})<{ isSelected?: boolean; isSelectable?: boolean }>(({ theme, isSelected, isSelectable }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  borderWidth: '1px',
  borderStyle: 'solid',
  borderColor: isSelected ? theme.palette.primary.main : theme.palette.divider,
  borderRadius: theme.shape.borderRadius,
  transition: theme.transitions.create(['border-color', 'box-shadow']),
  boxShadow: isSelected ? theme.shadows[2] : 'none',
  opacity: (!isSelectable && !isSelected) ? 0.6 : 1,
  '&:hover': {
    borderColor: isSelectable || isSelected ? theme.palette.primary.light : theme.palette.divider,
  }
}));

/**
 * A React functional component that renders an Outside Counsel Guidelines section with options for
 * viewing, editing, and negotiation. Supports displaying negotiable sections with alternative options
 * and their point values, used in both client and law firm interfaces.
 */
const OCGSectionView: React.FC<OCGSectionViewProps> = ({
  section,
  editMode = false,
  negotiationMode = false,
  lawFirmView = false,
  selectedAlternativeId,
  remainingPoints = 0,
  onEdit,
  onAlternativeSelect,
  className,
}) => {
  // State for expanded/collapsed section
  const [expanded, setExpanded] = useState<boolean>(true);
  
  // State for selected alternative
  const [selectedOption, setSelectedOption] = useState<string | undefined>(selectedAlternativeId);
  
  // Update selected option when prop changes
  useEffect(() => {
    setSelectedOption(selectedAlternativeId);
  }, [selectedAlternativeId]);
  
  // Toggle expanded state
  const handleExpandToggle = () => {
    setExpanded(!expanded);
  };
  
  // Handle alternative selection
  const handleAlternativeSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const alternativeId = event.target.value;
    setSelectedOption(alternativeId);
    if (onAlternativeSelect) {
      onAlternativeSelect(section.id, alternativeId);
    }
  };
  
  // Determine if an alternative can be selected based on point budget
  const isAlternativeSelectable = useCallback((alternative: OCGAlternativeType): boolean => {
    // If already selected, it's selectable
    if (alternative.id === selectedOption) {
      return true;
    }
    
    // Find currently selected alternative
    const currentSelection = section.alternatives.find(alt => alt.id === selectedOption);
    
    // Calculate point difference
    const pointDifference = alternative.points - (currentSelection?.points || 0);
    
    // Return whether remaining points is sufficient
    return pointDifference <= remainingPoints;
  }, [selectedOption, remainingPoints, section.alternatives]);
  
  return (
    <Card variant="outlined" className={`ocg-section ${className || ''}`}>
      <SectionHeader onClick={handleExpandToggle}>
        <Box display="flex" alignItems="center">
          <Typography variant="h6">{section.title}</Typography>
          {section.isNegotiable && (
            <Tooltip content="This section is negotiable with alternative options">
              <Badge 
                content="Negotiable" 
                variant="secondary" 
                size="small" 
                style={{ marginLeft: 8 }}
              />
            </Tooltip>
          )}
        </Box>
        <Box display="flex" alignItems="center">
          {editMode && !negotiationMode && (
            <Button 
              variant="text" 
              size="small" 
              onClick={(e) => {
                e.stopPropagation();
                if (onEdit) onEdit(section.id);
              }}
              aria-label={`Edit ${section.title} section`}
            >
              <Edit fontSize="small" style={{ marginRight: 4 }} />
              Edit
            </Button>
          )}
          <IconButton
            size="small"
            onClick={handleExpandToggle}
            aria-expanded={expanded}
            aria-label={expanded ? `Collapse ${section.title} section` : `Expand ${section.title} section`}
          >
            {expanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>
      </SectionHeader>
      
      <Collapse in={expanded}>
        <Divider />
        <SectionContent>
          {/* Non-negotiable section just shows content */}
          {!section.isNegotiable && (
            <Typography variant="body1">{section.content}</Typography>
          )}
          
          {/* Negotiable section shows alternatives */}
          {section.isNegotiable && (
            <>
              {/* View mode - just show current content */}
              {!negotiationMode && (
                <Typography variant="body1">{section.content}</Typography>
              )}
              
              {/* Negotiation mode - show alternatives with selection */}
              {negotiationMode && (
                <Box>
                  <RadioGroup
                    value={selectedOption || ''}
                    onChange={handleAlternativeSelect}
                    aria-label={`${section.title} options`}
                  >
                    {section.alternatives.map((alternative) => {
                      const selectable = isAlternativeSelectable(alternative);
                      const isSelected = selectedOption === alternative.id;
                      
                      return (
                        <Box key={alternative.id} mb={2}>
                          <AlternativeOption 
                            isSelected={isSelected}
                            isSelectable={selectable}
                          >
                            <FormControlLabel
                              value={alternative.id}
                              control={
                                <Radio 
                                  color="primary" 
                                  disabled={!selectable && !isSelected}
                                />
                              }
                              label={
                                <Box>
                                  <Box display="flex" justifyContent="space-between" alignItems="center">
                                    <Typography variant="subtitle1" fontWeight="medium">
                                      {alternative.title}
                                      {alternative.isDefault && (
                                        <Typography component="span" variant="caption" color="text.secondary" ml={1}>
                                          (Default)
                                        </Typography>
                                      )}
                                    </Typography>
                                    <Tooltip content={
                                      alternative.points === 0 
                                        ? "Standard option (no points required)" 
                                        : `Requires ${alternative.points} points from your point budget`
                                    }>
                                      <Badge 
                                        content={`${alternative.points} ${alternative.points === 1 ? 'point' : 'points'}`} 
                                        variant={alternative.points === 0 ? "neutral" : "primary"} 
                                        size="small" 
                                      />
                                    </Tooltip>
                                  </Box>
                                  <Typography variant="body2" mt={1}>
                                    {alternative.content}
                                  </Typography>
                                  {!selectable && !isSelected && lawFirmView && (
                                    <Typography color="error" variant="caption" mt={1} display="block">
                                      Not enough points available to select this option
                                    </Typography>
                                  )}
                                </Box>
                              }
                              sx={{ width: '100%', margin: 0, alignItems: 'flex-start' }}
                              disabled={!selectable && !isSelected}
                            />
                          </AlternativeOption>
                        </Box>
                      );
                    })}
                  </RadioGroup>
                </Box>
              )}
            </>
          )}
        </SectionContent>
      </Collapse>
    </Card>
  );
};

export default OCGSectionView;