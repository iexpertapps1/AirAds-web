import { forwardRef } from 'react';
import styles from './Checkbox.module.css';

interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'id' | 'type'> {
  label: string;
  id: string;
  error?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(function Checkbox(
  { label, id, error, className, ...rest },
  ref,
) {
  return (
    <div className={styles.wrapper}>
      <label className={styles.label} htmlFor={id}>
        <input
          ref={ref}
          type="checkbox"
          id={id}
          className={[styles.checkbox, className].filter(Boolean).join(' ')}
          {...rest}
        />
        <span className={styles.labelText}>{label}</span>
      </label>
      {error && (
        <span className={styles.error} role="alert">
          {error}
        </span>
      )}
    </div>
  );
});
