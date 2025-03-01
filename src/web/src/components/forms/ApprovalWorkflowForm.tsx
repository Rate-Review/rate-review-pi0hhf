import React, { useState, useEffect, useCallback } from 'react'; //  ^18.0.0
import styled from 'styled-components'; //  ^5.3.10
import { v4 as uuidv4 } from 'uuid'; //  ^8.3.2

import Button from '../common/Button';
import TextField from '../common/TextField';
import Select from '../common/Select';
import Checkbox from '../common/Checkbox';
import useOrganizations from '../../hooks/useOrganizations';
import { OrganizationType, WorkflowType } from '../../types/organization';
import { ApprovalStatus } from '../../types/negotiation';

/**
 * Interface for approval workflow step data
 */
interface ApprovalStep {
  id: string;
  order: number;
  approverUserId: string | null;
  approverRole: string | null;
  isRequired: boolean;
  timeoutHours: number | null;
}

/**
 * Interface for approval workflow data
 */
interface ApprovalWorkflow {
  id: string;
  name: string;
  description: string;
  type: WorkflowType;
  isActive: boolean;
  criteria: object;
  applicableEntities: object;
  steps: ApprovalStep[];
}

/**
 * Interface for ApprovalWorkflowForm props
 */
interface ApprovalWorkflowFormProps {
  onSubmit: (workflow: ApprovalWorkflow) => void;
  onCancel: () => void;
  initialWorkflowId?: string | null;
  defaultType?: WorkflowType | null;
  isEdit?: boolean;
}

/**
 * Form component for creating and editing approval workflows
 */
const ApprovalWorkflowForm: React.FC<ApprovalWorkflowFormProps> = ({
  onSubmit,
  onCancel,
  initialWorkflowId,
  defaultType,
  isEdit = false,
}) => {
  // Access organization data and functions
  const { currentOrganization } = useOrganizations();

  // Initialize state for workflow data
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [type, setType] = useState<WorkflowType>(defaultType || OrganizationType.Client);
  const [isActive, setIsActive] = useState(true);
  const [steps, setSteps] = useState<ApprovalStep[]>([]);

  // Load existing workflow data if in edit mode
  useEffect(() => {
    if (isEdit && initialWorkflowId && currentOrganization?.settings?.approvalWorkflow) {
      // TODO: Fetch workflow from API or Redux store
      // For now, mock data
      const mockWorkflow: ApprovalWorkflow = {
        id: initialWorkflowId,
        name: 'Example Workflow',
        description: 'This is an example approval workflow',
        type: OrganizationType.Client,
        isActive: true,
        criteria: {},
        applicableEntities: {},
        steps: [
          { id: uuidv4(), order: 1, approverUserId: null, approverRole: 'Legal Counsel', isRequired: true, timeoutHours: 24 },
          { id: uuidv4(), order: 2, approverUserId: null, approverRole: 'Finance Manager', isRequired: false, timeoutHours: 48 },
        ],
      };

      setName(mockWorkflow.name);
      setDescription(mockWorkflow.description);
      setType(mockWorkflow.type);
      setIsActive(mockWorkflow.isActive);
      setSteps(mockWorkflow.steps);
    }
  }, [isEdit, initialWorkflowId, currentOrganization]);

  /**
   * Handles form submission to create or update an approval workflow
   */
  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    // Validate form data (name, at least one step, etc.)
    if (!name || steps.length === 0) {
      alert('Please enter a workflow name and add at least one approval step.');
      return;
    }

    // Format the workflow data into the required structure
    const workflowData: ApprovalWorkflow = {
      id: initialWorkflowId || uuidv4(),
      name,
      description,
      type,
      isActive,
      criteria: {},
      applicableEntities: {},
      steps: steps.map((step, index) => ({ ...step, order: index + 1 })),
    };

    // Call the onSubmit callback with the updated workflow data
    onSubmit(workflowData);

    // Show success message or handle errors
    alert(`Workflow "${name}" ${isEdit ? 'updated' : 'created'} successfully!`);

    // Reset form if needed or navigate away
    onCancel();
  };

  /**
   * Adds a new approval step to the workflow
   */
  const addStep = () => {
    const newStepId = uuidv4();
    const newStep: ApprovalStep = {
      id: newStepId,
      order: steps.length + 1,
      approverUserId: null,
      approverRole: null,
      isRequired: true,
      timeoutHours: null,
    };
    setSteps([...steps, newStep]);
  };

  /**
   * Removes an approval step from the workflow
   */
  const removeStep = (stepId: string) => {
    const updatedSteps = steps.filter(step => step.id !== stepId);
    setSteps(updatedSteps);
  };

  /**
   * Changes the order of an approval step
   */
  const moveStep = (stepId: string, direction: 'up' | 'down') => {
    const currentIndex = steps.findIndex(step => step.id === stepId);
    const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;

    if (newIndex < 0 || newIndex >= steps.length) {
      return; // Prevent moving out of bounds
    }

    const updatedSteps = [...steps];
    const [movedStep] = updatedSteps.splice(currentIndex, 1);
    updatedSteps.splice(newIndex, 0, movedStep);

    setSteps(updatedSteps);
  };

  /**
   * Updates a field value for a specific step
   */
  const updateStepField = (stepId: string, field: string, value: any) => {
    const updatedSteps = steps.map(step => {
      if (step.id === stepId) {
        return { ...step, [field]: value };
      }
      return step;
    });
    setSteps(updatedSteps);
  };

  return (
    <FormContainer onSubmit={handleSubmit}>
      <Section>
        <SectionTitle>{isEdit ? 'Edit Approval Workflow' : 'Create Approval Workflow'}</SectionTitle>
        <FormRow>
          <FormColumn>
            <TextField
              label="Workflow Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </FormColumn>
          <FormColumn>
            <TextField
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </FormColumn>
        </FormRow>
        <FormRow>
          <FormColumn>
            <Select
              label="Workflow Type"
              value={type}
              onChange={(value) => setType(value as WorkflowType)}
              options={[
                { value: OrganizationType.Client, label: 'Client' },
                { value: OrganizationType.LawFirm, label: 'Law Firm' },
              ]}
              required
            />
          </FormColumn>
          <FormColumn>
            <Checkbox
              label="Active"
              checked={isActive}
              onChange={(checked) => setIsActive(checked)}
            />
          </FormColumn>
        </FormRow>
      </Section>

      <Section>
        <SectionTitle>Steps Configuration</SectionTitle>
        {steps.map((step, index) => (
          <StepContainer key={step.id}>
            <StepHeader>
              <StepTitle>Step {index + 1}</StepTitle>
              <StepActions>
                <Button size="small" variant="text" onClick={() => moveStep(step.id, 'up')} disabled={index === 0}>
                  Up
                </Button>
                <Button size="small" variant="text" onClick={() => moveStep(step.id, 'down')} disabled={index === steps.length - 1}>
                  Down
                </Button>
                <Button size="small" variant="text" color="error" onClick={() => removeStep(step.id)}>
                  Remove
                </Button>
              </StepActions>
            </StepHeader>
            <FormRow>
              <FormColumn>
                <TextField
                  label="Approver User ID"
                  value={step.approverUserId || ''}
                  onChange={(e) => updateStepField(step.id, 'approverUserId', e.target.value)}
                />
              </FormColumn>
              <FormColumn>
                <TextField
                  label="Approver Role"
                  value={step.approverRole || ''}
                  onChange={(e) => updateStepField(step.id, 'approverRole', e.target.value)}
                />
              </FormColumn>
            </FormRow>
            <FormRow>
              <FormColumn>
                <Checkbox
                  label="Required"
                  checked={step.isRequired}
                  onChange={(checked) => updateStepField(step.id, 'isRequired', checked)}
                />
              </FormColumn>
              <FormColumn>
                <TextField
                  label="Timeout (Hours)"
                  type="number"
                  value={step.timeoutHours || ''}
                  onChange={(e) => updateStepField(step.id, 'timeoutHours', parseInt(e.target.value))}
                />
              </FormColumn>
            </FormRow>
          </StepContainer>
        ))}
        <AddStepButton>
          <Button variant="secondary" onClick={addStep}>Add Step</Button>
        </AddStepButton>
      </Section>

      <Section>
        <SectionTitle>Applicable Entities</SectionTitle>
        <EntitySelectionContainer>
          {/* TODO: Implement entity selection (firms, peer groups, etc.) */}
          <div>Select which entities this workflow applies to (firms, peer groups, etc.).</div>
        </EntitySelectionContainer>
      </Section>

      <ButtonContainer>
        <Button type="submit">{isEdit ? 'Update Workflow' : 'Create Workflow'}</Button>
        <Button variant="outline" onClick={onCancel}>Cancel</Button>
      </ButtonContainer>
    </FormContainer>
  );
};

export default ApprovalWorkflowForm;

const FormContainer = styled.form`
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
`;

const Section = styled.div`
  margin-bottom: 24px;
`;

const SectionTitle = styled.h3`
  font-size: 18px;
  margin-bottom: 16px;
  color: ${props => props.theme.colors.primary.dark};
`;

const StepContainer = styled.div`
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  position: relative;
`;

const StepHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
`;

const StepTitle = styled.h4`
  font-size: 16px;
  margin: 0;
`;

const StepActions = styled.div`
  display: flex;
  gap: 8px;
`;

const FormRow = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
`;

const FormColumn = styled.div`
  flex: 1;
  min-width: 250px;
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
`;

const AddStepButton = styled.div`
  margin-top: 8px;
  margin-bottom: 24px;
`;

const EntitySelectionContainer = styled.div`
  margin-top: 24px;
  border-top: 1px solid #E2E8F0;
  padding-top: 24px;
`;