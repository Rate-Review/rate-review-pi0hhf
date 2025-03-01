import React, { useState, useEffect, useCallback } from 'react'; //  ^18.2.0
import {
  Grid,
  Paper,
  Typography,
  Divider,
  Box,
  CircularProgress,
} from '@mui/material'; //  ^5.14.0
import { useNavigate, useParams } from 'react-router-dom'; //  ^6.4.0
import { toast } from 'react-toastify'; //  ^9.1.3

import useForm from '../../hooks/useForm'; // Custom hook for form state management and validation
import useAuth from '../../hooks/useAuth'; // Authentication hook to get current organization context
import TextField from '../common/TextField'; // Input field component for text data
import Select from '../common/Select'; // Dropdown selection component
import DatePicker from '../common/DatePicker'; // Date selection component
import Button from '../common/Button'; // Button component for form actions
import {
  createAttorney,
  updateAttorney,
  getAttorney,
} from '../../services/attorneys'; // API service functions for attorney data operations
import {
  getOffices,
  getPracticeAreas,
} from '../../services/organizations'; // API service functions to fetch organization-related reference data
import { getStaffClasses } from '../../services/rates'; // API service function to fetch staff classes
import {
  AttorneyFormData,
  Attorney,
} from '../../types/attorney';

/**
 * Props interface for the AttorneyForm component
 */
interface AttorneyFormProps {
  attorneyId?: string;
  onSuccess: () => void;
  isEditMode?: boolean;
  initialData?: Partial<AttorneyFormData>;
}

/**
 * Validates the attorney form data
 * @param {object} formData - The form data to validate
 * @returns {object} Object with validation errors by field
 */
const validateForm = (formData: AttorneyFormData) => {
  let errors: { [key: string]: string } = {};

  // Validate required fields
  if (!formData.name) {
    errors.name = 'Name is required';
  }
  if (!formData.organizationId) {
    errors.organizationId = 'Organization is required';
  }

  // Validate date logic
  if (formData.barDate && formData.graduationDate) {
    const barDate = new Date(formData.barDate);
    const graduationDate = new Date(formData.graduationDate);
    if (barDate <= graduationDate) {
      errors.barDate = 'Bar Date must be after Graduation Date';
    }
  }

  // Validate email format
  if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = 'Invalid email format';
  }

  return errors;
};

/**
 * Form component for creating and editing attorney profiles
 */
const AttorneyForm: React.FC<AttorneyFormProps> = ({ attorneyId, onSuccess, isEditMode = false, initialData }) => {
  const navigate = useNavigate();
  const { orgId, isOrgType, hasRole } = useAuth();
  const { id } = useParams();
  const [isLoading, setIsLoading] = useState(false);
  const [offices, setOffices] = useState<any[]>([]);
  const [practiceAreas, setPracticeAreas] = useState<any[]>([]);
  const [staffClasses, setStaffClasses] = useState<any[]>([]);

  const {
    values: formData,
    errors,
    touched,
    isLoading: isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldValue,
    setValues: setFormValues,
    resetForm,
  } = useForm<AttorneyFormData>({
    initialValues: {
      name: initialData?.name || '',
      email: initialData?.email || '',
      organizationId: initialData?.organizationId || orgId || '',
      barDate: initialData?.barDate || null,
      graduationDate: initialData?.graduationDate || null,
      promotionDate: initialData?.promotionDate || null,
      officeIds: initialData?.officeIds || [],
      practiceAreas: initialData?.practiceAreas || [],
      staffClassId: initialData?.staffClassId || null,
      unicourtId: initialData?.unicourtId || '',
      timekeeperIds: initialData?.timekeeperIds || {},
    },
    validationSchema: { validate: validateForm },
    onSubmit: async () => {
      setIsLoading(true);
      try {
        const formattedData = {
          ...formData,
          officeIds: formData.officeIds ? formData.officeIds : [],
          practiceAreas: formData.practiceAreas ? formData.practiceAreas : [],
        };

        if (isEditMode && attorneyId) {
          await updateAttorney(attorneyId, formattedData);
          toast.success('Attorney updated successfully!');
        } else {
          await createAttorney(formattedData as CreateAttorneyRequest);
          toast.success('Attorney created successfully!');
          resetForm();
        }
        onSuccess();
      } catch (error: any) {
        toast.error(error?.message || 'An error occurred. Please try again.');
        console.error('Error submitting form:', error);
      } finally {
        setIsLoading(false);
      }
    },
  });

  /**
   * Loads attorney data when in edit mode
   */
  const loadAttorneyData = useCallback(async () => {
    if (isEditMode && attorneyId) {
      setIsLoading(true);
      try {
        const attorneyData = await getAttorney(attorneyId);
        setFormValues({
          name: attorneyData.name,
          email: attorneyData.email,
          organizationId: attorneyData.organizationId,
          barDate: attorneyData.barDate,
          graduationDate: attorneyData.graduationDate,
          promotionDate: attorneyData.promotionDate,
          officeIds: attorneyData.officeIds,
          practiceAreas: attorneyData.practiceAreas,
          staffClassId: attorneyData.staffClassId,
          unicourtId: attorneyData.unicourtId,
          timekeeperIds: attorneyData.timekeeperIds,
        });
      } catch (error: any) {
        toast.error(error?.message || 'Failed to load attorney data.');
        console.error('Error loading attorney data:', error);
      } finally {
        setIsLoading(false);
      }
    }
  }, [attorneyId, isEditMode, setFormValues]);

  /**
   * Loads reference data for dropdowns (offices, practice areas, staff classes)
   */
  const loadReferenceData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [officesData, practiceAreasData, staffClassesData] = await Promise.all([
        getOffices(orgId),
        getPracticeAreas(orgId),
        getStaffClasses(orgId),
      ]);
      setOffices(officesData);
      setPracticeAreas(practiceAreasData);
      setStaffClasses(staffClassesData);
    } catch (error: any) {
      toast.error(error?.message || 'Failed to load reference data.');
      console.error('Error loading reference data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [orgId]);

  useEffect(() => {
    loadReferenceData();
    loadAttorneyData();
  }, [loadReferenceData, loadAttorneyData]);

  return (
    <Box>
      {isLoading ? (
        <Box display="flex" justifyContent="center" alignItems="center" height="200px">
          <CircularProgress />
        </Box>
      ) : (
        <Paper elevation={3} style={{ padding: '20px' }}>
          <Typography variant="h6" gutterBottom>
            {isEditMode ? 'Edit Attorney' : 'Create Attorney'}
          </Typography>
          <Divider style={{ marginBottom: '20px' }} />
          <form onSubmit={handleSubmit}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  name="name"
                  label="Name"
                  value={formData.name}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched.name && errors.name}
                  required
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  name="email"
                  label="Email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched.email && errors.email}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                {isOrgType('Admin') ? (
                  <Select
                    name="organizationId"
                    label="Organization"
                    value={formData.organizationId}
                    onChange={(value) => setFieldValue('organizationId', value)}
                    onBlur={handleBlur}
                    error={touched.organizationId && errors.organizationId}
                    options={[]} // Replace with actual organization options
                    required
                    fullWidth
                  />
                ) : (
                  <TextField
                    label="Organization"
                    value={orgId}
                    InputProps={{
                      readOnly: true,
                    }}
                    fullWidth
                  />
                )}
              </Grid>
              <Grid item xs={12} sm={6}>
                <DatePicker
                  name="barDate"
                  label="Bar Date"
                  value={formData.barDate}
                  onChange={(value) => setFieldValue('barDate', value)}
                  onBlur={handleBlur}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <DatePicker
                  name="graduationDate"
                  label="Graduation Date"
                  value={formData.graduationDate}
                  onChange={(value) => setFieldValue('graduationDate', value)}
                  onBlur={handleBlur}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <DatePicker
                  name="promotionDate"
                  label="Promotion Date"
                  value={formData.promotionDate}
                  onChange={(value) => setFieldValue('promotionDate', value)}
                  onBlur={handleBlur}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Select
                  name="officeIds"
                  label="Office(s)"
                  value={formData.officeIds}
                  onChange={(value) => setFieldValue('officeIds', value)}
                  onBlur={handleBlur}
                  options={offices.map((office: any) => ({ value: office.id, label: office.name }))}
                  multiple
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Select
                  name="practiceAreas"
                  label="Practice Area(s)"
                  value={formData.practiceAreas}
                  onChange={(value) => setFieldValue('practiceAreas', value)}
                  onBlur={handleBlur}
                  options={practiceAreas.map((area: any) => ({ value: area.id, label: area.name }))}
                  multiple
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Select
                  name="staffClassId"
                  label="Staff Class"
                  value={formData.staffClassId}
                  onChange={(value) => setFieldValue('staffClassId', value)}
                  onBlur={handleBlur}
                  options={staffClasses.map((staffClass: any) => ({ value: staffClass.id, label: staffClass.name }))}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  name="unicourtId"
                  label="UniCourt ID"
                  value={formData.unicourtId}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  name="timekeeperIds"
                  label="Timekeeper IDs (Client: ID)"
                  value={formData.timekeeperIds}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  fullWidth
                />
              </Grid>
            </Grid>
            <Box mt={3} display="flex" justifyContent="flex-end">
              <Button onClick={() => navigate(-1)} style={{ marginRight: '10px' }}>
                Cancel
              </Button>
              <Button type="submit" variant="contained" color="primary" disabled={isSubmitting}>
                {isEditMode ? 'Update' : 'Create'}
              </Button>
            </Box>
          </form>
        </Paper>
      )}
    </Box>
  );
};

export default AttorneyForm;