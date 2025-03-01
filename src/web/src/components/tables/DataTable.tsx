import React, {
  useState,
  useEffect,
  useMemo,
  useCallback,
} from 'react'; // ^18.0.0
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Checkbox,
  Paper,
  Box,
  Typography,
  Tooltip,
  IconButton,
} from '@mui/material'; // ^5.14+
import {
  ArrowUpward,
  ArrowDownward,
  FilterList,
  FirstPage,
  LastPage,
  ChevronLeft,
  ChevronRight,
  MoreVert,
} from '@mui/icons-material'; // ^5.14+
import { styled } from '@mui/material/styles'; // ^5.14+
import { useWindowSize } from '../../hooks/useWindowSize'; // src/web/src/hooks/useWindowSize.ts
import { Pagination } from '../common/Pagination'; // src/web/src/components/common/Pagination.tsx
import { SearchBar } from '../common/SearchBar'; // src/web/src/components/common/SearchBar.tsx
import { EmptyState } from '../common/EmptyState'; // src/web/src/components/common/EmptyState.tsx
import { Spinner } from '../common/Spinner'; // src/web/src/components/common/Spinner.tsx

/**
 * Interface for defining column properties in DataTable
 */
export interface ColumnDef<T = any> {
  id: string;
  label: string;
  sortable?: boolean;
  filterable?: boolean;
  hidden?: boolean;
  align?: 'left' | 'right' | 'center';
  minWidth?: number;
  renderCell?: (row: T) => React.ReactNode;
}

/**
 * Interface defining the props for the DataTable component
 */
export interface DataTableProps<T = any> {
  data: T[];
  columns: ColumnDef<T>[];
  title?: string;
  isLoading?: boolean;
  emptyStateMessage?: string;
  selectable?: boolean;
  onRowClick?: (row: T) => void;
  onSelectionChange?: (selectedRows: T[]) => void;
  pagination?: boolean;
  defaultPageSize?: number;
  pageSizeOptions?: number[];
  search?: boolean;
  defaultSortField?: string;
  defaultSortDirection?: 'asc' | 'desc';
  customActions?: React.ReactNode;
}

/**
 * Returns a comparison function for sorting the table data
 * @param order - Sort order ('asc' or 'desc')
 * @param orderBy - Property to sort by
 * @returns Comparison function for sorting
 */
function getComparator<Key extends keyof any>(
  order: 'asc' | 'desc',
  orderBy: Key
): (
  a: { [key in Key]: number | string },
  b: { [key in Key]: number | string }
) => number {
  return order === 'desc'
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy);
}

/**
 * Performs a stable sort on the array, preserving original order for equal elements
 * @param array - Array to sort
 * @param comparator - Comparator function
 * @returns Sorted array
 */
function stableSort<T>(array: readonly T[], comparator: (a: T, b: T) => number): T[] {
  const stabilizedThis = array.map((el, index) => [el, index] as [T, number]);
  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) {
      return order;
    }
    return a[1] - b[1];
  });
  return stabilizedThis.map((el) => el[0]);
}

/**
 * Filters data based on search term and column filters
 * @param data - Array of data to filter
 * @param searchTerm - Search term to filter by
 * @param filters - Object containing column filters
 * @param columns - Array of column definitions
 * @returns Filtered data
 */
function filterData<T>(
  data: T[],
  searchTerm: string,
  filters: { [key: string]: any },
  columns: ColumnDef<T>[]
): T[] {
  if (!searchTerm && Object.keys(filters).length === 0) {
    return data;
  }

  let filteredData = data;

  if (searchTerm) {
    filteredData = filteredData.filter((row) =>
      columns.filter((col) => col.filterable !== false)
        .some((col) => {
          const value = row[col.id as keyof T];
          if (typeof value === 'string') {
            return value.toLowerCase().includes(searchTerm.toLowerCase());
          }
          if (typeof value === 'number') {
            return value.toString().includes(searchTerm);
          }
          return false;
        })
    );
  }

  for (const columnId in filters) {
    if (filters[columnId]) {
      filteredData = filteredData.filter((row) => row[columnId as keyof T] === filters[columnId]);
    }
  }

  return filteredData;
}

/**
 * Reusable table component with sorting, filtering, pagination and selection capabilities
 * @param props - Props for the component
 * @returns Rendered table component
 */
const DataTable: React.FC<DataTableProps> = <T extends object>({
  data,
  columns,
  title,
  isLoading = false,
  emptyStateMessage = 'No data available',
  selectable = false,
  onRowClick,
  onSelectionChange,
  pagination = true,
  defaultPageSize = 10,
  pageSizeOptions = [5, 10, 25, 50],
  search = true,
  defaultSortField,
  defaultSortDirection = 'asc',
  customActions,
}) => {
  // State for sorting
  const [order, setOrder] = useState<'asc' | 'desc'>(defaultSortDirection);
  const [orderBy, setOrderBy] = useState<string>(defaultSortField || '');

  // State for pagination
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(defaultPageSize);

  // State for selection
  const [selected, setSelected] = useState<T[]>([]);

  // State for search
  const [searchTerm, setSearchTerm] = useState('');

  // State for filters
  const [filters, setFilters] = useState<{ [key: string]: any }>({});

  // Hook for window size
  const { width } = useWindowSize();

  // Calculate visible columns based on screen size
  const visibleColumns = useMemo(() => {
    return columns.filter((column) => width >= 768 || !column.hidden);
  }, [columns, width]);

  // Handlers for sorting
  const handleRequestSort = (property: string) => () => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  // Handlers for selection
  const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelected([...data]);
      onSelectionChange?.([...data]);
      return;
    }
    setSelected([]);
    onSelectionChange?.([]);
  };

  const handleClick = (row: T) => (event: React.MouseEvent<unknown>) => {
    if (selectable) {
      const selectedIndex = selected.indexOf(row);
      let newSelected: T[] = [];

      if (selectedIndex === -1) {
        newSelected = newSelected.concat(selected, row);
      } else if (selectedIndex === 0) {
        newSelected = newSelected.concat(selected.slice(1));
      } else if (selectedIndex === selected.length - 1) {
        newSelected = newSelected.concat(selected.slice(0, -1));
      } else if (selectedIndex > 0) {
        newSelected = newSelected.concat(
          selected.slice(0, selectedIndex),
          selected.slice(selectedIndex + 1),
        );
      }

      setSelected(newSelected);
      onSelectionChange?.(newSelected);
    }
    onRowClick?.(row);
  };

  const isSelected = (row: T) => selected.indexOf(row) !== -1;

  // Handlers for pagination
  const handleChangePage = (newPage: number) => {
    setPage(newPage);
  };

  const handleChangePageSize = (newPageSize: number) => {
    setPageSize(newPageSize);
    setPage(1);
  };

  // Handler for search
  const handleSearch = (value: string) => {
    setSearchTerm(value);
    setPage(1);
  };

  // Process data
  const filteredData = useMemo(() => {
    return filterData(data, searchTerm, filters, columns);
  }, [data, searchTerm, filters, columns]);

  const sortedData = useMemo(() => {
    return stableSort(filteredData, getComparator(order, orderBy));
  }, [filteredData, order, orderBy]);

  const paginatedData = useMemo(() => {
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return sortedData.slice(startIndex, endIndex);
  }, [sortedData, page, pageSize]);

  const numSelected = selected.length;
  const rowCount = data.length;

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      {title && (
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2 }}>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
          {customActions}
        </Box>
      )}
      {search && (
        <Box sx={{ p: 2 }}>
          <SearchBar placeholder="Search" onSearch={handleSearch} />
        </Box>
      )}
      <TableContainer>
        <Table
          sx={{ minWidth: 750 }}
          aria-labelledby="tableTitle"
        >
          <TableHead>
            <TableRow>
              {selectable && (
                <TableCell padding="checkbox">
                  <Checkbox
                    color="primary"
                    indeterminate={numSelected > 0 && numSelected < rowCount}
                    checked={rowCount > 0 && numSelected === rowCount}
                    onChange={handleSelectAllClick}
                    inputProps={{
                      'aria-label': 'select all desserts',
                    }}
                  />
                </TableCell>
              )}
              {visibleColumns.map((column) => (
                <TableCell
                  key={column.id}
                  align={column.align || 'left'}
                  padding="normal"
                  sortDirection={orderBy === column.id ? order : false}
                  style={{ minWidth: column.minWidth }}
                >
                  {column.sortable !== false ? (
                    <TableSortLabel
                      active={orderBy === column.id}
                      direction={orderBy === column.id ? order : 'asc'}
                      onClick={handleRequestSort(column.id)}
                    >
                      {column.label}
                      {orderBy === column.id ? (
                        <Box component="span" sx={{ display: 'flex', alignItems: 'center' }}>
                          {order === 'desc' ? <ArrowDownward /> : <ArrowUpward />}
                        </Box>
                      ) : null}
                    </TableSortLabel>
                  ) : (
                    column.label
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          {isLoading ? (
            <TableBody>
              <TableRow>
                <TableCell colSpan={visibleColumns.length + (selectable ? 1 : 0)} align="center">
                  <Spinner />
                </TableCell>
              </TableRow>
            </TableBody>
          ) : paginatedData.length > 0 ? (
            <TableBody>
              {paginatedData.map((row, index) => {
                const isItemSelected = isSelected(row);
                const labelId = `enhanced-table-checkbox-${index}`;

                return (
                  <TableRow
                    hover
                    onClick={onRowClick ? handleClick(row) : undefined}
                    role={selectable ? "checkbox" : undefined}
                    aria-checked={isItemSelected}
                    tabIndex={-1}
                    key={row.id}
                    selected={isItemSelected}
                  >
                    {selectable && (
                      <TableCell padding="checkbox">
                        <Checkbox
                          color="primary"
                          checked={isItemSelected}
                          inputProps={{
                            'aria-labelledby': labelId,
                          }}
                          onClick={handleClick(row)}
                        />
                      </TableCell>
                    )}
                    {visibleColumns.map((column) => (
                      <TableCell
                        key={`${row.id}-${column.id}`}
                        align={column.align || 'left'}
                      >
                        {column.renderCell ? column.renderCell(row) : String(row[column.id as keyof T])}
                      </TableCell>
                    ))}
                  </TableRow>
                );
              })}
            </TableBody>
          ) : (
            <TableBody>
              <TableRow>
                <TableCell colSpan={visibleColumns.length + (selectable ? 1 : 0)} align="center">
                  <EmptyState title="No Data" message={emptyStateMessage} />
                </TableCell>
              </TableRow>
            </TableBody>
          )}
        </Table>
      </TableContainer>
      {pagination && (
        <Pagination
          totalItems={filteredData.length}
          itemsPerPage={pageSize}
          currentPage={page}
          onPageChange={handleChangePage}
          onItemsPerPageChange={handleChangePageSize}
          itemsPerPageOptions={pageSizeOptions}
        />
      )}
    </Paper>
  );
};

/**
 * Comparison function for sorting the table data
 * @param a - First object
 * @param b - Second object
 * @param orderBy - Property to sort by
 * @returns Comparison result
 */
function descendingComparator<T>(a: T, b: T, orderBy: keyof T): number {
  if (b[orderBy] < a[orderBy]) {
    return -1;
  }
  if (b[orderBy] > a[orderBy]) {
    return 1;
  }
  return 0;
}

export default DataTable;