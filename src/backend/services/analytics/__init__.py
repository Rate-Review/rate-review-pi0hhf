"""
Analytics service package initialization module that exposes key analytics services and functions for rate trends, impact analysis, peer comparison, attorney performance, custom reports, and general reporting capabilities in the Justice Bid Rate Negotiation System.
"""

from .rate_trends import RateTrendsAnalyzer  # Importing the rate trends analyzer for historical rate analysis
from .peer_comparison import PeerComparisonService  # Importing the peer comparison service for benchmarking rates
from .impact_analysis import ImpactAnalysisService  # Importing the impact analysis service for rate change financial projections
from .attorney_performance import AttorneyPerformanceService  # Importing the attorney performance service for performance metrics
from .reports import ReportService  # Importing the report service for generating standardized reports
from .custom_reports import CustomReportManager, ReportTemplate  # Importing custom report functionality for user-defined analytics
from .reports import format_report_data, export_report  # Importing utility functions for report formatting and exporting

__all__ = ["RateTrendsAnalyzer", "PeerComparisonService", "ImpactAnalysisService", "AttorneyPerformanceService", "ReportService", "CustomReportManager", "ReportTemplate", "format_report_data", "export_report"]