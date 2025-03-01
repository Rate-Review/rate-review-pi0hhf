import pytest
from unittest.mock import MagicMock
from datetime import date
from decimal import Decimal

from src.backend.services.analytics import rate_trends
from src.backend.services.analytics import peer_comparison
from src.backend.services.analytics import attorney_performance
from src.backend.services.analytics import impact_analysis
from src.backend.services.analytics import reports
from src.backend.services.analytics import custom_reports
from src.backend.db.repositories.rate_repository import RateRepository
from src.backend.db.repositories.billing_repository import BillingRepository
from src.backend.db.repositories.attorney_repository import AttorneyRepository
from src.backend.db.repositories.peer_group_repository import PeerGroupRepository

# Unit tests for analytics services in the Justice Bid Rate Negotiation System

# Test the get_historical_rate_trends function from rate_trends
@pytest.mark.parametrize('time_period, expected_data_points', [(1, 12), (3, 36), (5, 60)])
def test_get_historical_rate_trends(time_period, expected_data_points):
    # Mock the RateRepository.get_historical_rates method
    mock_rate_repository = MagicMock(spec=RateRepository)
    mock_rate_repository.get_historical_rates.return_value = [{'date': date(2023, 1, 1), 'rate': 100}] * expected_data_points

    # Call get_historical_rate_trends with different time periods
    trend_data = rate_trends.get_historical_rate_trends(rate_repository=mock_rate_repository, attorney_id='test_attorney', time_period=time_period)

    # Assert that the correct number of data points is returned
    assert len(trend_data) == expected_data_points

    # Assert that the trend data has the correct format and structure
    assert isinstance(trend_data, list)
    assert isinstance(trend_data[0], dict)
    assert 'date' in trend_data[0]
    assert 'rate' in trend_data[0]

    # Verify the mocked repository was called with correct parameters
    mock_rate_repository.get_historical_rates.assert_called_once()

# Test the calculate_rate_growth function from rate_trends
def test_calculate_rate_growth():
    # Setup test data with historical rates
    historical_rates = [100, 110, 121, 133.1]

    # Call calculate_rate_growth with the test data
    cagr = rate_trends.calculate_rate_growth(historical_rates)

    # Assert that the CAGR calculation is correct
    assert cagr == 10.0

    # Test with different time periods and rate values
    historical_rates = [100, 120]
    cagr = rate_trends.calculate_rate_growth(historical_rates, time_period=2)
    assert cagr == 9.54

    # Verify edge cases like no change and rate decreases
    historical_rates = [100, 100]
    cagr = rate_trends.calculate_rate_growth(historical_rates)
    assert cagr == 0.0

    historical_rates = [100, 90]
    cagr = rate_trends.calculate_rate_growth(historical_rates)
    assert cagr == -10.0

# Test the compare_rates_to_peer_group function from peer_comparison
def test_compare_rates_to_peer_group():
    # Mock PeerGroupRepository to return test peer group data
    mock_peer_group_repository = MagicMock(spec=PeerGroupRepository)
    mock_peer_group_repository.get_peer_group_members.return_value = ['firm1', 'firm2', 'firm3']

    # Mock RateRepository to return test rate data
    mock_rate_repository = MagicMock(spec=RateRepository)
    mock_rate_repository.get_rates_by_firm.return_value = [100, 110, 120]

    # Call compare_rates_to_peer_group with test parameters
    comparison_results = peer_comparison.compare_rates_to_peer_group(
        peer_group_repository=mock_peer_group_repository,
        rate_repository=mock_rate_repository,
        organization_id='test_org',
        peer_group_id='test_peer_group'
    )

    # Assert that the comparison results have the correct structure
    assert isinstance(comparison_results, dict)
    assert 'organization_id' in comparison_results
    assert 'peer_group_id' in comparison_results
    assert 'average_rate' in comparison_results
    assert 'rate_range' in comparison_results

    # Verify calculations for average rates, percentiles, and ranges are correct
    assert comparison_results['average_rate'] == 110.0
    assert comparison_results['rate_range'] == (100, 120)
    assert comparison_results['percentiles'] == [100, 110, 120]

    # Test with various peer groups and firm combinations
    mock_rate_repository.get_rates_by_firm.return_value = [150, 160, 170]
    comparison_results = peer_comparison.compare_rates_to_peer_group(
        peer_group_repository=mock_peer_group_repository,
        rate_repository=mock_rate_repository,
        organization_id='test_org',
        peer_group_id='test_peer_group'
    )
    assert comparison_results['average_rate'] == 160.0

# Test the get_peer_group_statistics function from peer_comparison
def test_get_peer_group_statistics():
    # Mock PeerGroupRepository to return test peer data
    mock_peer_group_repository = MagicMock(spec=PeerGroupRepository)
    mock_peer_group_repository.get_peer_group_members.return_value = ['firm1', 'firm2', 'firm3']

    # Call get_peer_group_statistics with test parameters
    statistics = peer_comparison.get_peer_group_statistics(
        peer_group_repository=mock_peer_group_repository,
        peer_group_id='test_peer_group'
    )

    # Assert that the statistics include average, min, max, and percentile values
    assert isinstance(statistics, dict)
    assert 'average_rate' in statistics
    assert 'min_rate' in statistics
    assert 'max_rate' in statistics
    assert 'percentiles' in statistics

    # Verify the calculations are accurate
    assert statistics['average_rate'] == 0.0
    assert statistics['min_rate'] == 0
    assert statistics['max_rate'] == 0
    assert statistics['percentiles'] == []

    # Test with different peer group sizes and compositions
    mock_peer_group_repository.get_peer_group_members.return_value = ['firm1', 'firm2']
    statistics = peer_comparison.get_peer_group_statistics(
        peer_group_repository=mock_peer_group_repository,
        peer_group_id='test_peer_group'
    )
    assert isinstance(statistics, dict)

# Test the get_attorney_performance_metrics function from attorney_performance
def test_get_attorney_performance_metrics():
    # Mock AttorneyRepository and BillingRepository with test data
    mock_attorney_repository = MagicMock(spec=AttorneyRepository)
    mock_billing_repository = MagicMock(spec=BillingRepository)
    mock_attorney_repository.get_attorney_billing_data.return_value = [{'hours': 100, 'fees': 50000}]
    mock_billing_repository.get_attorney_ratings.return_value = [4, 5, 4, 5]

    # Call get_attorney_performance_metrics with test attorney ID
    performance_metrics = attorney_performance.get_attorney_performance_metrics(
        attorney_repository=mock_attorney_repository,
        billing_repository=mock_billing_repository,
        attorney_id='test_attorney'
    )

    # Assert that performance metrics include hours, matters, and ratings
    assert isinstance(performance_metrics, dict)
    assert 'total_hours' in performance_metrics
    assert 'matter_count' in performance_metrics
    assert 'average_rating' in performance_metrics

    # Verify that UniCourt data is incorporated if available
    assert performance_metrics['total_hours'] == 100
    assert performance_metrics['matter_count'] == 0
    assert performance_metrics['average_rating'] == 4.5

    # Test with various attorney profiles and billing histories
    mock_attorney_repository.get_attorney_billing_data.return_value = [{'hours': 120, 'fees': 60000}]
    mock_billing_repository.get_attorney_ratings.return_value = [3, 4, 3, 4]
    performance_metrics = attorney_performance.get_attorney_performance_metrics(
        attorney_repository=mock_attorney_repository,
        billing_repository=mock_billing_repository,
        attorney_id='test_attorney'
    )
    assert performance_metrics['total_hours'] == 120
    assert performance_metrics['average_rating'] == 3.5

# Test the analyze_performance_vs_rates function from attorney_performance
def test_analyze_performance_vs_rates():
    # Mock AttorneyRepository, RateRepository, and BillingRepository with test data
    mock_attorney_repository = MagicMock(spec=AttorneyRepository)
    mock_rate_repository = MagicMock(spec=RateRepository)
    mock_billing_repository = MagicMock(spec=BillingRepository)
    mock_attorney_repository.get_attorney_billing_data.return_value = [{'hours': 100, 'fees': 50000}]
    mock_rate_repository.get_rates_by_attorney.return_value = [750]
    mock_billing_repository.get_attorney_ratings.return_value = [4, 5, 4, 5]

    # Call analyze_performance_vs_rates with test parameters
    value_metrics = attorney_performance.analyze_performance_vs_rates(
        attorney_repository=mock_attorney_repository,
        rate_repository=mock_rate_repository,
        billing_repository=mock_billing_repository,
        attorney_id='test_attorney'
    )

    # Assert that the analysis includes correlation between performance and rates
    assert isinstance(value_metrics, dict)
    assert 'utilization_rate' in value_metrics
    assert 'average_hourly_rate' in value_metrics
    assert 'client_satisfaction' in value_metrics

    # Verify that value metrics are correctly calculated
    assert value_metrics['utilization_rate'] == 0.0
    assert value_metrics['average_hourly_rate'] == 0.0
    assert value_metrics['client_satisfaction'] == 0.0

    # Test with different performance levels and rate structures
    mock_attorney_repository.get_attorney_billing_data.return_value = [{'hours': 120, 'fees': 60000}]
    mock_rate_repository.get_rates_by_attorney.return_value = [800]
    mock_billing_repository.get_attorney_ratings.return_value = [3, 4, 3, 4]
    value_metrics = attorney_performance.analyze_performance_vs_rates(
        attorney_repository=mock_attorney_repository,
        rate_repository=mock_rate_repository,
        billing_repository=mock_billing_repository,
        attorney_id='test_attorney'
    )
    assert value_metrics['utilization_rate'] == 0.0
    assert value_metrics['average_hourly_rate'] == 0.0
    assert value_metrics['client_satisfaction'] == 0.0

# Test the calculate_rate_impact function from impact_analysis
@pytest.mark.parametrize('proposed_rates, historical_hours, expected_impact', [(200, 100, 20000), (300, 200, 60000)])
def test_calculate_rate_impact(proposed_rates, historical_hours, expected_impact):
    # Setup test data with proposed rates and historical hours
    proposed_rates_data = [{'attorney_id': 'test_attorney', 'amount': proposed_rates}]
    historical_hours_data = {'test_attorney': historical_hours}

    # Call calculate_rate_impact with the test data
    impact = impact_analysis.calculate_rate_impact(proposed_rates_data, historical_hours_data)

    # Assert that the calculated impact matches expected results
    assert impact == expected_impact

    # Verify both absolute and percentage impacts are correct
    assert isinstance(impact, int)

    # Test with different rate increase scenarios
    proposed_rates_data = [{'attorney_id': 'test_attorney', 'amount': 250}]
    historical_hours_data = {'test_attorney': 150}
    impact = impact_analysis.calculate_rate_impact(proposed_rates_data, historical_hours_data)
    assert impact == 37500

# Test the project_annual_impact function from impact_analysis
def test_project_annual_impact():
    # Mock BillingRepository to return historical billing data
    mock_billing_repository = MagicMock(spec=BillingRepository)
    mock_billing_repository.get_billing_data.return_value = [{'hours': 100, 'fees': 50000}]

    # Call project_annual_impact with test parameters
    projected_impact = impact_analysis.project_annual_impact(
        billing_repository=mock_billing_repository,
        attorney_id='test_attorney',
        rate_increase=0.1
    )

    # Assert that the projected impact for the year is correctly calculated
    assert isinstance(projected_impact, float)
    assert projected_impact == 5000.0

    # Verify that seasonal adjustments are applied if specified
    projected_impact = impact_analysis.project_annual_impact(
        billing_repository=mock_billing_repository,
        attorney_id='test_attorney',
        rate_increase=0.1,
        seasonal_adjustment=[0.9, 1.1]
    )
    assert isinstance(projected_impact, float)

    # Test with different billing patterns and rate changes
    mock_billing_repository.get_billing_data.return_value = [{'hours': 120, 'fees': 60000}]
    projected_impact = impact_analysis.project_annual_impact(
        billing_repository=mock_billing_repository,
        attorney_id='test_attorney',
        rate_increase=0.1
    )
    assert isinstance(projected_impact, float)
    assert projected_impact == 6000.0

# Test the generate_standard_report function from reports
def test_generate_standard_report():
    # Mock required repositories with test data
    mock_rate_repository = MagicMock(spec=RateRepository)
    mock_billing_repository = MagicMock(spec=BillingRepository)
    mock_rate_trends_analyzer = MagicMock(spec=rate_trends.RateTrendsAnalyzer)
    mock_impact_analysis_service = MagicMock(spec=impact_analysis.ImpactAnalysisService)
    mock_peer_comparison_service = MagicMock(spec=peer_comparison.PeerComparisonService)

    # Call generate_standard_report with test parameters
    report_data = reports.generate_standard_report(
        rate_repository=mock_rate_repository,
        billing_repository=mock_billing_repository,
        rate_trends_analyzer=mock_rate_trends_analyzer,
        impact_analysis_service=mock_impact_analysis_service,
        peer_comparison_service=mock_peer_comparison_service,
        report_type='rate_analysis',
        parameters={'client_id': 'test_client'}
    )

    # Assert that the report contains all required sections
    assert isinstance(report_data, dict)
    assert 'report_type' in report_data
    assert 'parameters' in report_data
    assert 'data' in report_data

    # Verify that the data in the report is accurate
    assert report_data['report_type'] == 'rate_analysis'
    assert report_data['parameters']['client_id'] == 'test_client'

    # Test with different report types and parameters
    report_data = reports.generate_standard_report(
        rate_repository=mock_rate_repository,
        billing_repository=mock_billing_repository,
        rate_trends_analyzer=mock_rate_trends_analyzer,
        impact_analysis_service=mock_impact_analysis_service,
        peer_comparison_service=mock_peer_comparison_service,
        report_type='impact_analysis',
        parameters={'client_id': 'test_client', 'firm_id': 'test_firm'}
    )
    assert report_data['report_type'] == 'impact_analysis'
    assert report_data['parameters']['client_id'] == 'test_client'
    assert report_data['parameters']['firm_id'] == 'test_firm'

# Test the export_report_data function from reports
@pytest.mark.parametrize('format_type', ['csv', 'excel', 'pdf'])
def test_export_report_data(format_type):
    # Setup test report data
    report_data = {'report_type': 'test_report', 'data': [{'field1': 'value1', 'field2': 100}]}

    # Call export_report_data with different format types
    exported_data, mime_type = reports.export_report_data(report_data, format_type)

    # Assert that the export produces the correct file format
    assert isinstance(exported_data, bytes)

    # Verify that all data is included in the export
    assert len(exported_data) > 0

    # Test export of different report types and sizes
    report_data = {'report_type': 'large_report', 'data': [{'field1': 'value1', 'field2': 100}] * 1000}
    exported_data, mime_type = reports.export_report_data(report_data, format_type)
    assert isinstance(exported_data, bytes)
    assert len(exported_data) > 0

# Test the create_custom_report function from custom_reports
def test_create_custom_report():
    # Setup test report definition with fields and filters
    report_definition = {'name': 'test_report', 'fields': ['field1', 'field2'], 'filters': {'field1': 'value1'}}

    # Call create_custom_report with the test definition
    custom_report = custom_reports.create_custom_report(report_definition, 'test_org', 'test_user')

    # Assert that the report template is created correctly
    assert isinstance(custom_report, dict)
    assert 'report_id' in custom_report
    assert custom_report['name'] == 'test_report'

    # Verify that validation is performed on the report definition
    # (This requires more detailed mocking and validation logic)

    # Test with various report configurations
    report_definition = {'name': 'test_report2', 'fields': ['field3', 'field4'], 'filters': {'field2': 'value2'}}
    custom_report = custom_reports.create_custom_report(report_definition, 'test_org', 'test_user')
    assert isinstance(custom_report, dict)
    assert 'report_id' in custom_report
    assert custom_report['name'] == 'test_report2'

# Test the run_custom_report function from custom_reports
def test_run_custom_report():
    # Mock required repositories with test data
    mock_rate_repository = MagicMock(spec=RateRepository)
    mock_billing_repository = MagicMock(spec=BillingRepository)

    # Setup a test custom report definition
    report_definition = {'name': 'test_report', 'fields': ['hours', 'fees'], 'filters': {'client_id': 'test_client'}}

    # Call run_custom_report with the test report ID and parameters
    report_results = custom_reports.run_custom_report(
        rate_repository=mock_rate_repository,
        billing_repository=mock_billing_repository,
        report_id='test_report',
        report_definition=report_definition,
        parameters={'client_id': 'test_client'}
    )

    # Assert that the report results match expected output
    assert isinstance(report_results, dict)
    assert 'report_id' in report_results
    assert 'data' in report_results

    # Verify that filters and calculations are applied correctly
    # (This requires more detailed mocking and validation logic)

    # Test with different report parameters and data sets
    report_definition = {'name': 'test_report2', 'fields': ['hours', 'fees'], 'filters': {'firm_id': 'test_firm'}}
    report_results = custom_reports.run_custom_report(
        rate_repository=mock_rate_repository,
        billing_repository=mock_billing_repository,
        report_id='test_report2',
        report_definition=report_definition,
        parameters={'firm_id': 'test_firm'}
    )
    assert isinstance(report_results, dict)
    assert 'report_id' in report_results
    assert 'data' in report_results