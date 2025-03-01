"""
Provides mapping and data transformation utilities for the UniCourt integration, mapping Justice Bid attorneys 
to UniCourt attorneys and transforming UniCourt data to be used within the Justice Bid system.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
from fuzzywuzzy import fuzz  # v0.18.0
from fuzzywuzzy import process
import python_Levenshtein  # v0.12.2 - Optimizes fuzzywuzzy performance

from integrations.common.mapper import Mapper
from db.models.attorney import Attorney
from utils.datetime_utils import parse_date

# Set up logger
logger = logging.getLogger(__name__)

def map_attorney_to_unicourt(attorney: Attorney, unicourt_attorneys: Dict[str, Any], 
                            confidence_threshold: float = 0.7) -> Tuple[Optional[Dict[str, Any]], float]:
    """
    Maps a Justice Bid attorney to a potential UniCourt attorney match based on name, bar date, and other identifiers.

    Args:
        attorney: The Justice Bid attorney to map
        unicourt_attorneys: List of potential UniCourt attorney matches
        confidence_threshold: Minimum confidence score required for a match (0-1)

    Returns:
        Tuple containing the matched attorney data (or None if no match) and the confidence score.
    """
    if not unicourt_attorneys:
        logger.debug(f"No UniCourt attorneys provided for matching attorney: {attorney.name}")
        return None, 0.0
    
    # Find best match based on name similarity
    best_match, name_similarity = find_best_match(attorney.name, unicourt_attorneys)
    
    # Calculate overall confidence score considering additional factors
    confidence_score = calculate_confidence_score(attorney, best_match, name_similarity)
    
    logger.debug(f"Best match for {attorney.name}: {best_match.get('name', 'Unknown')} with confidence {confidence_score:.2f}")
    
    # Return match only if confidence meets threshold
    if confidence_score >= confidence_threshold:
        return best_match, confidence_score
    else:
        logger.debug(f"Match confidence {confidence_score:.2f} below threshold {confidence_threshold} for {attorney.name}")
        return None, confidence_score

def find_best_match(name: str, unicourt_attorneys: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], float]:
    """
    Find the best match for an attorney name from a list of UniCourt attorneys.

    Args:
        name: The attorney name to match
        unicourt_attorneys: List of UniCourt attorney data dictionaries

    Returns:
        Tuple containing the best matching attorney data and the confidence score.
    """
    # Normalize the name for better matching
    normalized_name = name.lower().strip()
    
    # Extract list of names from unicourt_attorneys
    attorney_names = [attorney.get('name', '') for attorney in unicourt_attorneys]
    
    # Use fuzzywuzzy's process to find the best match
    best_match_name, score = process.extractOne(normalized_name, attorney_names, scorer=fuzz.token_sort_ratio)
    
    # Normalize score to 0-1 range
    normalized_score = score / 100.0
    
    # Find the original attorney record for the best match
    for attorney in unicourt_attorneys:
        if attorney.get('name', '') == best_match_name:
            return attorney, normalized_score
    
    # Fallback if the match isn't found (shouldn't happen)
    logger.warning(f"Couldn't retrieve original record for best match name: {best_match_name}")
    return {}, 0.0

def transform_unicourt_attorney(unicourt_attorney: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms UniCourt attorney data into the format used by Justice Bid.

    Args:
        unicourt_attorney: Raw attorney data from UniCourt

    Returns:
        Transformed attorney data in Justice Bid format.
    """
    transformed = {}
    
    # Map basic attorney information
    transformed['name'] = unicourt_attorney.get('name', '')
    transformed['unicourt_id'] = unicourt_attorney.get('id', '')
    
    # Handle date fields with appropriate parsing
    if 'bar_admission_date' in unicourt_attorney:
        try:
            transformed['bar_date'] = parse_date(unicourt_attorney['bar_admission_date'])
        except ValueError:
            logger.warning(f"Could not parse bar admission date: {unicourt_attorney.get('bar_admission_date')}")
    
    # Extract and transform address information
    if 'address' in unicourt_attorney:
        address = unicourt_attorney['address']
        transformed['location'] = {
            'city': address.get('city', ''),
            'state': address.get('state', ''),
            'country': address.get('country', 'United States'),
        }
    
    # Map law firm information if available
    if 'law_firm' in unicourt_attorney:
        transformed['law_firm'] = {
            'name': unicourt_attorney['law_firm'].get('name', ''),
            'id': unicourt_attorney['law_firm'].get('id', '')
        }
    
    # Map education information if available
    if 'education' in unicourt_attorney:
        transformed['education'] = []
        for edu in unicourt_attorney['education']:
            education_entry = {
                'institution': edu.get('institution', ''),
                'degree': edu.get('degree', ''),
                'year': edu.get('year')
            }
            transformed['education'].append(education_entry)
            
            # Try to extract graduation date from education
            if not transformed.get('graduation_date') and edu.get('degree') == 'JD' and edu.get('year'):
                try:
                    # Assuming year is in YYYY format
                    transformed['graduation_date'] = parse_date(f"{edu['year']}-05-15")  # Using May 15 as a default graduation date
                except ValueError:
                    logger.warning(f"Could not parse graduation year: {edu.get('year')}")
    
    # Map practice areas
    if 'practice_areas' in unicourt_attorney:
        transformed['practice_areas'] = unicourt_attorney['practice_areas']
    
    # Map state bar numbers
    if 'bar_registrations' in unicourt_attorney:
        transformed['bar_registrations'] = {}
        for reg in unicourt_attorney['bar_registrations']:
            transformed['bar_registrations'][reg.get('state', '')] = reg.get('registration_number', '')
    
    return transformed

def transform_performance_data(performance_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms UniCourt case and performance data into the format used by Justice Bid.

    Args:
        performance_data: Raw performance data from UniCourt

    Returns:
        Transformed performance data in Justice Bid format.
    """
    transformed = {
        'cases': {
            'total': 0,
            'by_court_type': {},
            'by_year': {},
            'by_practice_area': {},
            'outcomes': {
                'wins': 0,
                'losses': 0,
                'settlements': 0,
                'other': 0
            }
        },
        'metrics': {
            'win_rate': 0.0,
            'case_complexity': 0.0,
            'avg_case_duration': 0.0,
            'practice_diversity': 0.0
        }
    }
    
    # Process overall case statistics
    cases = performance_data.get('cases', [])
    transformed['cases']['total'] = len(cases)
    
    wins = 0
    losses = 0
    settlements = 0
    total_duration = 0
    practice_areas = set()
    court_types = {}
    years = {}
    practice_area_counts = {}
    
    # Process individual cases
    for case in cases:
        # Track courts
        court_type = case.get('court_type', 'Unknown')
        court_types[court_type] = court_types.get(court_type, 0) + 1
        
        # Track years
        case_year = case.get('filing_date', '')[:4] if case.get('filing_date') else 'Unknown'
        years[case_year] = years.get(case_year, 0) + 1
        
        # Track practice areas
        practice_area = case.get('practice_area', 'Unknown')
        practice_areas.add(practice_area)
        practice_area_counts[practice_area] = practice_area_counts.get(practice_area, 0) + 1
        
        # Track outcomes
        outcome = case.get('outcome', {}).get('type', 'Unknown')
        if outcome == 'Win':
            wins += 1
        elif outcome == 'Loss':
            losses += 1
        elif outcome == 'Settlement':
            settlements += 1
        
        # Track duration
        if case.get('filing_date') and case.get('termination_date'):
            try:
                filing_date = parse_date(case['filing_date'])
                termination_date = parse_date(case['termination_date'])
                duration = (termination_date - filing_date).days
                total_duration += duration
            except ValueError:
                logger.warning(f"Could not parse dates for case duration: {case.get('id', 'Unknown')}")
    
    # Calculate derived metrics
    transformed['cases']['by_court_type'] = court_types
    transformed['cases']['by_year'] = years
    transformed['cases']['by_practice_area'] = practice_area_counts
    
    transformed['cases']['outcomes']['wins'] = wins
    transformed['cases']['outcomes']['losses'] = losses
    transformed['cases']['outcomes']['settlements'] = settlements
    transformed['cases']['outcomes']['other'] = len(cases) - (wins + losses + settlements)
    
    # Calculate average metrics
    if wins + losses > 0:
        transformed['metrics']['win_rate'] = round(wins / (wins + losses) * 100, 2)
    
    if len(cases) > 0:
        transformed['metrics']['avg_case_duration'] = round(total_duration / len(cases), 2)
    
    # Calculate practice diversity (0-1 scale)
    if len(cases) > 0:
        # Shannon diversity index simplified
        transformed['metrics']['practice_diversity'] = round(len(practice_areas) / len(cases), 2)
    
    # Calculate case complexity (0-5 scale)
    # Simple heuristic based on average duration and court types
    complexity_score = 0
    if total_duration / max(len(cases), 1) > 365:  # Cases lasting more than a year
        complexity_score += 1
    if court_types.get('Federal', 0) > court_types.get('State', 0):  # More federal than state cases
        complexity_score += 1
    if wins + losses > 10:  # Experienced in trials
        complexity_score += 1
    if len(practice_areas) > 3:  # Diverse practice
        complexity_score += 1
    if len(cases) > 50:  # High volume
        complexity_score += 1
    
    transformed['metrics']['case_complexity'] = complexity_score
    
    return transformed

def calculate_confidence_score(attorney: Attorney, unicourt_attorney: Dict[str, Any], name_similarity: float) -> float:
    """
    Calculates a confidence score for a potential attorney match based on various matching criteria.

    Args:
        attorney: Justice Bid attorney
        unicourt_attorney: UniCourt attorney data
        name_similarity: Base name similarity score (0-1)

    Returns:
        Confidence score between 0 and 1.
    """
    # Start with name similarity as base score
    confidence = name_similarity * 0.7  # Name is 70% of the total score
    
    # Check for matching bar admission date
    if attorney.bar_date and 'bar_admission_date' in unicourt_attorney:
        try:
            unicourt_bar_date = parse_date(unicourt_attorney['bar_admission_date'])
            if attorney.bar_date == unicourt_bar_date:
                confidence += 0.15  # Bar date is 15% of the total score
        except ValueError:
            logger.warning(f"Could not parse UniCourt bar date: {unicourt_attorney.get('bar_admission_date')}")
    
    # Check for matching law school
    if 'education' in unicourt_attorney and attorney.performance_data and 'education' in attorney.performance_data:
        # Simple check for any matching education institution
        justice_bid_schools = {edu.get('institution', '').lower() 
                              for edu in attorney.performance_data.get('education', [])}
        
        unicourt_schools = {edu.get('institution', '').lower() 
                           for edu in unicourt_attorney.get('education', [])}
        
        if justice_bid_schools.intersection(unicourt_schools):
            confidence += 0.1  # Education match is 10% of total score
    
    # Check for matching location
    if 'address' in unicourt_attorney and attorney.office_ids:
        # This is a simplified check - in a real implementation, we would
        # look up the office information associated with the office_ids
        # For now, we'll just log that we'd do this check
        logger.debug(f"Would check location match for attorney {attorney.name}")
        
        # Placeholder for location matching code
        # confidence += 0.05  # Location match would be 5% of total score
    
    # Ensure confidence is between 0 and 1
    return min(max(confidence, 0.0), 1.0)


class UniCourtMapper(Mapper):
    """
    Mapper class for transforming data between Justice Bid and UniCourt systems.
    """
    
    # Default confidence threshold for attorney matching
    DEFAULT_CONFIDENCE_THRESHOLD = 0.7
    
    # Field mapping between Justice Bid and UniCourt
    FIELD_MAPPING = {
        'name': 'name',
        'bar_date': 'bar_admission_date',
        'unicourt_id': 'id',
        # Add other field mappings as needed
    }
    
    # Performance data field mapping
    PERFORMANCE_MAPPING = {
        'cases': 'cases',
        'metrics': 'metrics',
        # Add other performance mappings as needed
    }
    
    def __init__(self):
        """
        Initializes the UniCourtMapper with logger and configuration.
        """
        super().__init__(self.FIELD_MAPPING)
        self.logger = logger
    
    def map_attorney(self, attorney: Attorney, unicourt_attorneys: List[Dict[str, Any]], 
                    confidence_threshold: Optional[float] = None) -> Tuple[Optional[Dict[str, Any]], float]:
        """
        Maps a Justice Bid attorney to a UniCourt attorney.

        Args:
            attorney: Justice Bid attorney to map
            unicourt_attorneys: List of potential UniCourt attorney matches
            confidence_threshold: Optional custom confidence threshold

        Returns:
            Matched attorney data and confidence score.
        """
        threshold = confidence_threshold if confidence_threshold is not None else self.DEFAULT_CONFIDENCE_THRESHOLD
        return map_attorney_to_unicourt(attorney, unicourt_attorneys, threshold)
    
    def transform_attorney_data(self, unicourt_attorney: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms UniCourt attorney data into Justice Bid format.

        Args:
            unicourt_attorney: UniCourt attorney data

        Returns:
            Transformed attorney data.
        """
        return transform_unicourt_attorney(unicourt_attorney)
    
    def transform_performance_metrics(self, unicourt_performance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms UniCourt performance metrics into Justice Bid format.

        Args:
            unicourt_performance: UniCourt performance data

        Returns:
            Transformed performance metrics.
        """
        return transform_performance_data(unicourt_performance)
    
    def batch_map_attorneys(self, attorneys: List[Attorney], unicourt_attorneys: List[Dict[str, Any]],
                          confidence_threshold: Optional[float] = None) -> Dict[str, Tuple[Optional[Dict[str, Any]], float]]:
        """
        Maps multiple Justice Bid attorneys to UniCourt attorneys in batch.

        Args:
            attorneys: List of Justice Bid attorneys to map
            unicourt_attorneys: List of potential UniCourt attorney matches
            confidence_threshold: Optional custom confidence threshold

        Returns:
            Mapping of attorney IDs to (matched attorney, confidence score) tuples.
        """
        threshold = confidence_threshold if confidence_threshold is not None else self.DEFAULT_CONFIDENCE_THRESHOLD
        results = {}
        
        for attorney in attorneys:
            matched_attorney, confidence = self.map_attorney(attorney, unicourt_attorneys, threshold)
            results[str(attorney.id)] = (matched_attorney, confidence)
        
        return results