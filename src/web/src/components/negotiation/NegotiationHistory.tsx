import React, { useState, useEffect, useMemo } from 'react'; // React library for building UI
import { useSelector, useDispatch } from 'react-redux'; // Redux hooks for accessing state and dispatching actions
import classNames from 'classnames'; // Utility for conditionally joining class names
import {
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  PencilSquareIcon,
  UserIcon,
} from '@heroicons/react/24/outline'; // Heroicons for different event types
import {
  Card,
  CardHeader,
  CardContent,
} from '../common/Card'; // UI container component for the history view
import Badge from '../common/Badge'; // UI component for displaying status labels
import Tooltip from '../common/Tooltip'; // UI component for displaying additional information on hover
import Avatar from '../common/Avatar'; // UI component for displaying user avatars
import Select from '../common/Select'; // UI component for selecting filter options
import Skeleton from '../common/Skeleton'; // UI component for loading states
import {
  NegotiationHistoryItem,
  NegotiationEventType,
  NegotiationEvent,
} from '../../types/negotiation'; // TypeScript interfaces for negotiation history data
import {
  selectNegotiationHistory,
  selectNegotiationLoading,
} from '../../store/negotiations/negotiationsSlice'; // Redux selectors for accessing negotiation history data
import { fetchNegotiationHistory } from '../../store/negotiations/negotiationsThunks'; // Redux thunk for fetching negotiation history data
import { formatDateTime } from '../../utils/date'; // Utility function for formatting date and time
import { formatCurrency } from '../../utils/formatting'; // Utility function for formatting currency values
import { usePermissions } from '../../hooks/usePermissions'; // Custom hook for checking user permissions

/**
 * Returns the appropriate icon component for a given event type
 * @param eventType 
 * @returns Icon component for the event type
 */
const getEventIcon = (eventType: NegotiationEventType): JSX.Element => {
  switch (eventType) {
    case 'SUBMISSION':
      return <DocumentTextIcon className="h-5 w-5" />;
    case 'COUNTER_PROPOSAL':
      return <ArrowPathIcon className="h-5 w-5" />;
    case 'APPROVAL':
      return <CheckCircleIcon className="h-5 w-5" />;
    case 'REJECTION':
      return <XCircleIcon className="h-5 w-5" />;
    case 'MESSAGE':
      return <ChatBubbleLeftRightIcon className="h-5 w-5" />;
    case 'MODIFICATION':
      return <PencilSquareIcon className="h-5 w-5" />;
    default:
      return <UserIcon className="h-5 w-5" />;
  }
};

/**
 * Returns the appropriate CSS color class for a given event type
 * @param eventType 
 * @returns CSS color class for the event type
 */
const getEventColor = (eventType: NegotiationEventType): string => {
  switch (eventType) {
    case 'SUBMISSION':
      return 'bg-blue-100 text-blue-800';
    case 'COUNTER_PROPOSAL':
      return 'bg-orange-100 text-orange-800';
    case 'APPROVAL':
      return 'bg-green-100 text-green-800';
    case 'REJECTION':
      return 'bg-red-100 text-red-800';
    case 'MESSAGE':
      return 'bg-purple-100 text-purple-800';
    case 'MODIFICATION':
      return 'bg-yellow-100 text-yellow-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

/**
 * Generates a human-readable description for a given event
 * @param event 
 * @returns Description of the event
 */
const getEventDescription = (event: NegotiationEvent): string => {
  switch (event.type) {
    case 'SUBMISSION':
      return `${event.user.name} submitted rates for ${event.data.count} attorneys`;
    case 'COUNTER_PROPOSAL':
      return `${event.user.name} counter-proposed ${event.data.count} rates`;
    case 'APPROVAL':
      return `${event.user.name} approved ${event.data.count} rates`;
    case 'REJECTION':
      return `${event.user.name} rejected ${event.data.count} rates`;
      case 'MESSAGE':
        return `${event.user.name} sent a message: "${event.data.content}"`;
    case 'MODIFICATION':
      return `${event.user.name} modified ${event.data.count} rates`;
    default:
      return `${event.user.name} performed an action`;
  }
};

/**
 * Renders a rate change detail with before and after values
 * @param changeData 
 * @returns Component displaying the rate change
 */
const renderRateChange = (changeData: any): JSX.Element => {
  const { attorneyName, previousRate, newRate } = changeData;
  const formattedPreviousRate = formatCurrency(previousRate, 'USD');
  const formattedNewRate = formatCurrency(newRate, 'USD');
  const percentageChange = ((newRate - previousRate) / previousRate) * 100;
  const changeClass = percentageChange > 0 ? 'text-green-500' : 'text-red-500';

  return (
    <div>
      {attorneyName}: {formattedPreviousRate} → {formattedNewRate} (<span className={changeClass}>{percentageChange.toFixed(2)}%</span>)
    </div>
  );
};

interface Props {
  negotiationId: string;
  showHeader?: boolean;
  compact?: boolean;
  maxItems?: number;
}

/**
 * Component for displaying negotiation history timeline
 * @param props 
 * @returns The rendered component
 */
const NegotiationHistory: React.FC<Props> = (props) => {
  const { negotiationId, showHeader = true, compact = false, maxItems } = props;
  const [filter, setFilter] = useState<string>('all');
  const history = useSelector(selectNegotiationHistory);
  const loading = useSelector(selectNegotiationLoading);
  const dispatch = useDispatch();
  const { can } = usePermissions();

  useEffect(() => {
    dispatch(fetchNegotiationHistory(negotiationId));
  }, [dispatch, negotiationId]);

  const filteredHistory = useMemo(() => {
    let filtered = history.sort((a, b) => new Date(b.performedAt).getTime() - new Date(a.performedAt).getTime());

    if (filter !== 'all') {
      filtered = filtered.filter(item => item.action === filter);
    }

    return filtered;
  }, [history, filter]);

  const handleFilterChange = (value: string) => {
    setFilter(value);
  };

  return (
    <Card className={classNames({ 'mb-4': showHeader }, { 'h-full': !showHeader })}>
      {showHeader && (
        <CardHeader title="Negotiation History" action={
          <Select
            name="historyFilter"
            value={filter}
            onChange={(e) => handleFilterChange(e.target.value as string)}
            options={[
              { value: 'all', label: 'All Events' },
              { value: 'submission', label: 'Submissions' },
              { value: 'counter_proposal', label: 'Counter Proposals' },
              { value: 'approval', label: 'Approvals' },
              { value: 'rejection', label: 'Rejections' },
              { value: 'message', label: 'Messages' },
              { value: 'modification', label: 'Modifications' },
            ]}
          />
        } />
      )}
      <CardContent padding="p-0">
        {loading ? (
          <div className="p-4">
            <Skeleton height="32px" />
            <Skeleton height="32px" />
            <Skeleton height="32px" />
          </div>
        ) : (
          <div className="relative">
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" style={{ marginLeft: '1.4px' }}></div>
            <ul className="space-y-4">
              {filteredHistory.slice(0, maxItems).map((item, index) => (
                <li key={item.id} className="ml-8">
                  <div className="flex items-center space-x-4">
                    <div className="relative">
                      <div className="absolute -left-7 w-14 text-right text-gray-500 text-sm">
                        {formatDateTime(item.performedAt)}
                      </div>
                      <Avatar name={item.user.name} size="sm" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="text-sm font-semibold">
                          {getEventDescription(item)}
                        </h3>
                      </div>
                      <p className="text-gray-600 text-sm">
                        {item.action}
                      </p>
                    </div>
                  </div>
                </li>
              ))}
              {filteredHistory.length === 0 && (
                <div className="p-4 text-center text-gray-500">
                  No history items available.
                </div>
              )}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default NegotiationHistory;