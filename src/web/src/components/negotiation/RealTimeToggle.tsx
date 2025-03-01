import React, { useCallback, useEffect } from 'react'; //  ^18.0.0
import { Switch, FormControlLabel } from '@mui/material'; //  ^5.14.0
import { styled } from '@mui/material/styles'; //  ^5.14.0
import InfoOutlined from '@mui/icons-material/InfoOutlined'; //  ^5.14.0
import { useSelector, useDispatch } from '../../store';
import { setRealTimeMode } from '../../store/negotiations/negotiationsSlice';
import { usePermissions } from '../../hooks/usePermissions';
import Tooltip from '../common/Tooltip';

// Styled Switch component for consistent UI
const StyledSwitch = styled(Switch)(({ theme }) => ({
  width: 42,
  height: 26,
  padding: 0,
  '& .MuiSwitch-switchBase': {
    padding: 0,
    margin: 2,
    transition: 'transform 0.2s linear',
    '&.Mui-checked': {
      transform: 'translateX(16px)',
      color: '#fff',
      '& + .MuiSwitch-track': {
        opacity: 1,
        backgroundColor: theme.palette.primary.main,
      },
    },
  },
  '& .MuiSwitch-thumb': {
    width: 22,
    height: 22,
    boxShadow: 'none',
  },
  '& .MuiSwitch-track': {
    borderRadius: 13,
    border: `1px solid ${theme.palette.neutral.main}`,
    opacity: 1,
    backgroundColor: theme.palette.action.disabledBackground,
    transition: 'background-color 0.2s linear',
  },
}));

/**
 * A functional component that renders a toggle switch to enable or disable real-time negotiation mode.
 * @param props - The component props
 * @returns The rendered toggle component
 */
interface RealTimeToggleProps {
  negotiationId: string;
  initialValue?: boolean;
  onChange?: (enabled: boolean) => void;
  disabled?: boolean;
}

const RealTimeToggle: React.FC<RealTimeToggleProps> = (props) => {
  // LD1: Destructure props
  const { negotiationId, initialValue = false, onChange, disabled: propDisabled } = props;

  // LD1: Define local state for the toggle with useState hook
  const [enabled, setEnabled] = React.useState(initialValue);

  // LD1: Use useSelector to get the current real-time mode state from Redux
  const realTimeMode = useSelector((state) => state.negotiations.isRealTimeMode);

  // LD1: Use useDispatch to get the dispatch function for Redux actions
  const dispatch = useDispatch();

  // LD1: Use usePermissions to check if user has permission to toggle real-time mode
  const { can } = usePermissions();
  const hasPermission = can('update', 'negotiations', 'organization');

  // LD1: Define handleToggleChange function to handle toggle state changes
  const handleToggleChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      // Get the new checked state from the event
      const newEnabled = event.target.checked;

      // Update local state with the new value
      setEnabled(newEnabled);

      // Dispatch Redux action to update global state
      dispatch(setRealTimeMode({ negotiationId, enabled: newEnabled }));

      // Call onChange prop with the new value if provided
      if (onChange) {
        onChange(newEnabled);
      }
    },
    [dispatch, negotiationId, onChange]
  );

  // LD1: Use useEffect to sync local state with Redux state and handle initialValue changes
  useEffect(() => {
    setEnabled(realTimeMode);
  }, [realTimeMode]);

  useEffect(() => {
    setEnabled(initialValue);
  }, [initialValue]);

  // LD1: Apply appropriate disabled state based on permissions and disabled prop
  const isDisabled = propDisabled || !hasPermission;

  // LD1: Render FormControlLabel with Switch component and appropriate styling
  return (
    <FormControlLabel
      control={
        <StyledSwitch
          checked={enabled}
          onChange={handleToggleChange}
          disabled={isDisabled}
          name="realTime"
        />
      }
      label={
        <Tooltip content="When enabled, rate actions are immediately communicated to the other party. When disabled, actions are saved but not communicated until explicitly sent.">
          Real Time <InfoOutlined sx={{ fontSize: 'small', verticalAlign: 'middle', ml: 0.5 }} />
        </Tooltip>
      }
    />
  );
};

export default RealTimeToggle;