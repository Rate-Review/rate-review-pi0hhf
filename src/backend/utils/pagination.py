"""
Utility module providing pagination functionality for API responses and database queries
across the Justice Bid Rate Negotiation System. Implements standardized pagination patterns,
parameter handling, and response formatting.
"""

from typing import Dict, List, Optional, Any, TypeVar, Generic, Tuple
from flask import Request, url_for
from sqlalchemy.orm import Query
from sqlalchemy import func

from ..utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from ..utils.validators import validate_integer

# Define pagination constants
PAGINATION_DEFAULT_PAGE = 1
PAGINATION_DEFAULT_PAGE_SIZE = DEFAULT_PAGE_SIZE
PAGINATION_MAX_PAGE_SIZE = MAX_PAGE_SIZE

# Define generic type variable
T = TypeVar('T')

def get_pagination_params(request: Request, 
                         default_page: int = PAGINATION_DEFAULT_PAGE, 
                         default_page_size: int = PAGINATION_DEFAULT_PAGE_SIZE, 
                         max_page_size: int = PAGINATION_MAX_PAGE_SIZE) -> Dict[str, int]:
    """
    Extracts pagination parameters from the request object with validation and defaults.
    
    Args:
        request: Flask request object
        default_page: Default page number if not provided in request
        default_page_size: Default page size if not provided in request
        max_page_size: Maximum allowed page size
        
    Returns:
        Dictionary with validated page and page_size parameters
    """
    # Extract page parameter from request args or use default
    try:
        page = int(request.args.get('page', default_page))
    except (TypeError, ValueError):
        page = default_page
    
    # Extract page_size parameter from request args or use default
    try:
        page_size = int(request.args.get('page_size', default_page_size))
    except (TypeError, ValueError):
        page_size = default_page_size
    
    # Validate pagination parameters
    validate_integer(page, 'page', min_value=1)
    validate_integer(page_size, 'page_size', min_value=1, max_value=max_page_size)
    
    # Enforce max_page_size limit
    page_size = min(page_size, max_page_size)
    
    return {
        'page': page,
        'page_size': page_size
    }

def paginate_query(query: Query, page: int, page_size: int) -> Tuple[List[Any], Dict[str, Any]]:
    """
    Applies pagination to an SQLAlchemy query and returns paginated results with metadata.
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-based)
        page_size: Number of items per page
        
    Returns:
        Tuple containing paginated items and pagination metadata
    """
    # Calculate offset based on page and page_size
    offset = (page - 1) * page_size
    
    # Get total count of items in the query
    total_count = query.count()
    
    # Apply limit and offset to the query
    items = query.limit(page_size).offset(offset).all()
    
    # Calculate total_pages based on total_count and page_size
    total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
    
    # Create pagination metadata dictionary
    pagination_metadata = {
        'page': page,
        'page_size': page_size,
        'total_count': total_count,
        'total_pages': total_pages
    }
    
    return items, pagination_metadata

def create_pagination_links(endpoint: str, page: int, page_size: int, 
                           total_pages: int, additional_params: Dict[str, Any] = {}) -> Dict[str, Optional[str]]:
    """
    Generates navigation links for paginated API responses using Flask's url_for.
    
    Args:
        endpoint: Flask endpoint for URL generation
        page: Current page number
        page_size: Number of items per page
        total_pages: Total number of pages
        additional_params: Additional query parameters to include in links
        
    Returns:
        Dictionary with first, prev, next, and last page URLs
    """
    # Initialize links dictionary with None values
    links = {
        'first': None,
        'prev': None,
        'next': None,
        'last': None
    }
    
    # Create link parameters by combining page, page_size, and additional_params
    params = {
        'page_size': page_size,
        **additional_params
    }
    
    # Generate first page link
    params['page'] = 1
    links['first'] = url_for(endpoint, **params, _external=True)
    
    # Generate previous page link if current page > 1
    if page > 1:
        params['page'] = page - 1
        links['prev'] = url_for(endpoint, **params, _external=True)
    
    # Generate next page link if current page < total_pages
    if page < total_pages:
        params['page'] = page + 1
        links['next'] = url_for(endpoint, **params, _external=True)
    
    # Generate last page link
    params['page'] = total_pages if total_pages > 0 else 1
    links['last'] = url_for(endpoint, **params, _external=True)
    
    return links

def create_pagination_response(items: List[T], page: int, page_size: int, 
                              total_count: int, endpoint: str, 
                              additional_params: Dict[str, Any] = {}) -> Dict[str, Any]:
    """
    Creates a standardized response structure for paginated data including items and metadata.
    
    Args:
        items: List of paginated items
        page: Current page number
        page_size: Number of items per page
        total_count: Total count of items across all pages
        endpoint: Flask endpoint for URL generation
        additional_params: Additional query parameters to include in links
        
    Returns:
        Standardized response with items and pagination metadata
    """
    # Calculate total_pages from total_count and page_size
    total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
    
    # Generate pagination links
    links = create_pagination_links(endpoint, page, page_size, total_pages, additional_params)
    
    # Create pagination metadata dictionary
    pagination = {
        'page': page,
        'page_size': page_size,
        'total_count': total_count,
        'total_pages': total_pages,
        'links': links
    }
    
    # Construct final response dictionary
    response = {
        'items': items,
        'pagination': pagination
    }
    
    return response

def apply_cursor_pagination(query: Query, cursor_column: str, cursor_value: Any, 
                           limit: int, ascending: bool = True) -> Tuple[List[Any], Optional[Any]]:
    """
    Implements cursor-based pagination for improved performance with large datasets.
    
    Args:
        query: SQLAlchemy query object
        cursor_column: Column name to use for cursor
        cursor_value: Current cursor value (value to start after)
        limit: Maximum number of items to return
        ascending: Whether to sort in ascending or descending order
        
    Returns:
        Tuple with results and next cursor value
    """
    # Apply filter to query based on cursor_value if provided
    if cursor_value is not None:
        column = getattr(query.column_descriptions[0]['entity'], cursor_column)
        if ascending:
            query = query.filter(column > cursor_value)
        else:
            query = query.filter(column < cursor_value)
    
    # Order query by cursor_column in ascending or descending order
    column = getattr(query.column_descriptions[0]['entity'], cursor_column)
    if ascending:
        query = query.order_by(column.asc())
    else:
        query = query.order_by(column.desc())
    
    # Apply limit to query
    query = query.limit(limit + 1)  # +1 to check if there are more results
    
    # Execute query to get results
    results = query.all()
    
    # Extract next cursor value from last result if results exist
    next_cursor = None
    if len(results) > limit:
        next_cursor = getattr(results[limit - 1], cursor_column)
        results = results[:limit]  # Remove the extra item
    
    return results, next_cursor

class PaginatedResponse(Generic[T]):
    """
    Generic class representing a paginated response with strongly typed items.
    """
    
    def __init__(self, items: List[T], page: int, page_size: int, 
                total_count: int, links: Dict[str, Optional[str]] = {}):
        """
        Initializes a paginated response with items and pagination metadata.
        
        Args:
            items: List of paginated items
            page: Current page number
            page_size: Number of items per page
            total_count: Total count of items across all pages
            links: Dictionary of navigation links
        """
        self.items = items
        
        # Calculate total_pages from total_count and page_size
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
        
        # Create pagination metadata dictionary with all parameters
        self.pagination = {
            'page': page,
            'page_size': page_size,
            'total_count': total_count,
            'total_pages': total_pages,
            'links': links
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the paginated response to a dictionary for JSON serialization.
        
        Returns:
            Dictionary representation with items and pagination
        """
        return {
            'items': self.items,
            'pagination': self.pagination
        }
    
    def has_next(self) -> bool:
        """
        Checks if there is a next page of results available.
        
        Returns:
            True if there are more pages after the current one
        """
        return self.pagination['page'] < self.pagination['total_pages']
    
    def has_prev(self) -> bool:
        """
        Checks if there is a previous page of results available.
        
        Returns:
            True if there are pages before the current one
        """
        return self.pagination['page'] > 1

class CursorPaginatedResponse(Generic[T]):
    """
    Class representing a cursor-paginated response for optimal performance with large datasets.
    """
    
    def __init__(self, items: List[T], limit: int, next_cursor: Optional[Any], 
                prev_cursor: Optional[Any] = None):
        """
        Initializes a cursor-paginated response with items and pagination metadata.
        
        Args:
            items: List of paginated items
            limit: Maximum number of items per page
            next_cursor: Cursor value for the next page
            prev_cursor: Cursor value for the previous page
        """
        self.items = items
        
        # Create pagination metadata with limit and cursor values
        self.pagination = {
            'limit': limit,
            'next_cursor': next_cursor,
            'prev_cursor': prev_cursor
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the cursor-paginated response to a dictionary for JSON serialization.
        
        Returns:
            Dictionary representation with items and pagination
        """
        return {
            'items': self.items,
            'pagination': self.pagination
        }
    
    def has_next(self) -> bool:
        """
        Checks if there are more results available after the current page.
        
        Returns:
            True if a next_cursor value exists
        """
        return self.pagination['next_cursor'] is not None