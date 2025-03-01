import React from 'react';
import styled from 'styled-components';
import { IconButton, MenuItem, Select, SelectChangeEvent } from '@mui/material';
import { NavigateNext, NavigateBefore } from '@mui/icons-material';
import Button from '../common/Button';
import theme from '../../theme';
import useQueryParams from '../../hooks/useQueryParams';

/**
 * Props for the Pagination component
 */
interface PaginationProps {
  /** Total number of items to paginate */
  totalItems: number;
  
  /** Number of items displayed per page */
  itemsPerPage: number;
  
  /** Current active page (1-based) */
  currentPage: number;
  
  /** Callback when page changes */
  onPageChange: (page: number) => void;
  
  /** Callback when items per page changes */
  onItemsPerPageChange?: (itemsPerPage: number) => void;
  
  /** Number of page buttons to display */
  displayedPageCount?: number;
  
  /** Available options for items per page selector */
  itemsPerPageOptions?: number[];
  
  /** Whether to show the items per page selector */
  showItemsPerPageSelector?: boolean;
  
  /** CSS class name for the pagination container */
  className?: string;
  
  /** Whether to sync pagination state with URL parameters */
  syncWithUrl?: boolean;
  
  /** URL parameter name for page (when syncWithUrl is true) */
  pageParam?: string;
  
  /** URL parameter name for items per page (when syncWithUrl is true) */
  itemsPerPageParam?: string;
}

/**
 * Calculates which page numbers should be visible based on current page and total pages
 * 
 * @param currentPage - Current active page
 * @param totalPages - Total number of pages
 * @param displayedPageCount - How many page numbers to display
 * @returns Array of page numbers to display
 */
const calculateVisiblePages = (
  currentPage: number, 
  totalPages: number, 
  displayedPageCount: number
): number[] => {
  const visiblePages: number[] = [];
  const halfCount = Math.floor(displayedPageCount / 2);
  
  let startPage = Math.max(currentPage - halfCount, 1);
  let endPage = startPage + displayedPageCount - 1;
  
  if (endPage > totalPages) {
    endPage = totalPages;
    startPage = Math.max(endPage - displayedPageCount + 1, 1);
  }
  
  for (let i = startPage; i <= endPage; i++) {
    visiblePages.push(i);
  }
  
  return visiblePages;
};

const PaginationContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: ${props => props.theme.spacing(2)}px 0;
  font-family: ${props => props.theme.typography.fontFamily.primary};
`;

const PaginationControls = styled.div`
  display: flex;
  align-items: center;
`;

const PageInfo = styled.div`
  margin: 0 ${props => props.theme.spacing(2)}px;
  color: ${props => props.theme.colors.text.secondary};
  font-size: ${props => props.theme.typography.fontSize.sm};
`;

const ItemsPerPageContainer = styled.div`
  display: flex;
  align-items: center;
  margin-left: ${props => props.theme.spacing(2)}px;
`;

const ItemsPerPageLabel = styled.span`
  margin-right: ${props => props.theme.spacing(1)}px;
  color: ${props => props.theme.colors.text.secondary};
  font-size: ${props => props.theme.typography.fontSize.sm};
`;

/**
 * A reusable pagination component for navigating through multi-page content
 * such as data tables and lists. Provides page navigation controls with
 * configurable page sizes and styling.
 */
const Pagination: React.FC<PaginationProps> = ({
  totalItems,
  itemsPerPage,
  currentPage,
  onPageChange,
  onItemsPerPageChange,
  displayedPageCount = 5,
  itemsPerPageOptions = [10, 25, 50, 100],
  showItemsPerPageSelector = true,
  className,
  syncWithUrl = false,
  pageParam = 'page',
  itemsPerPageParam = 'pageSize'
}) => {
  const { params, setParam } = useQueryParams();
  
  // Calculate total pages based on totalItems and itemsPerPage
  const totalPages = Math.max(1, Math.ceil(totalItems / itemsPerPage));
  
  // Calculate visible page numbers to display
  const visiblePages = calculateVisiblePages(currentPage, totalPages, displayedPageCount);
  
  // Calculate current range of items being displayed
  const startItem = totalItems > 0 ? Math.min((currentPage - 1) * itemsPerPage + 1, totalItems) : 0;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);
  
  // Handle page change
  const handlePageChange = (page: number) => {
    if (page < 1 || page > totalPages || page === currentPage) return;
    
    onPageChange(page);
    
    if (syncWithUrl) {
      setParam(pageParam, page);
    }
  };
  
  // Handle previous page navigation
  const handlePrevious = () => {
    handlePageChange(currentPage - 1);
  };
  
  // Handle next page navigation
  const handleNext = () => {
    handlePageChange(currentPage + 1);
  };
  
  // Handle items per page change
  const handleItemsPerPageChange = (event: SelectChangeEvent<number>) => {
    const newPageSize = Number(event.target.value);
    
    if (onItemsPerPageChange) {
      // Adjust current page to maintain approximate scroll position
      const firstItemIndex = (currentPage - 1) * itemsPerPage;
      const newPage = Math.max(1, Math.min(
        Math.floor(firstItemIndex / newPageSize) + 1,
        Math.ceil(totalItems / newPageSize)
      ));
      
      onItemsPerPageChange(newPageSize);
      onPageChange(newPage);
      
      if (syncWithUrl) {
        setParam(itemsPerPageParam, newPageSize);
        setParam(pageParam, newPage);
      }
    }
  };
  
  return (
    <PaginationContainer className={className}>
      <PaginationControls>
        <IconButton 
          onClick={handlePrevious} 
          disabled={currentPage <= 1}
          aria-label="Previous page"
          size="small"
        >
          <NavigateBefore />
        </IconButton>
        
        {visiblePages.map(page => (
          <Button 
            key={page}
            variant={page === currentPage ? "primary" : "text"}
            size="small"
            onClick={() => handlePageChange(page)}
            aria-label={`Page ${page}`}
            aria-current={page === currentPage ? 'page' : undefined}
          >
            {page}
          </Button>
        ))}
        
        <IconButton 
          onClick={handleNext}
          disabled={currentPage >= totalPages}
          aria-label="Next page"
          size="small"
        >
          <NavigateNext />
        </IconButton>
        
        <PageInfo>
          {totalItems > 0 
            ? `${startItem}-${endItem} of ${totalItems}`
            : 'No items'
          }
        </PageInfo>
      </PaginationControls>
      
      {showItemsPerPageSelector && onItemsPerPageChange && (
        <ItemsPerPageContainer>
          <ItemsPerPageLabel>Items per page:</ItemsPerPageLabel>
          <Select
            value={itemsPerPage}
            onChange={handleItemsPerPageChange}
            size="small"
            variant="outlined"
          >
            {itemsPerPageOptions.map(option => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </Select>
        </ItemsPerPageContainer>
      )}
    </PaginationContainer>
  );
};

export default Pagination;