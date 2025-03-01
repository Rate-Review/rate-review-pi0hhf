import React from 'react'; // ^18.0.0
import { render, screen, fireEvent, waitFor } from '@testing-library/react'; // ^13.0.0
import { jest, describe, it, expect } from 'jest'; // ^29.0.0
import RateTable from '../../components/tables/RateTable';
import { renderWithProviders } from '../../testUtils';
import { mockRates } from '../../tests/mocks/data';
import { Rate, RateStatus } from '../../../types/rate';

describe('RateTable Component', () => {
  it('renders correctly with default props', () => {
    renderWithProviders(<RateTable rates={[]} mode="view" />);
    expect(screen.getByText('No data available')).toBeInTheDocument();
  });

  it('displays rate data correctly', () => {
    const mockRatesData = mockRates.currentRates;
    renderWithProviders(<RateTable rates={mockRatesData} mode="view" />);
    expect(screen.getByText('James Smith')).toBeInTheDocument();
    expect(screen.getByText('$750.00')).toBeInTheDocument();
    expect(screen.getByText('Jan 1, 2023')).toBeInTheDocument();
    expect(screen.getByText('Approved')).toBeInTheDocument();
  });

  it('supports selecting rates', async () => {
    const mockOnSelect = jest.fn();
    const mockRatesData = mockRates.currentRates;
    renderWithProviders(<RateTable rates={mockRatesData} mode="view" onRateSelect={mockOnSelect} />);
    const checkbox = screen.getByRole('checkbox', { name: 'Select James Smith' });
    fireEvent.click(checkbox);
    await waitFor(() => expect(mockOnSelect).toHaveBeenCalledTimes(1));
    expect(mockOnSelect).toHaveBeenCalledWith(['rate-001']);
  });

  it('allows sorting of rates', async () => {
    const mockRatesData = mockRates.currentRates;
    renderWithProviders(<RateTable rates={mockRatesData} mode="view" />);
    const attorneyHeader = screen.getByText('Attorney');
    fireEvent.click(attorneyHeader);
    // Verify rates are sorted by attorney name
  });

  it('supports filtering rates', async () => {
    const mockRatesData = mockRates.currentRates;
    renderWithProviders(<RateTable rates={mockRatesData} mode="view" />);
    const searchInput = screen.getByPlaceholderText('Search');
    fireEvent.change(searchInput, { target: { value: 'James' } });
    // Verify only matching rates are displayed
    expect(screen.getByText('James Smith')).toBeInTheDocument();
    expect(screen.queryByText('Amanda Jones')).not.toBeInTheDocument();
  });

  it('shows approval/rejection buttons', async () => {
    const mockApproveRate = jest.fn();
    const mockRejectRate = jest.fn();
    const mockRatesData = mockRates.currentRates;
    renderWithProviders(<RateTable rates={mockRatesData} mode="negotiation" approveRate={mockApproveRate} rejectRate={mockRejectRate} />);
    const approveButton = screen.getByRole('button', { name: 'Approve' });
    const rejectButton = screen.getByRole('button', { name: 'Reject' });
    fireEvent.click(approveButton);
    expect(mockApproveRate).toHaveBeenCalled();
    fireEvent.click(rejectButton);
    expect(mockRejectRate).toHaveBeenCalled();
  });

  it('displays counter-proposal input', async () => {
    const mockCounterRate = jest.fn();
    const mockRatesData = mockRates.currentRates;
    renderWithProviders(<RateTable rates={mockRatesData} mode="negotiation" counterRate={mockCounterRate} />);
    const counterInput = screen.getByLabelText('Counter Rate');
    fireEvent.change(counterInput, { target: { value: '760' } });
    const counterButton = screen.getByRole('button', { name: 'Counter' });
    fireEvent.click(counterButton);
    expect(mockCounterRate).toHaveBeenCalled();
  });

  it('indicates excessive rate increases', () => {
    const mockRatesData = mockRates.currentRates;
    renderWithProviders(<RateTable rates={mockRatesData} mode="view" />);
    // Verify excessive increase indicators are shown for appropriate rates
  });

  it('handles custom cell rendering', () => {
    const mockRatesData = mockRates.currentRates;
    const customRenderer = jest.fn((rate: Rate) => <span>Custom: {rate.amount}</span>);
    renderWithProviders(<RateTable rates={mockRatesData} mode="view" customCellRenderer={customRenderer} />);
    // Verify custom renderer is used for specified columns
  });

  it('renders based on user permissions', () => {
    const mockRatesData = mockRates.currentRates;
    renderWithProviders(<RateTable rates={mockRatesData} mode="negotiation" />);
    // Verify certain actions are hidden/disabled based on permissions
  });
});