import { Button } from '@/shared/components/dls/Button';
import styles from './EmptyState.module.css';

interface EmptyStateProps {
  illustration?: React.ReactNode;
  heading: string;
  subheading: string;
  ctaLabel?: string;
  onCta?: () => void;
  ctaDisabled?: boolean;
}

export function EmptyState({
  illustration,
  heading,
  subheading,
  ctaLabel,
  onCta,
  ctaDisabled,
}: EmptyStateProps) {
  return (
    <div className={styles.wrapper}>
      {illustration && (
        <span className={styles.illustration} aria-hidden="true">
          {illustration}
        </span>
      )}
      <h3 className={styles.heading}>{heading}</h3>
      <p className={styles.subheading}>{subheading}</p>
      {ctaLabel && onCta && (
        <Button variant="primary" onClick={onCta} disabled={ctaDisabled}>
          {ctaLabel}
        </Button>
      )}
    </div>
  );
}
