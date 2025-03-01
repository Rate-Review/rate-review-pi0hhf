import React from 'react'; //  ^18.0.0
import { useNavigate } from 'react-router-dom'; //  ^6.4.0
import { useSelector } from 'react-redux'; //  ^8.0.2
import classNames from 'classnames'; //  ^2.3.2
import Card from '../common/Card';
import Button from '../common/Button';
import Badge from '../common/Badge';
import StatusIndicator from '../common/StatusIndicator';
import { useNotifications } from '../../hooks/useNotifications';
import { ROUTES } from '../../constants/routes';

/**
 * ActionCenter Component
 *
 * A React functional component that displays prioritized actions that require the user's attention,
 * grouped by type with counts.
 *
 * @param props - React.HTMLAttributes<HTMLDivElement>
 * @returns JSX.Element - The rendered ActionCenter component
 */
const ActionCenter: React.FC<React.HTMLAttributes<HTMLDivElement>> = (props) => {
  // LD1: Use the useNotifications hook to fetch action items requiring attention
  const { notifications } = useNotifications();

  // LD1: Use the useNavigate hook for programmatic navigation
  const navigate = useNavigate();

  // LD1: Group the action items by type and calculate counts for each group
  const groupedActionsByType = groupActionsByType(notifications);

  // LD1: Returns the appropriate route path for a given action type
  const getActionRouteByType = (actionType: string): string => {
    // Map action types to corresponding route paths
    const routeMap: Record<string, string> = {
      'rate_request': ROUTES.RATE_REQUESTS,
      'negotiation': ROUTES.NEGOTIATIONS,
      'ocg': ROUTES.OCG,
      'approval': ROUTES.APPROVALS,
    };

    // Return the appropriate route path based on the action type
    return routeMap[actionType] || ROUTES.CLIENT_DASHBOARD;
  };

  /**
   * Groups action items by their type and calculates counts
   * @param actions - Array<{ id: string; type: string; title: string; priority: string; }>
   * @returns Record<string, { items: Array<{ id: string; type: string; title: string; priority: string; }>, count: number }> - Actions grouped by type with counts
   */
  const groupActionsByType = (actions: Array<{ id: string; type: string; title: string; priority: string; }>) => {
    // Initialize groupedActions object with empty arrays for each action type
    const groupedActions: Record<string, { items: Array<{ id: string; type: string; title: string; priority: string; }>, count: number }> = {
      'rate_request': { items: [], count: 0 },
      'negotiation': { items: [], count: 0 },
      'ocg': { items: [], count: 0 },
      'approval': { items: [], count: 0 },
    };

    // Iterate through the actions array
    actions.forEach(action => {
      // Add each action to the appropriate group based on its type
      if (groupedActions[action.type]) {
        groupedActions[action.type].items.push(action);
      }
    });

    // Calculate count for each group
    Object.keys(groupedActions).forEach(key => {
      groupedActions[key].count = groupedActions[key].items.length;
    });

    // Return the grouped actions object with items and counts
    return groupedActions;
  };

  return (
    // LD1: Render a Card component containing the action items grouped by type
    <Card title="Action Center" {...props}>
      <ul>
        {Object.entries(groupedActionsByType).map(([actionType, { items, count }]) => (
          // LD1: For each action type group, render a list item with StatusIndicator, text, and Badge showing count
          items.length > 0 && (
            <li key={actionType} className="mb-2 last:mb-0">
              <Button
                variant="text"
                className="w-full flex items-center justify-between text-left"
                onClick={() => navigate(getActionRouteByType(actionType))}
              >
                <div className="flex items-center">
                  <StatusIndicator status={actionType} size="small" className="mr-2" />
                  {actionType.replace(/_/g, ' ')}
                </div>
                <Badge content={count} variant="primary" />
              </Button>
            </li>
          )
        ))}
      </ul>
    </Card>
  );
};

export default ActionCenter;