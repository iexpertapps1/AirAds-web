import styles from './SkeletonTable.module.css';

interface SkeletonTableProps {
  rows?: number;
  columns?: number;
  showHeader?: boolean;
}

const COLUMN_WIDTHS = ['60%', '40%', '80%', '30%', '50%'];

export function SkeletonTable({ rows = 5, columns = 5, showHeader = true }: SkeletonTableProps) {
  return (
    <div
      className={styles.wrapper}
      aria-label="Loading data"
      aria-busy="true"
      role="status"
    >
      <table className={styles.table}>
        {showHeader && (
          <thead>
            <tr>
              {Array.from({ length: columns }).map((_, i) => (
                <th key={i} className={styles.th}>
                  <span
                    className={styles.cell}
                    style={{ ['--cell-width' as string]: COLUMN_WIDTHS[i % COLUMN_WIDTHS.length] } as React.CSSProperties}
                  />
                </th>
              ))}
            </tr>
          </thead>
        )}
        <tbody>
          {Array.from({ length: rows }).map((_, rowIdx) => (
            <tr key={rowIdx} className={styles.row}>
              {Array.from({ length: columns }).map((_, colIdx) => (
                <td key={colIdx} className={styles.td}>
                  <span
                    className={styles.cell}
                    style={{ ['--cell-width' as string]: COLUMN_WIDTHS[colIdx % COLUMN_WIDTHS.length] } as React.CSSProperties}
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
