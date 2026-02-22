import { Link } from 'react-router-dom';
import styles from './PageHeader.module.css';

interface PageHeaderProps {
  heading: string;
  subheading?: string | undefined;
  actions?: React.ReactNode;
  breadcrumbs?: Array<{ label: string; href?: string | undefined }> | undefined;
}

export function PageHeader({ heading, subheading, actions, breadcrumbs }: PageHeaderProps) {
  return (
    <div className={styles.header}>
      {breadcrumbs && breadcrumbs.length > 0 && (
        <nav aria-label="Breadcrumb" className={styles.breadcrumbs}>
          <ol className={styles.breadcrumbList}>
            {breadcrumbs.map((crumb, i) => (
              <li key={i} className={styles.breadcrumbItem}>
                {i > 0 && <span className={styles.separator} aria-hidden="true">/</span>}
                {crumb.href ? (
                  <Link to={crumb.href} className={styles.breadcrumbLink}>
                    {crumb.label}
                  </Link>
                ) : (
                  <span aria-current="page">{crumb.label}</span>
                )}
              </li>
            ))}
          </ol>
        </nav>
      )}
      <div className={styles.row}>
        <div>
          <h1 className={styles.heading}>{heading}</h1>
          {subheading && <p className={styles.subheading}>{subheading}</p>}
        </div>
        {actions && <div className={styles.actions}>{actions}</div>}
      </div>
    </div>
  );
}
