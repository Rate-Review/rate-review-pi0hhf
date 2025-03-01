import React, { useState, useEffect, useMemo, useCallback } from 'react'; //  ^18.0.0
import styled from 'styled-components'; //  ^5.3.6
import {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
} from '../common/Card';
import Button from '../common/Button';
import Select from '../common/Select';
import TextField from '../common/TextField';
import Alert from '../common/Alert';
import Spinner from '../common/Spinner';
import Checkbox from '../common/Checkbox';
import {
  DragDropContext,
  Droppable,
  Draggable,
  DropResult,
} from 'react-beautiful-dnd'; //  ^13.1.1
import {
  Add,
  Delete,
  DragIndicator,
  ArrowForward,
} from '@mui/icons-material'; //  ^5.14.0
import { v4 as uuidv4 } from 'uuid'; //  ^9.0.0
import { toast } from 'react-toastify'; //  ^9.1.3
import { useAppDispatch, useAppSelector } from '../../store';
import {
  fetchFieldMappings,
  createFieldMappingConfiguration,
  updateFieldMappingConfiguration,
} from '../../store/integrations/integrationsThunks';
import {
  IntegrationType,
  SyncDirection,
  FieldMapping,
  FieldMappingSet,
} from '../../types/integration';

/**
 * Props for the FieldMappingInterface component
 */
interface FieldMappingInterfaceProps {
  integrationId: string;
  integrationType: IntegrationType;
  mappingSetId?: string;
  initialDirection?: SyncDirection;
  sourceFields: Array<{ label: string; value: string; description?: string }>;
  targetFields: Array<{ label: string; value: string; description?: string }>;
  onSave?: () => void;
  onCancel?: () => void;
  transformFunctions?: Array<{ label: string; value: string; description?: string }>;
  clearOnDirectionChange?: boolean;
}

/**
 * Container for the entire field mapping interface
 */
const MappingContainer = styled.div`
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
`;

/**
 * Header section with title and direction selector
 */
const MappingHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
`;

/**
 * Form for mapping set details
 */
const MappingForm = styled.div`
  margin-bottom: 24px;
`;

/**
 * Container for the list of field mappings
 */
const MappingList = styled.div`
  margin-bottom: 24px;
`;

/**
 * Container for a single field mapping row
 */
const MappingItem = styled.div`
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid #E2E8F0;
  border-radius: 4px;
  margin-bottom: 8px;
  background-color: #FFFFFF;
`;

/**
 * Handle for drag and drop reordering
 */
const DragHandle = styled.div`
  display: flex;
  align-items: center;
  margin-right: 12px;
  cursor: grab;
`;

/**
 * Container for source/target field selectors
 */
const FieldSelector = styled.div`
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
`;

/**
 * Container for the arrow between source and target fields
 */
const ArrowContainer = styled.div`
  display: flex;
  align-items: center;
  margin: 0 12px;
  color: #718096;
`;

/**
 * Container for field options (required, transform)
 */
const FieldOptions = styled.div`
  display: flex;
  align-items: center;
  margin-left: 16px;
  gap: 12px;
`;

/**
 * Button to delete a mapping
 */
const DeleteButton = styled.button`
  background: none;
  border: none;
  color: #E53E3E;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  margin-left: 12px;
  border-radius: 4px;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #FEF2F2;
  }
`;

/**
 * Container for action buttons
 */
const ActionBar = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 24px;
`;

/**
 * Container for the import/export direction selector
 */
const DirectionSelector = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

/**
 * Badge indicating a required field
 */
const RequiredFieldBadge = styled.span`
  background-color: #FEF2F2;
  color: #E53E3E;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
`;

/**
 * Main component that provides an interface for mapping fields between Justice Bid and external systems
 */
const FieldMappingInterface: React.FC<FieldMappingInterfaceProps> = ({
  integrationId,
  integrationType,
  mappingSetId,
  initialDirection = SyncDirection.IMPORT,
  sourceFields,
  targetFields,
  onSave,
  onCancel,
  transformFunctions,
  clearOnDirectionChange = true,
}) => {
  // Initialize state variables for current mapping set, available source/target fields, loading state, and validation errors
  const [currentMappingSet, setCurrentMappingSet] = useState<FieldMappingSet>({
    id: uuidv4(),
    name: '',
    integrationId: integrationId,
    direction: initialDirection,
    mappings: [],
    isDefault: false,
    createdAt: new Date(),
    updatedAt: new Date(),
  });
  const [availableSourceFields, setAvailableSourceFields] = useState(sourceFields);
  const [availableTargetFields, setAvailableTargetFields] = useState(targetFields);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Use Redux hooks to fetch existing field mappings and dispatch actions
  const dispatch = useAppDispatch();
  const integrations = useAppSelector((state) => state.integrations.integrations);

  // Handle loading existing mapping sets when integration ID changes
  useEffect(() => {
    const loadMappingSet = async () => {
      if (integrationId && mappingSetId) {
        setIsLoading(true);
        try {
          const integration = integrations.find((i) => i.id === integrationId);
          if (integration && (integration as any).mappings) {
            const existingMappingSet = (integration as any).mappings.find((ms: FieldMappingSet) => ms.id === mappingSetId);
            if (existingMappingSet) {
              setCurrentMappingSet(existingMappingSet);
              setAvailableSourceFields(sourceFields);
              setAvailableTargetFields(targetFields);
            }
          } else {
            await dispatch(fetchFieldMappings(integrationId));
          }
        } catch (error: any) {
          toast.error(`Error loading mapping set: ${error.message}`);
        } finally {
          setIsLoading(false);
        }
      } else {
        setCurrentMappingSet({
          id: uuidv4(),
          name: '',
          integrationId: integrationId,
          direction: initialDirection,
          mappings: [],
          isDefault: false,
          createdAt: new Date(),
          updatedAt: new Date(),
        });
        setAvailableSourceFields(sourceFields);
        setAvailableTargetFields(targetFields);
      }
    };

    loadMappingSet();
  }, [integrationId, mappingSetId, dispatch, integrations, sourceFields, targetFields, initialDirection]);

  /**
   * Adds a new field mapping to the current mapping set
   */
  const handleAddMapping = useCallback(() => {
    const newMapping: FieldMapping = {
      id: uuidv4(),
      sourceField: '',
      targetField: '',
      transformFunction: null,
      required: false,
      description: null,
    };

    setCurrentMappingSet((prev) => ({
      ...prev,
      mappings: [...prev.mappings, newMapping],
    }));
  }, []);

  /**
   * Updates an existing field mapping
   * @param mappingId - The ID of the mapping to update
   * @param updatedValues - The new values for the mapping
   */
  const handleUpdateMapping = useCallback((mappingId: string, updatedValues: Partial<FieldMapping>) => {
    setCurrentMappingSet((prev) => ({
      ...prev,
      mappings: prev.mappings.map((mapping) =>
        mapping.id === mappingId ? { ...mapping, ...updatedValues } : mapping
      ),
    }));
  }, []);

  /**
   * Removes a field mapping from the current mapping set
   * @param mappingId - The ID of the mapping to remove
   */
  const handleDeleteMapping = useCallback((mappingId: string) => {
    setCurrentMappingSet((prev) => ({
      ...prev,
      mappings: prev.mappings.filter((mapping) => mapping.id !== mappingId),
    }));
  }, []);

  /**
   * Reorders mappings using drag and drop functionality
   * @param result - The result of the drag and drop operation
   */
  const handleReorderMappings = useCallback((result: DropResult) => {
    if (!result.destination) {
      return;
    }

    const startIndex = result.source.index;
    const endIndex = result.destination.index;

    const reorderedMappings = Array.from(currentMappingSet.mappings);
    const [removed] = reorderedMappings.splice(startIndex, 1);
    reorderedMappings.splice(endIndex, 0, removed);

    setCurrentMappingSet((prev) => ({
      ...prev,
      mappings: reorderedMappings,
    }));
  }, [currentMappingSet.mappings]);

  /**
   * Saves the current mapping set to the backend
   */
  const handleSaveMappingSet = useCallback(async () => {
    if (!validateMappingSet()) {
      return;
    }

    setIsLoading(true);
    try {
      if (mappingSetId) {
        await dispatch(
          updateFieldMappingConfiguration({
            integrationId,
            mappingSetId,
            updatedMappingSet: currentMappingSet,
          })
        );
        toast.success('Mapping set updated successfully!');
      } else {
        await dispatch(
          createFieldMappingConfiguration({
            integrationId,
            mappingSet: currentMappingSet,
          })
        );
        toast.success('Mapping set created successfully!');
      }

      if (onSave) {
        onSave();
      }
    } catch (error: any) {
      toast.error(`Error saving mapping set: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [currentMappingSet, dispatch, integrationId, mappingSetId, onSave]);

  /**
   * Validates the mapping set before saving
   */
  const validateMappingSet = useCallback(() => {
    const newErrors: Record<string, string> = {};

    if (!currentMappingSet.name) {
      newErrors.name = 'Mapping set name is required';
    }

    if (currentMappingSet.mappings.length === 0) {
      newErrors.mappings = 'At least one mapping is required';
    }

    currentMappingSet.mappings.forEach((mapping, index) => {
      if (!mapping.sourceField || !mapping.targetField) {
        newErrors[`mapping-${index}`] = 'Both source and target fields are required';
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [currentMappingSet]);

  /**
   * Handles changing the mapping direction (import/export)
   * @param newDirection - The new direction to set
   */
  const handleDirectionChange = useCallback((newDirection: SyncDirection) => {
    setCurrentMappingSet((prev) => ({
      ...prev,
      direction: newDirection,
    }));

    setAvailableSourceFields(sourceFields);
    setAvailableTargetFields(targetFields);

    if (clearOnDirectionChange) {
      setCurrentMappingSet((prev) => ({
        ...prev,
        direction: newDirection,
        mappings: [],
      }));
    }
  }, [clearOnDirectionChange, sourceFields, targetFields]);

  /**
   * Updates the mapping set name
   * @param name - The new name to set
   */
  const handleNameChange = useCallback((name: string) => {
    setCurrentMappingSet((prev) => ({
      ...prev,
      name: name,
    }));
    setErrors((prev) => ({ ...prev, name: '' }));
  }, []);

  /**
   * Toggles the default status of the mapping set
   * @param isDefault - Whether the mapping set should be default
   */
  const handleDefaultChange = useCallback((isDefault: boolean) => {
    setCurrentMappingSet((prev) => ({
      ...prev,
      isDefault: isDefault,
    }));
  }, []);

  return (
    <MappingContainer>
      <Card>
        <CardHeader
          title="Field Mapping"
          action={
            <DirectionSelector>
              <span>Direction:</span>
              <Select
                name="direction"
                value={currentMappingSet.direction}
                onChange={(value) => handleDirectionChange(value as SyncDirection)}
                options={[
                  { label: 'Import', value: SyncDirection.IMPORT },
                  { label: 'Export', value: SyncDirection.EXPORT },
                ]}
              />
            </DirectionSelector>
          }
        />
        <CardContent>
          <MappingForm>
            <TextField
              label="Mapping Set Name"
              value={currentMappingSet.name}
              onChange={(e) => handleNameChange(e.target.value)}
              error={errors.name}
            />
            <Checkbox
              label="Is Default Mapping"
              checked={currentMappingSet.isDefault}
              onChange={handleDefaultChange}
            />
          </MappingForm>

          <MappingList>
            <DragDropContext onDragEnd={handleReorderMappings}>
              <Droppable droppableId="mappings">
                {(provided) => (
                  <div {...provided.droppableProps} ref={provided.innerRef}>
                    {currentMappingSet.mappings.map((mapping, index) => (
                      <Draggable key={mapping.id} draggableId={mapping.id} index={index}>
                        {(provided) => (
                          <MappingItem
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                          >
                            <DragHandle>
                              <DragIndicator />
                            </DragHandle>
                            <FieldSelector>
                              <Select
                                name={`sourceField-${index}`}
                                label="Source Field"
                                value={mapping.sourceField}
                                options={availableSourceFields}
                                onChange={(value) => handleUpdateMapping(mapping.id, { sourceField: value as string })}
                              />
                              <ArrowContainer>
                                <ArrowForward />
                              </ArrowContainer>
                              <Select
                                name={`targetField-${index}`}
                                label="Target Field"
                                value={mapping.targetField}
                                options={availableTargetFields}
                                onChange={(value) => handleUpdateMapping(mapping.id, { targetField: value as string })}
                              />
                            </FieldSelector>
                            <FieldOptions>
                              <Checkbox
                                label="Required"
                                checked={mapping.required}
                                onChange={(checked) => handleUpdateMapping(mapping.id, { required: checked })}
                              />
                              <DeleteButton onClick={() => handleDeleteMapping(mapping.id)}>
                                <Delete />
                              </DeleteButton>
                            </FieldOptions>
                          </MappingItem>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </DragDropContext>
            {errors.mappings && <Alert severity="error" message={errors.mappings} />}
          </MappingList>

          <Button variant="text" onClick={handleAddMapping}>
            <Add />
            Add Mapping
          </Button>
        </CardContent>
        <CardFooter>
          <Button onClick={onCancel}>Cancel</Button>
          <Button variant="primary" onClick={handleSaveMappingSet} disabled={isLoading}>
            {isLoading ? <Spinner size="16px" /> : 'Save'}
          </Button>
        </CardFooter>
      </Card>
    </MappingContainer>
  );
};

export default FieldMappingInterface;