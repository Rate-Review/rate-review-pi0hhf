# flask==2.3+
from flask import Blueprint, request, g
# flask_graphql==2.0.0
from flask_graphql import GraphQLView
# graphene==3.0+
import graphene
from graphene import Schema, ObjectType, Field, List, String, Float, Int, Boolean, NonNull, InputObjectType, Argument
from typing import List, Dict, Any, Optional

from src.backend.api.core import auth
from src.backend.api.core.logging import logger
from src.backend.services.analytics import rate_trends
from src.backend.services.analytics import peer_comparison
from src.backend.services.analytics import impact_analysis
from src.backend.services.analytics import attorney_performance
from src.backend.services.analytics import custom_reports


graphql_blueprint = Blueprint('graphql', __name__, url_prefix='/api/graphql')


class RateTrendType(ObjectType):
    """GraphQL object type for rate trend data points over time"""
    year = String()
    average_rate = Float()
    percent_change = Float()
    staff_class = String()
    firm_name = String()
    currency = String()

    def __init__(self, *args, **kwargs):
        """Initializes the RateTrendType"""
        super().__init__(*args, **kwargs)


class PeerComparisonType(ObjectType):
    """GraphQL object type for peer comparison data"""
    firm_name = String()
    average_rate = Float()
    percent_difference = Float()
    peer_group = String()
    staff_class = String()
    currency = String()

    def __init__(self, *args, **kwargs):
        """Initializes the PeerComparisonType"""
        super().__init__(*args, **kwargs)


class ImpactAnalysisType(ObjectType):
    """GraphQL object type for rate impact analysis data"""
    firm_name = String()
    current_total = Float()
    proposed_total = Float()
    impact_amount = Float()
    impact_percentage = Float()
    staff_class = String()
    currency = String()

    def __init__(self, *args, **kwargs):
        """Initializes the ImpactAnalysisType"""
        super().__init__(*args, **kwargs)


class AttorneyPerformanceType(ObjectType):
    """GraphQL object type for attorney performance metrics"""
    attorney_name = String()
    attorney_id = String()
    hours_billed = Int()
    matter_count = Int()
    efficiency_score = Float()
    client_satisfaction = Float()
    firm_name = String()
    performance_index = Float()
    current_rate = Float()
    currency = String()

    def __init__(self, *args, **kwargs):
        """Initializes the AttorneyPerformanceType"""
        super().__init__(*args, **kwargs)


class CustomReportType(ObjectType):
    """GraphQL object type for custom report data"""
    report_id = String()
    report_name = String()
    created_by = String()
    created_at = String()
    report_type = String()
    data = graphene.JSONString()

    def __init__(self, *args, **kwargs):
        """Initializes the CustomReportType"""
        super().__init__(*args, **kwargs)


class CustomReportInputType(InputObjectType):
    """GraphQL input type for creating custom reports"""
    report_name = String()
    report_type = String()
    filters = graphene.JSONString()
    fields = List(String)
    grouping = List(String)

    def __init__(self, *args, **kwargs):
        """Initializes the CustomReportInputType"""
        super().__init__(*args, **kwargs)


class Query(ObjectType):
    """Root query object for GraphQL schema containing all available queries"""

    rate_trends = Field(List(RateTrendType),
                         firm_id=String(required=True),
                         start_year=String(required=True),
                         end_year=String(required=True),
                         staff_class=String(default_value="All"),
                         description="Resolver for rate trends query that provides historical rate data over time")

    @auth.authenticate
    @auth.check_permissions
    def resolve_rate_trends(self, info, firm_id, start_year, end_year, staff_class):
        """Resolver for rate trends query that provides historical rate data over time"""
        logger.info("GraphQL request for rate trends", extra={'additional_data': {'firm_id': firm_id, 'start_year': start_year, 'end_year': end_year, 'staff_class': staff_class}})
        result = rate_trends.get_rate_trends(firm_id, start_year, end_year, staff_class)
        rate_trends_list = [RateTrendType(**item) for item in result]
        return rate_trends_list

    peer_comparison = Field(List(PeerComparisonType),
                             firm_id=String(required=True),
                             peer_group_id=String(required=True),
                             staff_class=String(default_value="All"),
                             description="Resolver for peer comparison query that benchmarks rates against defined peer groups")

    @auth.authenticate
    @auth.check_permissions
    def resolve_peer_comparison(self, info, firm_id, peer_group_id, staff_class):
        """Resolver for peer comparison query that benchmarks rates against defined peer groups"""
        logger.info("GraphQL request for peer comparison", extra={'additional_data': {'firm_id': firm_id, 'peer_group_id': peer_group_id, 'staff_class': staff_class}})
        result = peer_comparison.get_peer_comparison(firm_id, peer_group_id, staff_class)
        peer_comparison_list = [PeerComparisonType(**item) for item in result]
        return peer_comparison_list

    impact_analysis = Field(List(ImpactAnalysisType),
                            client_id=String(required=True),
                            firm_id=String(required=True),
                            use_historical_hours=Boolean(default_value=True),
                            staff_class=String(default_value="All"),
                            description="Resolver for rate impact analysis query that calculates financial impact of rate changes")

    @auth.authenticate
    @auth.check_permissions
    def resolve_impact_analysis(self, info, client_id, firm_id, use_historical_hours, staff_class):
        """Resolver for rate impact analysis query that calculates financial impact of rate changes"""
        logger.info("GraphQL request for impact analysis", extra={'additional_data': {'client_id': client_id, 'firm_id': firm_id, 'use_historical_hours': use_historical_hours, 'staff_class': staff_class}})
        result = impact_analysis.get_impact_analysis(client_id, firm_id, use_historical_hours, staff_class)
        impact_analysis_list = [ImpactAnalysisType(**item) for item in result]
        return impact_analysis_list

    attorney_performance = Field(AttorneyPerformanceType,
                                  attorney_id=String(required=True),
                                  client_id=String(required=True),
                                  time_period=String(default_value="YTD"),
                                  description="Resolver for attorney performance query that provides performance metrics")

    @auth.authenticate
    @auth.check_permissions
    def resolve_attorney_performance(self, info, attorney_id, client_id, time_period):
        """Resolver for attorney performance query that provides performance metrics"""
        logger.info("GraphQL request for attorney performance", extra={'additional_data': {'attorney_id': attorney_id, 'client_id': client_id, 'time_period': time_period}})
        result = attorney_performance.get_attorney_performance(attorney_id, client_id, time_period)
        return AttorneyPerformanceType(**result)

    custom_report = Field(CustomReportType,
                            report_id=String(required=True),
                            description="Resolver for retrieving a saved custom report")

    @auth.authenticate
    def resolve_custom_report(self, info, report_id):
        """Resolver for retrieving a saved custom report"""
        logger.info("GraphQL request for custom report retrieval", extra={'additional_data': {'report_id': report_id}})
        report_data = custom_reports.get_report_data(report_id)
        return CustomReportType(**report_data)

    user_reports = Field(List(CustomReportType), description="Resolver for retrieving all reports created by the current user")

    @auth.authenticate
    def resolve_user_reports(self, info):
        """Resolver for retrieving all reports created by the current user"""
        logger.info("GraphQL request for user reports")
        user_id = auth.get_current_user().id
        user_reports_data = custom_reports.get_user_reports(user_id)
        return [CustomReportType(**report) for report in user_reports_data]


class Mutation(ObjectType):
    """Root mutation object for GraphQL schema containing all available mutations"""

    save_custom_report = Field(CustomReportType,
                                report_input=CustomReportInputType(required=True),
                                description="Mutation for saving a custom report configuration")

    @auth.authenticate
    @auth.check_permissions
    def resolve_save_custom_report(self, info, report_input):
        """Mutation for saving a custom report configuration"""
        logger.info("GraphQL request for saving a custom report", extra={'additional_data': {'report_name': report_input.report_name, 'report_type': report_input.report_type}})
        user_id = auth.get_current_user().id
        saved_report = custom_reports.save_report(report_input, user_id)
        return CustomReportType(**saved_report)


def create_schema():
    """Creates and configures the GraphQL schema with query and mutation types"""
    return Schema(query=Query, mutation=Mutation)


def init_graphql_routes(app):
    """Initializes GraphQL routes and registers them with the Flask application"""
    schema = create_schema()

    graphql_view = GraphQLView(schema=schema, graphiql=True, middleware=[auth_middleware])
    graphql_blueprint.add_url_rule('/graphql', view_func=graphql_view)
    app.register_blueprint(graphql_blueprint)

    logger.info("GraphQL routes initialized")


def auth_middleware(next, root, info, **kwargs):
    """Middleware for authenticating GraphQL requests before processing"""
    token = request.headers.get('Authorization')
    # TODO: Implement token validation and set authentication context
    return next(root, info, **kwargs)