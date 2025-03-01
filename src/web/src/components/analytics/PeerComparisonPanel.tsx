import React, { useMemo, useState } from 'react'; // React v18.2.0
import styled from 'styled-components'; // styled-components v5.3.6

import useAnalytics from '../../hooks/useAnalytics';
import useOrganizations from '../../hooks/useOrganizations';
import PeerComparisonChart from '../charts/PeerComparisonChart';
import Select from '../common/Select';
import Card, { CardHeader, CardContent } from '../common/Card';
import Skeleton from '../common/Skeleton';
import ExportControls from './ExportControls';
import MetricDisplay from './MetricDisplay';
import { formatPercentage } from '../../utils/formatting';
import { PeerComparisonProps, PeerGroup, PeerComparisonData } from '../../types/analytics';

// Styled components for layout and styling
const PanelContainer = styled.div`
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const HeaderRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ChartContainer = styled.div`
  height: 300px;
  width: 100%;
  margin: 1rem 0;
`;

const MetricsContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
`;

const Title = styled.h2`
  margin: 0;
  font-size: 1.25rem;
  font-weight: 500;
  color: #2C5282;
`;

/**
 * A component that displays peer comparison analytics, showing how the organization's rate increases compare to defined peer groups
 */
const PeerComparisonPanel: React.FC<PeerComparisonProps> = ({
  title,
  height,
  filters,
  onExport,
}) => {
  // LD1: Initialize state for selectedPeerGroupId
  const [selectedPeerGroupId, setSelectedPeerGroupId] = useState<string | null>(null);

  // IE1: Use the useAnalytics hook to fetch peer comparison data
  const { peerComparison, fetchPeerComparison, isLoading } = useAnalytics();

  // IE1: Use the useOrganizations hook to fetch available peer groups
  const { peerGroups, fetchPeerGroups } = useOrganizations();

  // LD2: Fetch peer groups on component mount
  React.useEffect(() => {
    fetchPeerGroups("your_organization_id"); // TODO: Replace with actual organization ID
  }, [fetchPeerGroups]);

  // LD1: Create handlePeerGroupChange function to update the selected peer group
  const handlePeerGroupChange = (peerGroupId: string) => {
    setSelectedPeerGroupId(peerGroupId);
    // LD2: Fetch peer comparison data when the selected peer group changes
    fetchPeerComparison({
      ...filters,
      peerGroupId,
    });
  };

  // LD1: Format peer group options for the select component
  const peerGroupOptions = useMemo(() => {
    return peerGroups.map((group: PeerGroup) => ({
      value: group.id,
      label: group.name,
    }));
  }, [peerGroups]);

  // LD1: Extract key metrics from comparison data
  const yourFirmsAvg = peerComparison?.yourAverage || 0;
  const peerGroupAvg = peerComparison?.peerGroup?.averageRateIncrease || 0;
  const peerGroupMin = peerComparison?.peerGroup?.minRateIncrease || 0;
  const peerGroupMax = peerComparison?.peerGroup?.maxRateIncrease || 0;

  // LD1: Render loading skeleton when isLoading is true
  if (isLoading) {
    return (
      <Card>
        <PanelContainer>
          <Skeleton width="100%" height="2rem" />
          <Skeleton width="100%" height="300px" />
          <MetricsContainer>
            <Skeleton width="100%" height="5rem" />
            <Skeleton width="100%" height="5rem" />
            <Skeleton width="100%" height="5rem" />
          </MetricsContainer>
        </PanelContainer>
      </Card>
    );
  }

  // LD1: Render Card component with PanelContainer as the main wrapper
  return (
    <Card>
      <PanelContainer>
        {/* LD1: Render HeaderRow with Title and peer group Select dropdown */}
        <HeaderRow>
          <Title>{title || "Peer Group Comparison"}</Title>
          <Select
            name="peerGroup"
            label="Select Peer Group"
            options={peerGroupOptions}
            value={selectedPeerGroupId || ""}
            onChange={handlePeerGroupChange}
            placeholder="Select a peer group"
          />
        </HeaderRow>

        {/* LD1: Display PeerComparisonChart in ChartContainer with the comparison data */}
        {peerComparison && (
          <ChartContainer>
            <PeerComparisonChart data={peerComparison} height={height} />
          </ChartContainer>
        )}

        {/* LD1: Show key metrics in MetricsContainer using MetricDisplay components */}
        <MetricsContainer>
          <MetricDisplay
            label="Your Firm's Avg Increase"
            value={yourFirmsAvg}
            format="percentage"
            tooltipText="Average rate increase across your firm"
          />
          <MetricDisplay
            label="Peer Group Avg Increase"
            value={peerGroupAvg}
            format="percentage"
            tooltipText="Average rate increase across the selected peer group"
          />
          <MetricDisplay
            label="Peer Group Rate Increase Range"
            value={peerGroupMin !== peerGroupMax ? `${formatPercentage(peerGroupMin)} - ${formatPercentage(peerGroupMax)}` : formatPercentage(peerGroupMin)}
            format="number"
            tooltipText="Range of rate increases within the selected peer group"
          />
        </MetricsContainer>

        {/* LD1: Include ExportControls at the bottom for exporting the comparison data */}
        {onExport && (
          <ExportControls
            data={peerComparison}
            title="Peer Group Comparison"
            onExport={onExport}
            isLoading={isLoading}
          />
        )}
      </PanelContainer>
    </Card>
  );
};

export default PeerComparisonPanel;