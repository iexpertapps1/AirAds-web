import { forwardRef } from 'react';
import styles from './Button.module.css';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant: 'primary' | 'secondary' | 'destructive' | 'ghost';
  size?: 'compact' | 'default' | 'large';
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  {
    variant,
    size = 'default',
    loading = false,
    leftIcon,
    rightIcon,
    children,
    disabled,
    className,
    ...rest
  },
  ref,
) {
  const isDisabled = disabled ?? loading;

  return (
    <button
      ref={ref}
      {...rest}
      disabled={isDisabled}
      aria-busy={loading ? 'true' : undefined}
      className={[styles.btn, styles[variant], styles[size], className].filter(Boolean).join(' ')}
    >
      {loading ? (
        <span className={styles.spinner} aria-hidden="true" />
      ) : (
        <>
          {leftIcon && (
            <span className={styles.iconLeft} aria-hidden="true">
              {leftIcon}
            </span>
          )}
          {children}
          {rightIcon && (
            <span className={styles.iconRight} aria-hidden="true">
              {rightIcon}
            </span>
          )}
        </>
      )}
    </button>
  );
});
