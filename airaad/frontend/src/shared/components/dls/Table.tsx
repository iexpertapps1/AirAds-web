import { ChevronUp, ChevronDown } from 'lucide-react';
import { SkeletonTable } from '@/shared/components/dls/SkeletonTable';
import styles from './Table.module.css';

export interface ColumnDef<T> {
  key: string;
  header: string;
  render: (row: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
}

interface PaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
  onPageSizeChange?: ((pageSize: number) => void) | undefined;
  pageSizeOptions?: number[];
}

interface SortProps {
  key: string;
  direction: 'asc' | 'desc';
  onSort: (key: string, direction: 'asc' | 'desc') => void;
}

interface TableProps<T> {
  'aria-label': string;
  columns: ColumnDef<T>[];
  data: T[];
  isLoading: boolean;
  isEmpty: boolean;
  emptyState: React.ReactNode;
  pagination?: PaginationProps | undefined;
  onPageSizeChange?: ((pageSize: number) => void) | undefined;
  sort?: SortProps | undefined;
  selectable?: boolean | undefined;
  selectedIds?: string[] | undefined;
  onSelectionChange?: ((ids: string[]) => void) | undefined;
  getRowId?: ((row: T) => string) | undefined;
  stickyHeader?: boolean | undefined;
  onRowClick?: ((row: T) => void) | undefined;
}

function getDefaultRowId<T>(row: T): string {
  if (row !== null && typeof row === 'object' && 'id' in row) {
    return String((row as Record<string, unknown>)['id']);
  }
  return '';
}

export function Table<T>({
  'aria-label': ariaLabel,
  columns,
  data,
  isLoading,
  isEmpty,
  emptyState,
  pagination,
  sort,
  selectable,
  selectedIds = [],
  onSelectionChange,
  getRowId = getDefaultRowId,
  stickyHeader,
  onRowClick,
}: TableProps<T>) {
  const autoSticky = stickyHeader ?? data.length > 10;

  if (isLoading) {
    return <SkeletonTable rows={5} columns={columns.length + (selectable ? 1 : 0)} />;
  }

  if (isEmpty) {
    return <>{emptyState}</>;
  }

  const allIds = data.map(getRowId);
  const allSelected = allIds.length > 0 && allIds.every((id) => selectedIds.includes(id));
  const someSelected = allIds.some((id) => selectedIds.includes(id)) && !allSelected;

  function handleSelectAll(checked: boolean) {
    if (!onSelectionChange) return;
    onSelectionChange(checked ? allIds : []);
  }

  function handleSelectRow(id: string, checked: boolean) {
    if (!onSelectionChange) return;
    onSelectionChange(
      checked ? [...selectedIds, id] : selectedIds.filter((s) => s !== id),
    );
  }

  function handleSortClick(key: string) {
    if (!sort) return;
    const newDir = sort.key === key && sort.direction === 'asc' ? 'desc' : 'asc';
    sort.onSort(key, newDir);
  }

  const totalPages = pagination ? Math.ceil(pagination.total / pagination.pageSize) : 1;
  const pageSizeOptions = pagination?.pageSizeOptions ?? [25, 50, 100];

  const startRow = pagination ? (pagination.page - 1) * pagination.pageSize + 1 : 1;
  const endRow = pagination ? Math.min(pagination.page * pagination.pageSize, pagination.total) : data.length;
  const total = pagination?.total ?? data.length;

  return (
    <div className={styles.wrapper}>
      <div className={styles.tableContainer}>
        <table
          className={[styles.table, autoSticky ? styles.stickyHeader : ''].join(' ')}
          aria-label={ariaLabel}
        >
          <thead className={styles.thead}>
            <tr>
              {selectable && (
                <th className={styles.checkboxTh} scope="col">
                  <input
                    type="checkbox"
                    aria-label="Select all rows on this page"
                    checked={allSelected}
                    ref={(el) => {
                      if (el) el.indeterminate = someSelected;
                    }}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className={styles.checkbox}
                  />
                </th>
              )}
              {columns.map((col) => {
                const isSorted = sort?.key === col.key;
                const ariaSort = isSorted
                  ? sort?.direction === 'asc'
                    ? 'ascending'
                    : 'descending'
                  : col.sortable
                    ? 'none'
                    : undefined;
                return (
                  <th
                    key={col.key}
                    scope="col"
                    aria-sort={ariaSort}
                    className={[styles.th, col.sortable ? styles.sortable : '', col.width ? styles.thFixedWidth : ''].join(' ')}
                    style={col.width ? ({ ['--col-width' as string]: col.width } as React.CSSProperties) : undefined}
                    onClick={col.sortable ? () => handleSortClick(col.key) : undefined}
                  >
                    <span className={styles.thContent}>
                      {col.header}
                      {col.sortable && (
                        <span className={styles.sortIcon} aria-hidden="true">
                          {isSorted && sort?.direction === 'asc' ? (
                            <ChevronUp size={14} strokeWidth={1.5} />
                          ) : isSorted && sort?.direction === 'desc' ? (
                            <ChevronDown size={14} strokeWidth={1.5} />
                          ) : (
                            <ChevronDown size={14} strokeWidth={1.5} className={styles.sortIconInactive} />
                          )}
                        </span>
                      )}
                    </span>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {data.map((row) => {
              const id = getRowId(row);
              const isSelected = selectedIds.includes(id);
              return (
                <tr
                  key={id}
                  className={[
                    styles.tr,
                    isSelected ? styles.trSelected : '',
                    onRowClick ? styles.trClickable : '',
                  ].join(' ')}
                  onClick={onRowClick ? () => onRowClick(row) : undefined}
                  onKeyDown={
                    onRowClick
                      ? (e) => {
                          if (e.key === 'Enter') onRowClick(row);
                        }
                      : undefined
                  }
                  tabIndex={onRowClick ? 0 : undefined}
                  aria-selected={selectable ? isSelected : undefined}
                >
                  {selectable && (
                    <td className={styles.checkboxTd} onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        aria-label={`Select row ${id}`}
                        checked={isSelected}
                        onChange={(e) => handleSelectRow(id, e.target.checked)}
                        className={styles.checkbox}
                      />
                    </td>
                  )}
                  {columns.map((col) => (
                    <td key={col.key} className={styles.td}>
                      {col.render(row)}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {pagination && (
        <div className={styles.pagination}>
          <span className={styles.rowCount}>
            Showing {startRow}–{endRow} of {total.toLocaleString()}
          </span>
          <div className={styles.paginationControls}>
            <select
              aria-label="Rows per page"
              value={pagination.pageSize}
              onChange={(e) => {
                const newSize = parseInt(e.target.value, 10);
                if (pagination.onPageSizeChange) {
                  pagination.onPageSizeChange(newSize);
                }
                pagination.onPageChange(1);
              }}
              className={styles.pageSizeSelect}
            >
              {pageSizeOptions.map((opt) => (
                <option key={opt} value={opt}>
                  {opt} per page
                </option>
              ))}
            </select>
            <button
              className={styles.pageBtn}
              onClick={() => pagination.onPageChange(pagination.page - 1)}
              disabled={pagination.page <= 1}
              aria-label="Previous page"
            >
              ‹
            </button>
            {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
              const pageNum = i + 1;
              return (
                <button
                  key={pageNum}
                  className={[styles.pageBtn, pagination.page === pageNum ? styles.pageBtnActive : ''].join(' ')}
                  onClick={() => pagination.onPageChange(pageNum)}
                  aria-label={`Page ${pageNum}`}
                  aria-current={pagination.page === pageNum ? 'page' : undefined}
                >
                  {pageNum}
                </button>
              );
            })}
            <button
              className={styles.pageBtn}
              onClick={() => pagination.onPageChange(pagination.page + 1)}
              disabled={pagination.page >= totalPages}
              aria-label="Next page"
            >
              ›
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
