import React, { useState, useEffect, useCallback, FormEvent, ChangeEvent, KeyboardEvent } from 'react'; //  ^18.0.0
import styled from 'styled-components'; //  ^5.3.10
import TextField from '../common/TextField';
import Button from '../common/Button';
import Select from '../common/Select';
import Checkbox from '../common/Checkbox';
import DatePicker from '../common/DatePicker';
import useForm from '../../hooks/useForm';
import useDebounce from '../../hooks/useDebounce';
import useWindowSize from '../../hooks/useWindowSize';

/**
 * Interface for filter option used in select and radio components
 */
interface FilterOption {
  label: string;
  value: string | number | boolean;
}

/**
 * Interface for configuring filter controls in the search form
 */
interface FilterConfig {
  name: string;
  label: string;
  type: 'select' | 'checkbox' | 'radio' | 'date';
  options?: FilterOption[];
  defaultValue?: string | number | boolean;
  isAdvanced?: boolean;
}

/**
 * Interface defining the props for the SearchForm component
 */
interface SearchFormProps {
  onSearch: (formValues: Record<string, any>) => void;
  placeholder?: string;
  initialValues?: Record<string, any>;
  filters?: FilterConfig[];
  debounceTime?: number;
  showAdvancedToggle?: boolean;
  buttonText?: string;
  immediateSearch?: boolean;
  showReset?: boolean;
  ariaLabel?: string;
}

/**
 * Styled components for the SearchForm
 */
const FormContainer = styled.form`
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
  width: 100%;
  margin-bottom: 1.5rem;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: stretch;
  }
`;

const FilterContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;

  @media (max-width: 768px) {
    margin-top: 1rem;
  }
`;

const SearchContainer = styled.div`
  flex: 1;
  min-width: 250px;
`;

const ButtonContainer = styled.div`
  display: flex;
  gap: 0.5rem;

  @media (max-width: 768px) {
    margin-top: 1rem;
  }
`;

const AdvancedSearchToggle = styled.button`
  background: none;
  border: none;
  color: ${props => props.theme.colors.primary};
  text-decoration: underline;
  cursor: pointer;
  font-size: 0.875rem;
  margin-left: auto;
  padding: 0.5rem;
`;

/**
 * Helper function to render filter controls based on filter configuration
 */
const renderFilterControls = (
  filters: FilterConfig[] | undefined,
  formValues: Record<string, any>,
  handleChange: (e: ChangeEvent<any>) => void
): React.ReactNode[] => {
  if (!filters || filters.length === 0) {
    return [];
  }

  return filters.map((filter) => {
    switch (filter.type) {
      case 'select':
        return (
          <Select
            key={filter.name}
            name={filter.name}
            label={filter.label}
            value={formValues[filter.name] || ''}
            onChange={handleChange}
            options={filter.options || []}
            aria-label={filter.label}
          />
        );
      case 'checkbox':
        return (
          <Checkbox
            key={filter.name}
            name={filter.name}
            label={filter.label}
            checked={formValues[filter.name] || false}
            onChange={(checked: boolean) => handleChange({ target: { name: filter.name, value: checked } } as ChangeEvent<HTMLInputElement>)}
            aria-label={filter.label}
          />
        );
      case 'radio':
        // Implement radio button group rendering here
        return null; // Placeholder
      case 'date':
        return (
          <DatePicker
            key={filter.name}
            name={filter.name}
            label={filter.label}
            value={formValues[filter.name] || null}
            onChange={(date: string | null) => handleChange({ target: { name: filter.name, value: date } } as ChangeEvent<HTMLInputElement>)}
            placeholder={filter.placeholder}
            aria-label={filter.label}
          />
        );
      default:
        return null;
    }
  });
};

/**
 * A reusable form component for searching various entities in the system with optional filtering capabilities and responsive design.
 */
const SearchForm: React.FC<SearchFormProps> = ({
  onSearch,
  placeholder = 'Search...',
  initialValues = {},
  filters,
  debounceTime = 300,
  showAdvancedToggle = false,
  buttonText = 'Search',
  immediateSearch = true,
  showReset = false,
  ariaLabel = 'Search form'
}) => {
  // Initialize form state using useForm hook
  const {
    values: formValues,
    handleChange: formHandlersHandleChange,
    handleSubmit: formHandlersHandleSubmit,
    resetForm,
  } = useForm({
    initialValues: { searchTerm: '', ...initialValues },
    onSubmit: onSearch,
  });

  // Setup debounced search value using useDebounce hook
  const searchTerm = formValues.searchTerm || '';
  const debouncedSearchTerm = useDebounce(searchTerm, debounceTime);

  // Get window size using useWindowSize hook for responsive adaptations
  const windowSize = useWindowSize();

  // Initialize state for advanced search visibility
  const [advancedSearch, setAdvancedSearch] = useState(false);

  // Create custom handleSubmit function that wraps formHandlers.handleSubmit
  const handleSubmit = useCallback(
    (e?: React.FormEvent<HTMLFormElement>) => {
      formHandlersHandleSubmit(e);
    },
    [formHandlersHandleSubmit]
  );

  // Create handleKeyDown function to submit form when Enter key is pressed
  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        handleSubmit(e);
      }
    },
    [handleSubmit]
  );

  // Implement useEffect to trigger onSearch when debounced searchTerm changes (if immediateSearch is true)
  useEffect(() => {
    if (immediateSearch) {
      onSearch(formValues);
    }
  }, [debouncedSearchTerm, immediateSearch, onSearch, formValues]);

  // Create toggleAdvancedSearch function to show/hide advanced filters
  const toggleAdvancedSearch = useCallback(() => {
    setAdvancedSearch((prev) => !prev);
  }, []);

  // Filter filters array into basic and advanced filters based on isAdvanced property
  const basicFilters = filters?.filter((filter) => !filter.isAdvanced);
  const advancedFilters = filters?.filter((filter) => filter.isAdvanced);

  // Handle change event
  const handleChange = useCallback((e: ChangeEvent<any>) => {
    formHandlersHandleChange(e);
  }, [formHandlersHandleChange]);

  return (
    <FormContainer onSubmit={handleSubmit} aria-label={ariaLabel}>
      <SearchContainer>
        <TextField
          name="searchTerm"
          placeholder={placeholder}
          value={formValues.searchTerm || ''}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          fullWidth
          aria-label="Search input"
        />
      </SearchContainer>

      <FilterContainer>
        {renderFilterControls(basicFilters, formValues, handleChange)}
      </FilterContainer>

      {showAdvancedToggle && (
        <AdvancedSearchToggle type="button" onClick={toggleAdvancedSearch}>
          {advancedSearch ? 'Hide Advanced Filters' : 'Show Advanced Filters'}
        </AdvancedSearchToggle>
      )}

      {advancedSearch && (
        <FilterContainer>
          {renderFilterControls(advancedFilters, formValues, handleChange)}
        </FilterContainer>
      )}

      <ButtonContainer>
        <Button type="submit">{buttonText}</Button>
        {showReset && <Button type="button" variant="outline" onClick={resetForm}>Reset</Button>}
      </ButtonContainer>
    </FormContainer>
  );
};

export default SearchForm;