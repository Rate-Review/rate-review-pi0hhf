import React, { useMemo } from 'react'; //  ^18.0.0
import { useNavigate } from 'react-router-dom'; //  ^6.4.0
import WarningIcon from '@mui/icons-material/Warning'; //  ^5.14.0
import NotificationsIcon from '@mui/icons-material/Notifications'; //  ^5.14.0
import AssignmentIcon from '@mui/icons-material/Assignment'; //  ^5.14.0
import DescriptionIcon from '@mui/icons-material/Description'; //  ^5.14.0
import DashboardCard from '../dashboard/DashboardCard';
import Button from '../common/Button';
import StatusIndicator from '../common/StatusIndicator';
import { useAuth } from '../../hooks/useAuth';
import { useNotifications } from '../../hooks/useNotifications';
import { useRates } from '../../hooks/useRates';
import { useNegotiations } from '../../hooks/useNegotiations';
import { useOCG } from '../../hooks/useOCG';
import { ROUTES } from '../../constants/routes';

/**
 * @internal
 * @remarks
 * Interface defining the structure of an action item for the ActionCenterCard component
 */
interface ActionItem {
  id: string;
  title: string;
  type: string;
  status: string;
  priority: number;
  onClick: () => void;
}

/**
 * @internal
 * @remarks
 * Returns the appropriate icon based on action type
 * @param actionType - string
 * @returns React.ReactNode - Icon component corresponding to the action type
 */
const getActionIcon = (actionType: string): React.ReactNode => {
  switch (actionType) {
    case 'rate_request':
      return <AssignmentIcon />;
    case 'counter_proposal':
      return <WarningIcon />;
    case 'ocg_negotiation':
      return <DescriptionIcon />;
    case 'approval_workflow':
      return <NotificationsIcon />;
    default:
      return <NotificationsIcon />;
  }
};

/**
 * @internal
 * @remarks
 * Calculates a priority score for an action item based on type, age, and status
 * @param action - ActionItem
 * @returns number - Priority score with higher numbers indicating higher priority
 */
const getPriorityScore = (action: ActionItem): number => {
  let score = 0;

  // Base score based on action type
  switch (action.type) {
    case 'rate_request':
      score += 50;
      break;
    case 'counter_proposal':
      score += 75;
      break;
    case 'ocg_negotiation':
      score += 60;
      break;
    case 'approval_workflow':
      score += 80;
      break;
    default:
      score += 40;
  }

  // Adjust score based on action age (older items may be more urgent)
  // TODO: Implement age-based priority adjustment

  // Adjust score based on status (pending approval might be higher priority)
  if (action.status === 'pending_approval') {
    score += 20;
  }

  return score;
};

/**
 * A component that displays prioritized action items requiring user attention on the dashboard
 * @param props - React.PropsWithChildren<{}>
 * @returns JSX.Element - The rendered action center card component
 */
const ActionCenterCard: React.FC = () => {
  // HOOKS:
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const { notifications } = useNotifications();
  const { fetchNegotiations } = useNegotiations();
  const { getOCGs } = useOCG();

  // MEMOIZED VARIABLES:
  const actionItems: ActionItem[] = useMemo(() => {
    const items: ActionItem[] = [];

    // Map over notifications to create action items
    notifications.forEach((notification) => {
      items.push({
        id: notification.id,
        title: notification.message,
        type: notification.type,
        status: notification.isRead ? 'read' : 'unread',
        priority: 0, // TODO: Implement priority calculation
        onClick: () => {
          // TODO: Implement navigation logic based on notification type
          console.log('Navigating to:', notification.entityType, notification.entityId);
        },
      });
    });

    // TODO: Fetch and map over rate requests, counter-proposals, and OCG negotiations
    // to create additional action items

    return items.sort((a, b) => b.priority - a.priority);
  }, [notifications]);

  // HANDLERS:
  const handleViewAllClick = () => {
    navigate(ROUTES.NOTIFICATIONS);
  };

  // RENDER:
  return (
    <DashboardCard title="ACTION CENTER">
      {actionItems.length > 0 ? (
        <ul>
          {actionItems.map((action) => (
            <li key={action.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0' }}>
              <div>
                {getActionIcon(action.type)}
                <span style={{ marginLeft: '8px' }}>{action.title}</span>
              </div>
              <StatusIndicator status={action.status} />
            </li>
          ))}
        </ul>
      ) : (
        <p>No actions required at this time.</p>
      )}
      <Button onClick={handleViewAllClick} style={{ marginTop: '16px' }}>
        View All
      </Button>
    </DashboardCard>
  );
};

export default ActionCenterCard;