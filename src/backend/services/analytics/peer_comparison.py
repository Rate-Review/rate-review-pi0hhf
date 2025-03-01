"""
Service for generating peer comparison analytics, comparing rates between organizations within defined peer groups.
"""

import pandas  # version: 2.0+
import numpy  # version: 1.24+
from typing import List, Dict, Any, Optional
import datetime
import logging  # standard library
from src.backend.db.models.peer_group import PeerGroup  # Access to peer group data model
from src.backend.db.models.organization import Organization  # Access to organization data model
from src.backend.db.models.rate import Rate  # Access to rate data model
from src.backend.db.models.attorney import Attorney  # Access to attorney data model
from src.backend.db.models.staff_class import StaffClass  # Access to staff class data model
from src.backend.db.repositories.peer_group_repository import PeerGroupRepository  # Repository for peer group data access
from src.backend.db.repositories.rate_repository import RateRepository  # Repository for rate data access
from src.backend.db.repositories.organization_repository import OrganizationRepository  # Repository for organization data access
from src.backend.utils.currency import convert_currency  # Currency conversion for comparing rates in different currencies

logger = logging.getLogger(__name__)


class PeerComparisonService:
    """
    Service class that provides peer comparison analytics functionality
    """

    def __init__(
        self,
        peer_group_repository: PeerGroupRepository,
        rate_repository: RateRepository,
        organization_repository: OrganizationRepository,
    ):
        """
        Initializes the PeerComparisonService with required repositories

        Args:
            peer_group_repository: Repository for peer group data access
            rate_repository: Repository for rate data access
            organization_repository: Repository for organization data access
        """
        self._peer_group_repository = peer_group_repository
        self._rate_repository = rate_repository
        self._organization_repository = organization_repository
        logger.info("PeerComparisonService initialized")

    def get_comparison(
        self,
        organization_id: str,
        peer_group_id: str,
        filters: Dict,
        target_currency: str,
        as_of_date: datetime.date,
    ) -> Dict:
        """
        Main method to generate peer comparison analytics

        Args:
            organization_id: ID of the organization to compare
            peer_group_id: ID of the peer group to compare against
            filters: Filters to apply to the rate data
            target_currency: Currency to convert all rates to
            as_of_date: Date to retrieve rates as of

        Returns:
            Comprehensive peer comparison analytics
        """
        logger.info(
            f"Generating peer comparison for organization {organization_id}, peer group {peer_group_id}"
        )
        # Validate the organization and peer group exist
        organization = self._organization_repository.get_by_id(uuid.UUID(organization_id))
        peer_group = self._peer_group_repository.get_by_id(uuid.UUID(peer_group_id))

        if not organization:
            logger.warning(f"Organization with ID {organization_id} not found")
            return {}
        if not peer_group:
            logger.warning(f"Peer group with ID {peer_group_id} not found")
            return {}

        # Call get_peer_comparison with parameters
        comparison_results = get_peer_comparison(
            organization_id, peer_group_id, filters, target_currency, as_of_date
        )

        # Return the comparison results
        return comparison_results

    def get_staff_class_comparison(
        self,
        organization_id: str,
        peer_group_id: str,
        filters: Dict,
        target_currency: str,
        as_of_date: datetime.date,
    ) -> Dict:
        """
        Generates peer comparison analytics grouped by staff class

        Args:
            organization_id: ID of the organization to compare
            peer_group_id: ID of the peer group to compare against
            filters: Filters to apply to the rate data
            target_currency: Currency to convert all rates to
            as_of_date: Date to retrieve rates as of

        Returns:
            Staff class comparison analytics
        """
        logger.info(
            f"Generating staff class comparison for organization {organization_id}, peer group {peer_group_id}"
        )
        # Call compare_rates_by_staff_class with parameters
        comparison_results = compare_rates_by_staff_class(
            organization_id, peer_group_id, filters, target_currency, as_of_date
        )

        # Return the comparison results
        return comparison_results

    def get_practice_area_comparison(
        self,
        organization_id: str,
        peer_group_id: str,
        filters: Dict,
        target_currency: str,
        as_of_date: datetime.date,
    ) -> Dict:
        """
        Generates peer comparison analytics grouped by practice area

        Args:
            organization_id: ID of the organization to compare
            peer_group_id: ID of the peer group to compare against
            filters: Filters to apply to the rate data
            target_currency: Currency to convert all rates to
            as_of_date: Date to retrieve rates as of

        Returns:
            Practice area comparison analytics
        """
        logger.info(
            f"Generating practice area comparison for organization {organization_id}, peer group {peer_group_id}"
        )
        # Call compare_rates_by_practice_area with parameters
        comparison_results = compare_rates_by_practice_area(
            organization_id, peer_group_id, filters, target_currency, as_of_date
        )

        # Return the comparison results
        return comparison_results

    def get_geography_comparison(
        self,
        organization_id: str,
        peer_group_id: str,
        filters: Dict,
        target_currency: str,
        as_of_date: datetime.date,
    ) -> Dict:
        """
        Generates peer comparison analytics grouped by geographic region

        Args:
            organization_id: ID of the organization to compare
            peer_group_id: ID of the peer group to compare against
            filters: Filters to apply to the rate data
            target_currency: Currency to convert all rates to
            as_of_date: Date to retrieve rates as of

        Returns:
            Geography comparison analytics
        """
        logger.info(
            f"Generating geography comparison for organization {organization_id}, peer group {peer_group_id}"
        )
        # Call compare_rates_by_geography with parameters
        comparison_results = compare_rates_by_geography(
            organization_id, peer_group_id, filters, target_currency, as_of_date
        )

        # Return the comparison results
        return comparison_results


def get_peer_comparison(
    organization_id: str,
    peer_group_id: str,
    filters: Dict,
    target_currency: str,
    as_of_date: datetime.date,
) -> Dict:
    """
    Generates peer comparison analytics for a given organization and peer group

    Args:
        organization_id: ID of the organization to compare
        peer_group_id: ID of the peer group to compare against
        filters: Filters to apply (staff class, practice area, etc.)
        target_currency: Currency to convert all rates to
        as_of_date: Date to retrieve rates as of

    Returns:
        Peer comparison analytics including averages, ranges, and percentiles
    """
    logger.info(
        f"Starting peer comparison for organization {organization_id}, peer group {peer_group_id}"
    )

    # 1. Validate input parameters
    try:
        uuid.UUID(organization_id)
        uuid.UUID(peer_group_id)
    except ValueError:
        logger.error("Invalid UUID format for organization_id or peer_group_id")
        return {}

    # 2. Retrieve organization and peer group data
    peer_group_repository = PeerGroupRepository(get_db())
    rate_repository = RateRepository(get_db())
    organization_repository = OrganizationRepository(get_db())

    organization = organization_repository.get_by_id(uuid.UUID(organization_id))
    peer_group = peer_group_repository.get_by_id(uuid.UUID(peer_group_id))

    if not organization or not peer_group:
        logger.warning(
            f"Organization or peer group not found: org={organization_id}, peer_group={peer_group_id}"
        )
        return {}

    # 3. Get rates for the specified organization
    org_rates = rate_repository.get_by_firm(
        firm_id=organization_id, as_of_date=as_of_date
    )
    org_rates_df = pandas.DataFrame([rate.__dict__ for rate in org_rates])

    # 4. Get rates for all organizations in the peer group
    peer_orgs = get_peer_group_organizations(peer_group_id, organization_id)
    peer_rates_df = pandas.DataFrame()
    for peer_org in peer_orgs:
        peer_rates = rate_repository.get_by_firm(
            firm_id=str(peer_org.id), as_of_date=as_of_date
        )
        peer_rates_df = pandas.concat(
            [peer_rates_df, pandas.DataFrame([rate.__dict__ for rate in peer_rates])],
            ignore_index=True,
        )

    # 5. Apply filters (staff class, practice area, etc.)
    org_rates_df = apply_filters(org_rates_df, filters)
    peer_rates_df = apply_filters(peer_rates_df, filters)

    # 6. Normalize currencies to target currency
    org_rates_df = normalize_currencies(org_rates_df, target_currency, as_of_date)
    peer_rates_df = normalize_currencies(peer_rates_df, target_currency, as_of_date)

    # 7. Calculate statistics (mean, median, range, percentiles)
    org_stats = calculate_rate_statistics(org_rates_df)
    peer_stats = calculate_rate_statistics(peer_rates_df)

    # 8. Structure and return the comparison data
    comparison_data = {
        "organization": {"id": organization_id, "name": organization.name, "stats": org_stats},
        "peer_group": {"id": peer_group_id, "name": peer_group.name, "stats": peer_stats},
        "filters": filters,
        "target_currency": target_currency,
        "as_of_date": as_of_date.isoformat(),
    }

    logger.info(
        f"Peer comparison completed for organization {organization_id}, peer group {peer_group_id}"
    )
    return comparison_data


def compare_rates_by_staff_class(
    organization_id: str,
    peer_group_id: str,
    filters: Dict,
    target_currency: str,
    as_of_date: datetime.date,
) -> Dict:
    """
    Compares rates across organizations within a peer group, grouped by staff class

    Args:
        organization_id: ID of the organization to compare
        peer_group_id: ID of the peer group to compare against
        filters: Filters to apply (practice area, etc.)
        target_currency: Currency to convert all rates to
        as_of_date: Date to retrieve rates as of

    Returns:
        Staff class comparison data with organization vs peer metrics
    """
    logger.info(
        f"Starting staff class comparison for organization {organization_id}, peer group {peer_group_id}"
    )

    # 1. Get staff classes for the organization
    organization_repository = OrganizationRepository(get_db())
    organization = organization_repository.get_by_id(uuid.UUID(organization_id))
    if not organization:
        logger.warning(f"Organization with ID {organization_id} not found")
        return {}

    staff_classes = organization.staff_classes
    comparison_data = {}

    # 2. For each staff class, retrieve rates from the organization
    rate_repository = RateRepository(get_db())
    for staff_class in staff_classes:
        org_rates = rate_repository.get_by_firm(
            firm_id=organization_id,
            staff_class_id=str(staff_class.id),
            as_of_date=as_of_date,
        )
        org_rates_df = pandas.DataFrame([rate.__dict__ for rate in org_rates])

        # 3. For each staff class, retrieve rates from peer organizations
        peer_group_repository = PeerGroupRepository(get_db())
        peer_orgs = get_peer_group_organizations(peer_group_id, organization_id)
        peer_rates_df = pandas.DataFrame()
        for peer_org in peer_orgs:
            peer_rates = rate_repository.get_by_firm(
                firm_id=str(peer_org.id),
                staff_class_id=str(staff_class.id),
                as_of_date=as_of_date,
            )
            peer_rates_df = pandas.concat(
                [peer_rates_df, pandas.DataFrame([rate.__dict__ for rate in peer_rates])],
                ignore_index=True,
            )

        # 4. Apply filters
        org_rates_df = apply_filters(org_rates_df, filters)
        peer_rates_df = apply_filters(peer_rates_df, filters)

        # 5. Normalize all rates to target currency
        org_rates_df = normalize_currencies(org_rates_df, target_currency, as_of_date)
        peer_rates_df = normalize_currencies(peer_rates_df, target_currency, as_of_date)

        # 6. Calculate statistics for each staff class
        org_stats = calculate_rate_statistics(org_rates_df)
        peer_stats = calculate_rate_statistics(peer_rates_df)

        # 7. Structure and return the comparison data by staff class
        comparison_data[staff_class.name] = {
            "organization": {"id": organization_id, "name": organization.name, "stats": org_stats},
            "peer_group": {"id": peer_group_id, "name": f"Peer Group - {staff_class.name}", "stats": peer_stats},
        }

    logger.info(
        f"Staff class comparison completed for organization {organization_id}, peer group {peer_group_id}"
    )
    return comparison_data


def compare_rates_by_practice_area(
    organization_id: str,
    peer_group_id: str,
    filters: Dict,
    target_currency: str,
    as_of_date: datetime.date,
) -> Dict:
    """
    Compares rates across organizations within a peer group, grouped by practice area

    Args:
        organization_id: ID of the organization to compare
        peer_group_id: ID of the peer group to compare against
        filters: Filters to apply (staff class, etc.)
        target_currency: Currency to convert all rates to
        as_of_date: Date to retrieve rates as of

    Returns:
        Practice area comparison data with organization vs peer metrics
    """
    logger.warning("compare_rates_by_practice_area is not yet implemented")
    return {}


def compare_rates_by_geography(
    organization_id: str,
    peer_group_id: str,
    filters: Dict,
    target_currency: str,
    as_of_date: datetime.date,
) -> Dict:
    """
    Compares rates across organizations within a peer group, grouped by geographic region

    Args:
        organization_id: ID of the organization to compare
        peer_group_id: ID of the peer group to compare against
        filters: Filters to apply (staff class, etc.)
        target_currency: Currency to convert all rates to
        as_of_date: Date to retrieve rates as of

    Returns:
        Geographic comparison data with organization vs peer metrics
    """
    logger.warning("compare_rates_by_geography is not yet implemented")
    return {}


def calculate_rate_statistics(rates_df: pandas.DataFrame) -> Dict:
    """
    Calculates statistical measures for a set of rates

    Args:
        rates_df: DataFrame containing rate data

    Returns:
        Statistics including mean, median, range, percentiles
    """
    if rates_df.empty:
        return {
            "mean": 0,
            "median": 0,
            "min": 0,
            "max": 0,
            "10th_percentile": 0,
            "25th_percentile": 0,
            "75th_percentile": 0,
            "90th_percentile": 0,
            "standard_deviation": 0,
        }

    # Calculate mean rate
    mean_rate = numpy.mean(rates_df["amount"])

    # Calculate median rate
    median_rate = numpy.median(rates_df["amount"])

    # Determine minimum and maximum rates
    min_rate = numpy.min(rates_df["amount"])
    max_rate = numpy.max(rates_df["amount"])

    # Calculate percentiles (10th, 25th, 75th, 90th)
    percentiles = numpy.percentile(rates_df["amount"], [10, 25, 75, 90])

    # Calculate standard deviation
    std_dev = numpy.std(rates_df["amount"])

    # Return the compiled statistics
    return {
        "mean": round(float(mean_rate), 2),
        "median": round(float(median_rate), 2),
        "min": round(float(min_rate), 2),
        "max": round(float(max_rate), 2),
        "10th_percentile": round(float(percentiles[0]), 2),
        "25th_percentile": round(float(percentiles[1]), 2),
        "75th_percentile": round(float(percentiles[2]), 2),
        "90th_percentile": round(float(percentiles[3]), 2),
        "standard_deviation": round(float(std_dev), 2),
    }


def normalize_currencies(
    rates_df: pandas.DataFrame, target_currency: str, conversion_date: datetime.date
) -> pandas.DataFrame:
    """
    Converts all rates in a DataFrame to a target currency

    Args:
        rates_df: DataFrame containing rate data
        target_currency: Currency to convert all rates to
        conversion_date: Date to use for currency conversion

    Returns:
        DataFrame with normalized currency values
    """
    if rates_df.empty:
        return rates_df

    # 1. Create a copy of the input DataFrame
    rates_df = rates_df.copy()

    # 2. Identify unique source currencies in the data
    unique_currencies = rates_df["currency"].unique()

    # 3. For each source currency, apply conversion to target currency
    for from_currency in unique_currencies:
        if from_currency == target_currency:
            continue  # Skip if already in target currency

        # Get exchange rate
        exchange_rate = convert_currency(1, from_currency, target_currency)

        # Apply conversion to the 'amount' column
        rates_df.loc[rates_df["currency"] == from_currency, "amount"] = (
            rates_df["amount"][rates_df["currency"] == from_currency] * exchange_rate
        )

    # 4. Update the currency column to reflect the target currency
    rates_df["currency"] = target_currency

    # 5. Return the normalized DataFrame
    return rates_df


def apply_filters(rates_df: pandas.DataFrame, filters: Dict) -> pandas.DataFrame:
    """
    Applies filtering criteria to a rates DataFrame

    Args:
        rates_df: DataFrame containing rate data
        filters: Dictionary of filters to apply

    Returns:
        Filtered DataFrame
    """
    if rates_df.empty:
        return rates_df

    # 1. Check for staff class filter and apply if present
    if "staff_class" in filters and filters["staff_class"]:
        rates_df = rates_df[rates_df["staff_class"] == filters["staff_class"]]

    # 2. Check for practice area filter and apply if present
    if "practice_area" in filters and filters["practice_area"]:
        rates_df = rates_df[rates_df["practice_area"] == filters["practice_area"]]

    # 3. Check for geography filter and apply if present
    if "geography" in filters and filters["geography"]:
        rates_df = rates_df[rates_df["geography"] == filters["geography"]]

    # 4. Check for attorney experience filter and apply if present
    if "attorney_experience" in filters and filters["attorney_experience"]:
        rates_df = rates_df[
            rates_df["attorney_experience"] == filters["attorney_experience"]
        ]

    # 5. Check for rate type filter and apply if present
    if "rate_type" in filters and filters["rate_type"]:
        rates_df = rates_df[rates_df["type"] == filters["rate_type"]]

    return rates_df


def get_peer_group_organizations(peer_group_id: str, exclude_organization_id: str) -> List[Organization]:
    """
    Retrieves all organizations in a peer group except the target organization

    Args:
        peer_group_id: ID of the peer group
        exclude_organization_id: ID of the organization to exclude

    Returns:
        List of organization objects in the peer group
    """
    peer_group_repository = PeerGroupRepository(get_db())

    # 1. Retrieve the peer group from the repository
    peer_group = peer_group_repository.get_by_id(uuid.UUID(peer_group_id))
    if not peer_group:
        logger.warning(f"Peer group with ID {peer_group_id} not found")
        return []

    # 2. Get all organization IDs in the peer group
    organization_ids = [org.id for org in peer_group.member_organizations]

    # 3. Exclude the specified organization ID
    organization_ids = [org_id for org_id in organization_ids if str(org_id) != exclude_organization_id]

    # 4. Retrieve organization objects for the remaining IDs
    organization_repository = OrganizationRepository(get_db())
    organizations = []
    for org_id in organization_ids:
        org = organization_repository.get_by_id(org_id)
        if org:
            organizations.append(org)

    # 5. Return the list of organization objects
    return organizations