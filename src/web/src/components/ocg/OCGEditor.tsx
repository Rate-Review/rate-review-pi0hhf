import React, {
  useState,
  useEffect,
  useMemo,
  useCallback,
} from 'react'; //  ^18.2.0
import {
  DragDropContext,
  Droppable,
  Draggable,
} from 'react-beautiful-dnd'; //  ^13.1.1
import { v4 as uuidv4 } from 'uuid'; //  ^9.0.0
import {
  OCG,
  OCGSection,
} from '../../../types/ocg';
import OCGSectionEditor from './OCGSectionEditor';
import OCGPointBudget from './OCGPointBudget';
import Button from '../common/Button';
import Card from '../common/Card';
import TextField from '../common/TextField';
import RecommendationCard from '../ai/RecommendationCard';
import { useOCG } from '../../hooks/useOCG';

/**
 * @interface OCGEditorProps
 * @description Props interface for the OCGEditor component
 */
interface OCGEditorProps {
  ocgId?: string;
  initialData?: OCG;
  isLoading?: boolean;
  isReadOnly?: boolean;
  onSaveDraft?: (ocg: OCG) => void;
  onPublish?: (ocgId: string) => void;
  onCancel?: () => void;
}

/**
 * @component OCGEditor
 * @description Component for creating and editing Outside Counsel Guidelines (OCGs)
 */
export const OCGEditor: React.FC<OCGEditorProps> = (props) => {
  // LD1: Extract props such as ocgId, initialData, isLoading, isReadOnly, and callback functions
  const {
    ocgId,
    initialData,
    isLoading,
    isReadOnly,
    onSaveDraft,
    onPublish,
    onCancel,
  } = props;

  // LD1: Initialize state for the OCG data, active section, validation errors, and dirty state
  const [ocg, setOcg] = useState<OCG | null>(null);
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState({});
  const [isDirty, setIsDirty] = useState(false);

  // LD1: Handle initializing OCG data from props when available
  useEffect(() => {
    if (initialData) {
      setOcg(initialData);
    }
  }, [initialData]);

  // LD1: Implement handlers for title changes, section management, and point budget changes
  const handleTitleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (ocg) {
      setOcg({ ...ocg, title: event.target.value });
      setIsDirty(true);
    }
  };

  const handleAddSection = () => {
    if (ocg) {
      const newSection: OCGSection = {
        id: uuidv4(),
        title: 'New Section',
        content: 'Enter content here',
        isNegotiable: false,
        alternatives: [],
        order: ocg.sections.length,
      };
      setOcg({ ...ocg, sections: [...ocg.sections, newSection] });
      setIsDirty(true);
    }
  };

  const handleSectionChange = (updatedSection: OCGSection) => {
    if (ocg) {
      const updatedSections = ocg.sections.map((section) =>
        section.id === updatedSection.id ? updatedSection : section
      );
      setOcg({ ...ocg, sections: updatedSections });
      setIsDirty(true);
    }
  };

  const handleSectionDelete = (sectionId: string) => {
    if (ocg) {
      const updatedSections = ocg.sections.filter(
        (section) => section.id !== sectionId
      );
      setOcg({ ...ocg, sections: updatedSections });
      setIsDirty(true);
    }
  };

  const handleTotalPointsChange = (value: number) => {
    if (ocg) {
      setOcg({ ...ocg, totalPoints: value });
      setIsDirty(true);
    }
  };

  const handleDefaultPointBudgetChange = (value: number) => {
    if (ocg) {
      setOcg({ ...ocg, defaultFirmPointBudget: value });
      setIsDirty(true);
    }
  };

  // LD1: Implement validation logic for OCG data
  const validateOCG = (): boolean => {
    // TODO: Implement validation logic
    return true;
  };

  // LD1: Implement save draft, preview, and publish handlers
  const handleSaveDraft = () => {
    if (ocg && onSaveDraft) {
      onSaveDraft(ocg);
      setIsDirty(false);
    }
  };

  const handlePublish = () => {
    if (ocg && ocg.id && onPublish) {
      onPublish(ocg.id);
    }
  };

  // LD1: Set up effect to prompt users before leaving with unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      if (isDirty) {
        event.preventDefault();
        event.returnValue = '';
        return '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isDirty]);

  // LD1: Calculate total points used across all sections
  const totalPointsUsed = useMemo(() => {
    // TODO: Implement total points calculation
    return 0;
  }, [ocg]);

  // LD1: Render the OCG editor UI with title and metadata fields
  return (
    <div>
      <Card>
        {/* Title and metadata */}
        <TextField
          label="Title"
          value={ocg?.title || ''}
          onChange={handleTitleChange}
          fullWidth
          disabled={isReadOnly}
        />
      </Card>

      {/* Draggable section list */}
      {ocg?.sections && (
        <div>
          {ocg.sections.map((section, index) => (
            <OCGSectionEditor
              key={section.id}
              section={section}
              onChange={handleSectionChange}
              onDelete={handleSectionDelete}
              readOnly={isReadOnly}
            />
          ))}
          {!isReadOnly && (
            <Button onClick={handleAddSection}>Add Section</Button>
          )}
        </div>
      )}

      {/* Point budget configuration */}
      {ocg && (
        <OCGPointBudget
          totalPoints={ocg.totalPoints}
          pointsUsed={totalPointsUsed}
          editable={!isReadOnly}
          onTotalPointsChange={handleTotalPointsChange}
          firmPointBudget={ocg.defaultFirmPointBudget}
          onFirmPointBudgetChange={handleDefaultPointBudgetChange}
        />
      )}

      {/* AI recommendations */}
      <RecommendationCard
        recommendation={{
          id: '1',
          type: 'APPROVE',
          value: null,
          rationale: 'This is a sample recommendation',
          confidence: 0.8,
        }}
        onApply={() => {}}
        onDismiss={() => {}}
        onViewExplanation={() => {}}
      />

      {/* Action buttons */}
      {!isReadOnly && (
        <div>
          <Button onClick={handleSaveDraft} disabled={!isDirty}>
            Save Draft
          </Button>
          <Button onClick={handlePublish} disabled={!validateOCG()}>
            Publish
          </Button>
          <Button onClick={onCancel}>Cancel</Button>
        </div>
      )}
    </div>
  );
};