import { Search, X } from 'lucide-react';
import styles from './FiltersBar.module.css';

interface FiltersBarProps {
  search?: string;
  onSearchChange?: (value: string) => void;
  searchPlaceholder?: string;
  filters?: React.ReactNode;
  actions?: React.ReactNode;
  activeFilterCount?: number;
  onClearFilters?: () => void;
}

export function FiltersBar({
  search,
  onSearchChange,
  searchPlaceholder = 'Search…',
  filters,
  actions,
  activeFilterCount = 0,
  onClearFilters,
}: FiltersBarProps) {
  return (
    <div className={styles.bar} role="search">
      {onSearchChange !== undefined && (
        <div className={styles.searchWrapper}>
          <span className={styles.searchIcon} aria-hidden="true">
            <Search size={16} strokeWidth={1.5} />
          </span>
          <input
            type="search"
            className={styles.searchInput}
            placeholder={searchPlaceholder}
            value={search ?? ''}
            onChange={(e) => onSearchChange(e.target.value)}
            aria-label={searchPlaceholder}
          />
        </div>
      )}

      {filters && <div className={styles.filters}>{filters}</div>}

      {activeFilterCount > 0 && onClearFilters && (
        <button
          className={styles.clearBtn}
          onClick={onClearFilters}
          aria-label={`Clear ${activeFilterCount} active filter${activeFilterCount > 1 ? 's' : ''}`}
        >
          <X size={14} strokeWidth={1.5} aria-hidden="true" />
          Clear filters
          <span className={styles.filterCount}>{activeFilterCount}</span>
        </button>
      )}

      {actions && <div className={styles.actions}>{actions}</div>}
    </div>
  );
}
