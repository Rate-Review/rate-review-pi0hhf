import { useState, useCallback, useEffect, useRef } from 'react'; // React 18.0.0+

// Type definitions
type FormValues = Record<string, any>;
type FormErrors<Values> = Partial<Record<keyof Values, string>>;
type FormTouched<Values> = Partial<Record<keyof Values, boolean>>;

/**
 * Interface for form validation schema
 */
interface ValidationSchema<Values extends FormValues> {
  validate: (values: Values) => Promise<FormErrors<Values>> | FormErrors<Values>;
}

/**
 * Configuration options for the useForm hook
 */
interface FormOptions<Values extends FormValues> {
  initialValues: Values;
  validationSchema?: ValidationSchema<Values>;
  onSubmit: (values: Values, formHelpers: FormHelpers<Values>) => void | Promise<void>;
  validateOnMount?: boolean;
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
}

/**
 * Helper functions provided to onSubmit callback
 */
interface FormHelpers<Values extends FormValues> {
  setSubmitting: (isSubmitting: boolean) => void;
  setErrors: (errors: FormErrors<Values>) => void;
  resetForm: () => void;
}

/**
 * Return type for the useForm hook
 */
interface UseFormReturn<Values extends FormValues> {
  // Form state
  values: Values;
  errors: FormErrors<Values>;
  touched: FormTouched<Values>;
  isSubmitting: boolean;
  isValid: boolean;
  isDirty: boolean;
  
  // Event handlers
  handleChange: (e: React.ChangeEvent<any>) => void;
  handleBlur: (e: React.FocusEvent<any>) => void;
  handleSubmit: (e?: React.FormEvent<HTMLFormElement>) => Promise<void>;
  
  // Field and form manipulation
  setFieldValue: (field: keyof Values, value: any, shouldValidate?: boolean) => void;
  setFieldError: (field: keyof Values, error: string) => void;
  setValues: (values: Partial<Values>, shouldValidate?: boolean) => void;
  resetForm: () => void;
  
  // Validation
  validateField: (field: keyof Values) => Promise<string | undefined>;
  validateForm: () => Promise<FormErrors<Values>>;
}

/**
 * Performs a deep equality check between two values
 */
function isEqual(a: any, b: any): boolean {
  if (a === b) return true;
  
  if (
    typeof a !== 'object' ||
    typeof b !== 'object' ||
    a === null ||
    b === null
  ) {
    return a === b;
  }
  
  const keysA = Object.keys(a);
  const keysB = Object.keys(b);
  
  if (keysA.length !== keysB.length) return false;
  
  for (const key of keysA) {
    if (!keysB.includes(key)) return false;
    if (!isEqual(a[key], b[key])) return false;
  }
  
  return true;
}

/**
 * A custom React hook for managing form state, validation, and submission across the Justice Bid application.
 * Provides comprehensive form handling for rate submissions, negotiation interfaces, OCG management,
 * and integration configurations.
 * 
 * @param options - Configuration object containing initialValues, validationSchema, onSubmit, and validation behavior options
 * @returns Object containing form state and actions for managing the form
 */
function useForm<Values extends FormValues>({
  initialValues,
  validationSchema,
  onSubmit,
  validateOnMount = false,
  validateOnChange = true,
  validateOnBlur = true,
}: FormOptions<Values>): UseFormReturn<Values> {
  // Form state
  const [values, setValues] = useState<Values>(initialValues);
  const [errors, setErrors] = useState<FormErrors<Values>>({});
  const [touched, setTouched] = useState<FormTouched<Values>>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  
  // Use refs to keep track of latest values for validation and callbacks
  const valuesRef = useRef<Values>(values);
  const validationSchemaRef = useRef(validationSchema);
  const initialValuesRef = useRef<Values>(initialValues);
  
  // Update refs when dependencies change
  useEffect(() => {
    valuesRef.current = values;
  }, [values]);
  
  useEffect(() => {
    validationSchemaRef.current = validationSchema;
  }, [validationSchema]);
  
  useEffect(() => {
    initialValuesRef.current = initialValues;
  }, [initialValues]);
  
  /**
   * Validates a single field and updates the errors state
   */
  const validateField = useCallback(async (field: keyof Values): Promise<string | undefined> => {
    if (!validationSchemaRef.current) return undefined;
    
    try {
      const validationErrors = await validationSchemaRef.current.validate(valuesRef.current);
      
      // Update errors state but only for the specified field
      setErrors(prev => ({
        ...prev,
        [field]: validationErrors[field]
      }));
      
      return validationErrors[field];
    } catch (error) {
      console.error(`Field validation error for ${String(field)}:`, error);
      return undefined;
    }
  }, []);
  
  /**
   * Validates the entire form and updates the errors state
   */
  const validateForm = useCallback(async (): Promise<FormErrors<Values>> => {
    if (!validationSchemaRef.current) return {};
    
    try {
      const validationErrors = await validationSchemaRef.current.validate(valuesRef.current);
      setErrors(validationErrors);
      return validationErrors;
    } catch (error) {
      console.error('Form validation error:', error);
      return {};
    }
  }, []);
  
  /**
   * Handles input change events and updates form values
   */
  const handleChange = useCallback((e: React.ChangeEvent<any>) => {
    const { name, value, type, checked } = e.target;
    const fieldValue = type === 'checkbox' ? checked : value;
    
    setValues(prev => ({
      ...prev,
      [name]: fieldValue
    }));
    
    if (validateOnChange && validationSchemaRef.current) {
      validateField(name as keyof Values);
    }
  }, [validateOnChange, validateField]);
  
  /**
   * Handles input blur events and marks fields as touched
   */
  const handleBlur = useCallback((e: React.FocusEvent<any>) => {
    const { name } = e.target;
    
    setTouched(prev => ({
      ...prev,
      [name]: true
    }));
    
    if (validateOnBlur && validationSchemaRef.current) {
      validateField(name as keyof Values);
    }
  }, [validateOnBlur, validateField]);
  
  /**
   * Sets a field value programmatically with optional validation
   */
  const setFieldValue = useCallback((field: keyof Values, value: any, shouldValidate = validateOnChange): void => {
    setValues(prev => ({
      ...prev,
      [field]: value
    }));
    
    if (shouldValidate && validationSchemaRef.current) {
      validateField(field);
    }
  }, [validateOnChange, validateField]);
  
  /**
   * Sets a field error message manually
   */
  const setFieldError = useCallback((field: keyof Values, error: string): void => {
    setErrors(prev => ({
      ...prev,
      [field]: error
    }));
  }, []);
  
  /**
   * Updates multiple form values at once with optional validation
   */
  const setFormValues = useCallback((newValues: Partial<Values>, shouldValidate = validateOnChange): void => {
    setValues(prev => ({
      ...prev,
      ...newValues
    }));
    
    if (shouldValidate && validationSchemaRef.current) {
      validateForm();
    }
  }, [validateOnChange, validateForm]);
  
  /**
   * Resets the form to its initial state
   */
  const resetForm = useCallback((): void => {
    setValues(initialValuesRef.current);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, []);
  
  /**
   * Handles form submission with validation and error handling
   */
  const handleSubmit = useCallback(async (e?: React.FormEvent<HTMLFormElement>): Promise<void> => {
    if (e) {
      e.preventDefault();
    }
    
    // Mark all fields as touched on submission
    const allTouched = Object.keys(valuesRef.current).reduce(
      (touched, key) => ({ ...touched, [key]: true }),
      {} as FormTouched<Values>
    );
    setTouched(allTouched);
    
    setIsSubmitting(true);
    
    let validationErrors = {};
    if (validationSchemaRef.current) {
      validationErrors = await validateForm();
    }
    
    const hasErrors = Object.keys(validationErrors).length > 0;
    
    if (!hasErrors) {
      try {
        await onSubmit(valuesRef.current, {
          setSubmitting: setIsSubmitting,
          setErrors,
          resetForm
        });
      } catch (error) {
        console.error('Form submission error:', error);
      }
    }
    
    setIsSubmitting(false);
  }, [onSubmit, validateForm, resetForm]);
  
  // Compute derived state
  const isValid = Object.keys(errors).length === 0;
  const isDirty = !isEqual(values, initialValues);
  
  // Validate form on mount if enabled
  useEffect(() => {
    if (validateOnMount && validationSchemaRef.current) {
      validateForm();
    }
  }, [validateOnMount, validateForm]);
  
  return {
    // Form state
    values,
    errors,
    touched,
    isSubmitting,
    isValid,
    isDirty,
    
    // Event handlers
    handleChange,
    handleBlur,
    handleSubmit,
    
    // Field and form manipulation
    setFieldValue,
    setFieldError,
    setValues: setFormValues,
    resetForm,
    
    // Validation
    validateField,
    validateForm
  };
}

export default useForm;
export type { FormOptions, UseFormReturn, ValidationSchema };