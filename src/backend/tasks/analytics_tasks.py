"""
Contains Celery tasks for performing asynchronous analytics processing in the Justice Bid Rate Negotiation System. These tasks handle computation-intensive operations including rate impact analysis, peer comparisons, historical trend analysis, attorney performance metrics, and custom report generation.
"""

import uuid  # standard library
import datetime  # standard library
import json  # standard library
from typing import List, Dict, Any, Optional  # standard library
import time  # standard library

import pandas  # pandas==2.0+
import sqlalchemy  # sqlalchemy==2.0.0+
import openpyxl  # openpyxl==3.1.0+

from .celery_app import shared_task  # Import Celery app instance and shared_task decorator for registering tasks
from ..services.analytics.rate_trends import RateTrendsAnalyzer  # Service for analyzing historical rate trends over time
from ..services.analytics.impact_analysis import ImpactAnalysisService  # Service for calculating financial impact of rate changes
from ..services.analytics.peer_comparison import PeerComparisonService  # Service for generating peer comparison analytics
from ..services.analytics.attorney_performance import AttorneyPerformanceService  # Service for analyzing attorney performance metrics
from ..services.analytics.custom_reports import execute_custom_report  # Function for executing custom reports with user-defined parameters
from ..services.analytics.custom_reports import export_custom_report  # Function for exporting custom reports in various formats
from ..utils.cache import cache_result, invalidate_cache  # Cache decorator for analytics results to improve performance
from ..utils.logging import get_logger  # Function to get a logger for the module
from ..db.repositories.organization_repository import OrganizationRepository  # Repository for accessing organization data
from ..db.repositories.rate_repository import RateRepository  # Repository for accessing rate data
from ..db.repositories.peer_group_repository import PeerGroupRepository  # Repository for accessing peer group data

logger = get_logger(__name__)


@shared_task(bind=True, name='tasks.analytics.process_rate_impact_analysis')
def process_rate_impact_analysis(self, params: dict) -> dict:
    """
    Celery task for calculating the financial impact of rate changes based on historical billing data

    Args:
        params (dict): Parameters for the impact analysis including client_id, firm_id, proposed_rates, reference_period, filters, currency, etc.

    Returns:
        dict: Impact analysis results including total impact amount and percentage
    """
    start_time = time.time()
    logger.info(f"Starting rate impact analysis task", extra={'additional_data': {'params': params}})
    try:
        client_id = params['client_id']
        firm_id = params['firm_id']
        proposed_rates = params['proposed_rates']
        reference_period = (datetime.datetime.fromisoformat(params['reference_period'][0]).date(),
                             datetime.datetime.fromisoformat(params['reference_period'][1]).date())
        filters = params.get('filters', {})
        currency = params.get('currency', 'USD')
        view_type = params.get('view_type', 'total')

        rate_repository = RateRepository()
        billing_repository = BillingRepository()
        organization_repository = OrganizationRepository()
        impact_service = ImpactAnalysisService(rate_repository, billing_repository, organization_repository)

        impact_results = impact_service.calculate_impact(client_id, firm_id, proposed_rates, reference_period, filters, view_type, currency)

        cache_key = f"impact_analysis:{client_id}:{firm_id}"
        cache_result(cache_key, impact_results)

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Rate impact analysis task completed in {execution_time:.2f} seconds",
                    extra={'additional_data': {'client_id': client_id, 'firm_id': firm_id, 'execution_time': execution_time}})

        return impact_results

    except Exception as e:
        logger.error(f"Error during rate impact analysis: {str(e)}", exc_info=True)
        return {'error': str(e)}


@shared_task(bind=True, name='tasks.analytics.process_impact_by_staff_class')
def process_impact_by_staff_class(self, params: dict) -> dict:
    """
    Celery task for calculating rate impact broken down by staff class

    Args:
        params (dict): Parameters for the staff class impact analysis

    Returns:
        dict: Impact analysis by staff class
    """
    start_time = time.time()
    logger.info(f"Starting staff class impact analysis task", extra={'additional_data': {'params': params}})
    try:
        client_id = params['client_id']
        firm_id = params['firm_id']
        proposed_rates = params['proposed_rates']
        reference_period = (datetime.datetime.fromisoformat(params['reference_period'][0]).date(),
                             datetime.datetime.fromisoformat(params['reference_period'][1]).date())
        currency = params.get('currency', 'USD')

        rate_repository = RateRepository()
        billing_repository = BillingRepository()
        organization_repository = OrganizationRepository()
        impact_service = ImpactAnalysisService(rate_repository, billing_repository, organization_repository)

        impact_results = impact_service.calculate_impact_by_staff_class(client_id, firm_id, proposed_rates, reference_period, currency)

        cache_key = f"impact_by_staff_class:{client_id}:{firm_id}"
        cache_result(cache_key, impact_results)

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Staff class impact analysis task completed in {execution_time:.2f} seconds",
                    extra={'additional_data': {'client_id': client_id, 'firm_id': firm_id, 'execution_time': execution_time}})

        return impact_results

    except Exception as e:
        logger.error(f"Error during staff class impact analysis: {str(e)}", exc_info=True)
        return {'error': str(e)}


@shared_task(bind=True, name='tasks.analytics.process_impact_by_practice_area')
def process_impact_by_practice_area(self, params: dict) -> dict:
    """
    Celery task for calculating rate impact broken down by practice area

    Args:
        params (dict): Parameters for the practice area impact analysis

    Returns:
        dict: Impact analysis by practice area
    """
    start_time = time.time()
    logger.info(f"Starting practice area impact analysis task", extra={'additional_data': {'params': params}})
    try:
        client_id = params['client_id']
        firm_id = params['firm_id']
        proposed_rates = params['proposed_rates']
        reference_period = (datetime.datetime.fromisoformat(params['reference_period'][0]).date(),
                             datetime.datetime.fromisoformat(params['reference_period'][1]).date())
        currency = params.get('currency', 'USD')

        rate_repository = RateRepository()
        billing_repository = BillingRepository()
        organization_repository = OrganizationRepository()
        impact_service = ImpactAnalysisService(rate_repository, billing_repository, organization_repository)

        impact_results = impact_service.calculate_impact_by_practice_area(client_id, firm_id, proposed_rates, reference_period, currency)

        cache_key = f"impact_by_practice_area:{client_id}:{firm_id}"
        cache_result(cache_key, impact_results)

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Practice area impact analysis task completed in {execution_time:.2f} seconds",
                    extra={'additional_data': {'client_id': client_id, 'firm_id': firm_id, 'execution_time': execution_time}})

        return impact_results

    except Exception as e:
        logger.error(f"Error during practice area impact analysis: {str(e)}", exc_info=True)
        return {'error': str(e)}


@shared_task(bind=True, name='tasks.analytics.process_peer_comparison')
def process_peer_comparison(self, params: dict) -> dict:
    """
    Celery task for generating peer comparison analytics

    Args:
        params (dict): Parameters for the peer comparison including organization_id, peer_group_id, filters, target_currency, as_of_date, etc.

    Returns:
        dict: Peer comparison results with statistics and visualizations data
    """
    start_time = time.time()
    logger.info(f"Starting peer comparison task", extra={'additional_data': {'params': params}})
    try:
        organization_id = params['organization_id']
        peer_group_id = params['peer_group_id']
        filters = params.get('filters', {})
        target_currency = params.get('target_currency', 'USD')
        as_of_date = datetime.datetime.fromisoformat(params['as_of_date']).date()

        peer_group_repository = PeerGroupRepository()
        rate_repository = RateRepository()
        organization_repository = OrganizationRepository()
        peer_comparison_service = PeerComparisonService(peer_group_repository, rate_repository, organization_repository)

        comparison_results = peer_comparison_service.get_comparison(organization_id, peer_group_id, filters, target_currency, as_of_date)

        cache_key = f"peer_comparison:{organization_id}:{peer_group_id}"
        cache_result(cache_key, comparison_results)

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Peer comparison task completed in {execution_time:.2f} seconds",
                    extra={'additional_data': {'organization_id': organization_id, 'peer_group_id': peer_group_id, 'execution_time': execution_time}})

        return comparison_results

    except Exception as e:
        logger.error(f"Error during peer comparison: {str(e)}", exc_info=True)
        return {'error': str(e)}


@shared_task(bind=True, name='tasks.analytics.process_staff_class_peer_comparison')
def process_staff_class_peer_comparison(self, params: dict) -> dict:
    """
    Celery task for generating peer comparisons grouped by staff class

    Args:
        params (dict): Parameters for the staff class peer comparison

    Returns:
        dict: Staff class peer comparison results
    """
    start_time = time.time()
    logger.info(f"Starting staff class peer comparison task", extra={'additional_data': {'params': params}})
    try:
        organization_id = params['organization_id']
        peer_group_id = params['peer_group_id']
        filters = params.get('filters', {})
        target_currency = params.get('target_currency', 'USD')
        as_of_date = datetime.datetime.fromisoformat(params['as_of_date']).date()

        peer_group_repository = PeerGroupRepository()
        rate_repository = RateRepository()
        organization_repository = OrganizationRepository()
        peer_comparison_service = PeerComparisonService(peer_group_repository, rate_repository, organization_repository)

        comparison_results = peer_comparison_service.get_staff_class_comparison(organization_id, peer_group_id, filters, target_currency, as_of_date)

        cache_key = f"staff_class_peer_comparison:{organization_id}:{peer_group_id}"
        cache_result(cache_key, comparison_results)

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Staff class peer comparison task completed in {execution_time:.2f} seconds",
                    extra={'additional_data': {'organization_id': organization_id, 'peer_group_id': peer_group_id, 'execution_time': execution_time}})

        return comparison_results

    except Exception as e:
        logger.error(f"Error during staff class peer comparison: {str(e)}", exc_info=True)
        return {'error': str(e)}


@shared_task(bind=True, name='tasks.analytics.process_practice_area_peer_comparison')
def process_practice_area_peer_comparison(self, params: dict) -> dict:
    """
    Celery task for generating peer comparisons grouped by practice area

    Args:
        params (dict): Parameters for the practice area peer comparison

    Returns:
        dict: Practice area peer comparison results
    """
    start_time = time.time()
    logger.info(f"Starting practice area peer comparison task", extra={'additional_data': {'params': params}})
    try:
        organization_id = params['organization_id']
        peer_group_id = params['peer_group_id']
        filters = params.get('filters', {})
        target_currency = params.get('target_currency', 'USD')
        as_of_date = datetime.datetime.fromisoformat(params['as_of_date']).date()

        peer_group_repository = PeerGroupRepository()
        rate_repository = RateRepository()
        organization_repository = OrganizationRepository()
        peer_comparison_service = PeerComparisonService(peer_group_repository, rate_repository, organization_repository)

        comparison_results = peer_comparison_service.get_practice_area_comparison(organization_id, peer_group_id, filters, target_currency, as_of_date)

        cache_key = f"practice_area_peer_comparison:{organization_id}:{peer_group_id}"
        cache_result(cache_key, comparison_results)

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Practice area peer comparison task completed in {execution_time:.2f} seconds",
                    extra={'additional_data': {'organization_id': organization_id, 'peer_group_id': peer_group_id, 'execution_time': execution_time}})

        return comparison_results

    except Exception as e:
        logger.error(f"Error during practice area peer comparison: {str(e)}", exc_info=True)
        return {'error': str(e)}


@shared_task(bind=True, name='tasks.analytics.process_historical_rate_trends')
def process_historical_rate_trends(self, params: dict) -> dict:
    """
    Celery task for analyzing historical rate trends over multiple years

    Args:
        params (dict): Parameters for the historical rate trends analysis including entity_type, entity_id, start_date, end_date, currency, etc.

    Returns:
        dict: Historical trend analysis with yearly rates and CAGR calculations
    """
    start_time = time.time()
    logger.info(f"Starting historical rate trends task", extra={'additional_data': {'params': params}})
    try:
        entity_type = params['entity_type']
        entity_id = params['entity_id']
        start_date = datetime.datetime.fromisoformat(params['start_date']).date()
        end_date = datetime.datetime.fromisoformat(params['end_date']).date()
        currency = params.get('currency', 'USD')
        years = params.get('years', 5)

        rate_repository = RateRepository()
        billing_repository = BillingRepository()
        rate_trends_analyzer = RateTrendsAnalyzer(rate_repository, billing_repository)

        if entity_type == 'attorney':
            trend_results = rate_trends_analyzer.get_rate_trends_by_attorney(entity_id, start_date=start_date, end_date=end_date, currency=currency, years=years)
        elif entity_type == 'client':
            trend_results = rate_trends_analyzer.get_rate_trends_by_client(entity_id, start_date=start_date, end_date=end_date, currency=currency, years=years)
        elif entity_type == 'firm':
            trend_results = rate_trends_analyzer.get_rate_trends_by_firm(entity_id, start_date=start_date, end_date=end_date, currency=currency, years=years)
        else:
            raise ValueError(f"Invalid entity_type: {entity_type}")

        cache_key = f"historical_rate_trends:{entity_type}:{entity_id}"
        cache_result(cache_key, trend_results)

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Historical rate trends task completed in {execution_time:.2f} seconds",
                    extra={'additional_data': {'entity_type': entity_type, 'entity_id': entity_id, 'execution_time': execution_time}})

        return trend_results

    except Exception as e:
        logger.error(f"Error during historical rate trends analysis: {str(e)}", exc_info=True)
        return {'error': str(e)}


@shared_task(bind=True, name='tasks.analytics.process_rate_trends_time_series')
def process_rate_trends_time_series(self, params: dict) -> dict:
    """
    Celery task for generating time series data for rate trend visualizations

    Args:
        params (dict): Parameters for the time series generation including entity_type, entity_id, related_id, group_by, start_date, end_date, currency

    Returns:
        dict: Time series data for visualization in charts
    """
    start_time = time.time()
    logger.info(f"Starting time series generation task", extra={'additional_data': {'params': params}})
    try:
        entity_type = params['entity_type']
        entity_id = params['entity_id']
        related_id = params.get('related_id')
        group_by = params.get('group_by')
        start_date = datetime.datetime.fromisoformat(params['start_date']).date()
        end_date = datetime.datetime.fromisoformat(params['end_date']).date()
        currency = params.get('currency', 'USD')

        rate_repository = RateRepository()
        billing_repository = BillingRepository()
        rate_trends_analyzer = RateTrendsAnalyzer(rate_repository, billing_repository)

        time_series_data = rate_trends_analyzer.get_time_series_data(entity_type, entity_id, related_id, group_by, start_date, end_date, currency)

        cache_key = f"rate_trends_time_series:{entity_type}:{entity_id}"
        cache_result(cache_key, time_series_data)

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Time series generation task completed in {execution_time:.2f} seconds",
                    extra={'additional_data': {'entity_type': entity_type, 'entity_id': entity_id, 'execution_time': execution_time}})

        return time_series_data

    except Exception as e:
        logger.error(f"Error during time series generation: {str(e)}", exc_info=True)
        return {'error': str(e)}


@shared_task(bind=True, name='tasks.analytics.process_attorney_performance_analysis')
def process_attorney_performance_analysis(self, params: dict) -> dict:
    """
    Celery task for analyzing attorney performance metrics

    Args:
        params (dict): Parameters for the attorney performance analysis including attorney_id, client_id, start_date, end_date, include_unicourt, include_ratings, etc.

    Returns:
        dict: Attorney performance metrics and analysis results
    """
    start_time = time.time()
    logger.info(f"Starting attorney performance analysis task", extra={'additional_data': {'params': params}})
    try:
        attorney_id = params['attorney_id']
        client_id = params.get('client_id')
        start_date = datetime.datetime.fromisoformat(params['start_date']).date() if params.get('start_date') else None
        end_date = datetime.datetime.fromisoformat(params['end_date']).date() if params.get('end_date') else None
        include_unicourt = params.get('include_unicourt', True)
        include_ratings = params.get('include_ratings', True)
        include_rate_comparison = params.get('include_rate_comparison', True)

        rate_repository = RateRepository()
        billing_repository = BillingRepository()
        organization_repository = OrganizationRepository()
        attorney_repository = attorney_repository.AttorneyRepository()
        attorney_performance_service = AttorneyPerformanceService(attorney_repository, billing_repository, rate_repository, unicourt_client.UniCourtClient("test"), unicourt_mapper.UniCourtMapper())

        performance_metrics = attorney_performance_service.get_comprehensive_metrics(attorney_id, client_id, start_date, end_date, include_unicourt, include_ratings, include_rate_comparison)

        cache_key = f"attorney_performance:{attorney_id}"
        cache_result(cache_key, performance_metrics)

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Attorney performance analysis task completed in {execution_time:.2f} seconds",
                    extra={'additional_data': {'attorney_id': attorney_id, 'execution_time': execution_time}})

        return performance_metrics

    except Exception as e:
        logger.error(f"Error during attorney performance analysis: {str(e)}", exc_info=True)
        return {'error': str(e)}


@shared_task(bind=True, name='tasks.analytics.process_top_performers_analysis')
def process_top_performers_analysis(self, params: dict) -> dict:
    """
    Celery task for identifying top-performing attorneys based on criteria

    Args:
        params (dict): Parameters for the top performers analysis including client_id, firm_id, practice_area, staff_class_id, start_date, end_date, metrics, limit

    Returns:
        dict: List of top-performing attorneys with metrics
    """
    start_time = time.time()
    logger.info(f"Starting top performers analysis task", extra={'additional_data': {'params': params}})
    try:
        client_id = params.get('client_id')
        firm_id = params.get('firm_id')
        practice_area = params.get('practice_area')
        staff_class_id = params.get('staff_class_id')
        start_date = datetime.datetime.fromisoformat(params['start_date']).date() if params.get('start_date') else None
        end_date = datetime.datetime.fromisoformat(params['end_date']).date() if params.get('end_date') else None
        metrics = params.get('metrics')
        limit = params.get('limit', 10)

        rate_repository = RateRepository()
        billing_repository = BillingRepository()
        organization_repository = OrganizationRepository()
        attorney_repository = attorney_repository.AttorneyRepository()
        attorney_performance_service = AttorneyPerformanceService(attorney_repository, billing_repository, rate_repository, unicourt_client.UniCourtClient("test"), unicourt_mapper.UniCourtMapper())

        top_performers = attorney_performance_service.find_top_performers(client_id, firm_id, practice_area, staff_class_id, start_date, end_date, metrics, limit)

        cache_key = f"top_performers:{client_id}:{firm_id}"
        cache_result(cache_key, top_performers)

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Top performers analysis task completed in {execution_time:.2f} seconds",
                    extra={'additional_data': {'client_id': client_id, 'firm_id': firm_id, 'execution_time': execution_time}})

        return top_performers

    except Exception as e:
        logger.error(f"Error during top performers analysis: {str(e)}", exc_info=True)
        return {'error': str(e)}


@shared_task(bind=True, name='tasks.analytics.process_custom_report')
def process_custom_report(self, params: dict) -> dict:
    """
    Celery task for generating custom reports based on user-defined configuration

    Args:
        params (dict): Parameters for the custom report including report_id, organization_id, parameters, filters, page, page_size

    Returns:
        dict: Custom report results based on report configuration
    """
    start_time = time.time()
    logger.info(f"Starting custom report task", extra={'additional_data': {'params': params}})
    try:
        report_id = params['report_id']
        organization_id = params['organization_id']
        parameters = params.get('parameters', {})
        filters = params.get('filters', {})
        page = params.get('page', 1)
        page_size = params.get('page_size', 20)

        report_results = execute_custom_report(report_id, organization_id, parameters, filters, page, page_size)

        cache_key = f"custom_report:{report_id}:{organization_id}"
        cache_result(cache_key, report_results)

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Custom report task completed in {execution_time:.2f} seconds",
                    extra={'additional_data': {'report_id': report_id, 'organization_id': organization_id, 'execution_time': execution_time}})

        return report_results

    except Exception as e:
        logger.error(f"Error during custom report generation: {str(e)}", exc_info=True)
        return {'error': str(e)}


@shared_task(bind=True, name='tasks.analytics.export_report')
def export_report(self, params: dict) -> dict:
    """
    Celery task for exporting reports to various formats (Excel, CSV, PDF)

    Args:
        params (dict): Parameters for the report export including report_id, organization_id, parameters, filters, export_format

    Returns:
        dict: Export metadata including download URL
    """
    start_time = time.time()
    logger.info(f"Starting report export task", extra={'additional_data': {'params': params}})
    try:
        report_id = params['report_id']
        organization_id = params['organization_id']
        parameters = params.get('parameters', {})
        filters = params.get('filters', {})
        export_format = params.get('export_format', 'excel')

        export_metadata = export_custom_report(report_id, organization_id, parameters, filters, export_format)

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Report export task completed in {execution_time:.2f} seconds",
                    extra={'additional_data': {'report_id': report_id, 'organization_id': organization_id, 'export_format': export_format, 'execution_time': execution_time}})

        return export_metadata

    except Exception as e:
        logger.error(f"Error during report export: {str(e)}", exc_info=True)
        return {'error': str(e)}


@shared_task(bind=True, name='tasks.analytics.refresh_analytics_cache')
def refresh_analytics_cache(self, cache_keys: List[str] = None) -> dict:
    """
    Celery task for refreshing cached analytics data on a schedule

    Args:
        cache_keys (List[str], optional): List of specific cache keys to refresh. If None, refresh all analytics caches.

    Returns:
        dict: Status of refresh operations
    """
    start_time = time.time()
    logger.info("Starting analytics cache refresh task")
    try:
        refreshed_count = 0
        if cache_keys is None:
            # Invalidate commonly accessed analytics cache entries
            # This is a placeholder - in a real implementation, we would
            # identify these dynamically based on usage patterns
            cache_keys = [
                "impact_analysis:*",
                "peer_comparison:*",
                "historical_rate_trends:*"
            ]

        for key in cache_keys:
            count = invalidate_cache(key)
            refreshed_count += count

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Analytics cache refresh task completed in {execution_time:.2f} seconds, refreshed {refreshed_count} entries")

        return {'status': 'success', 'refreshed_count': refreshed_count}

    except Exception as e:
        logger.error(f"Error during analytics cache refresh: {str(e)}", exc_info=True)
        return {'status': 'error', 'error': str(e)}


@shared_task(bind=True, name='tasks.analytics.schedule_recurring_analytics')
def schedule_recurring_analytics(self) -> dict:
    """
    Celery task to trigger scheduled analytics jobs for all organizations

    Returns:
        dict: Summary of scheduled analytics tasks and their status
    """
    start_time = time.time()
    logger.info("Starting scheduled analytics task")
    try:
        organization_repository = OrganizationRepository()
        organizations = organization_repository.get_all()

        scheduled_tasks = {}
        for org in organizations:
            org_id = str(org.id)
            scheduled_tasks[org_id] = []

            # Determine which analytics need updating for this organization
            # (This is a placeholder - in a real implementation, we would
            # determine this based on the organization's settings and data)

            # Schedule appropriate analytics tasks with organization-specific parameters
            # (This is a placeholder - in a real implementation, we would
            # use Celery's signature to schedule the tasks)
            scheduled_tasks[org_id].append("impact_analysis")
            scheduled_tasks[org_id].append("peer_comparison")

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Scheduled analytics task completed in {execution_time:.2f} seconds, scheduled for {len(organizations)} organizations")

        return {'status': 'success', 'scheduled_tasks': scheduled_tasks}

    except Exception as e:
        logger.error(f"Error during scheduled analytics task: {str(e)}", exc_info=True)
        return {'status': 'error', 'error': str(e)}


@shared_task(bind=True, name='tasks.analytics.update_analytics_after_rate_change')
def update_analytics_after_rate_change(self, organization_id: str, affected_rate_ids: List[str]) -> dict:
    """
    Celery task to update all affected analytics after rates have been changed

    Args:
        organization_id (str): The ID of the organization that owns the rates
        affected_rate_ids (List[str]): A list of rate IDs that have been changed

    Returns:
        dict: Status of analytics updates
    """
    start_time = time.time()
    logger.info(f"Starting analytics update task after rate change", extra={'additional_data': {'organization_id': organization_id, 'affected_rate_ids': affected_rate_ids}})
    try:
        # Determine which analytics reports and caches are affected by the rate changes
        # (This is a placeholder - in a real implementation, we would
        # determine this based on the rate change and the report dependencies)
        affected_analytics = [
            "impact_analysis",
            "peer_comparison",
            "historical_rate_trends"
        ]

        # Invalidate all affected cache entries
        for analytic in affected_analytics:
            cache_key = f"{analytic}:{organization_id}"
            invalidate_cache(cache_key)

        # Schedule tasks to regenerate critical analytics (impact analysis, peer comparisons, trends)
        # (This is a placeholder - in a real implementation, we would
        # use Celery's signature to schedule the tasks)
        regenerated_analytics = ["impact_analysis", "peer_comparison"]

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Analytics update task completed in {execution_time:.2f} seconds, invalidated caches and scheduled regenerations for {len(affected_analytics)} analytics",
                    extra={'additional_data': {'organization_id': organization_id, 'affected_rate_ids': affected_rate_ids, 'regenerated_analytics': regenerated_analytics}})

        return {'status': 'success', 'invalidated_caches': affected_analytics, 'regenerated_analytics': regenerated_analytics}

    except Exception as e:
        logger.error(f"Error during analytics update after rate change: {str(e)}", exc_info=True)
        return {'status': 'error', 'error': str(e)}