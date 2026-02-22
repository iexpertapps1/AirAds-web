import { forwardRef } from 'react';
import { AlertCircle } from 'lucide-react';
import styles from './Input.module.css';

interface BaseInputProps {
  label: string;
  error?: string | undefined;
  hint?: string | undefined;
  required?: boolean | undefined;
  disabled?: boolean | undefined;
  id: string;
}

export interface InputProps extends BaseInputProps, Omit<React.InputHTMLAttributes<HTMLInputElement>, 'id' | 'required' | 'disabled'> {}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, error, hint, required, disabled, id, className, ...rest },
  ref,
) {
  const errorId = `${id}-error`;
  const hintId = `${id}-hint`;
  const describedBy = [error ? errorId : null, hint ? hintId : null].filter(Boolean).join(' ') || undefined;

  return (
    <div className={styles.field}>
      <label htmlFor={id} className={styles.label}>
        {label}
        {required && <span className={styles.required} aria-hidden="true"> *</span>}
      </label>
      <input
        ref={ref}
        id={id}
        required={required}
        disabled={disabled}
        aria-describedby={describedBy}
        aria-invalid={error ? 'true' : undefined}
        className={[styles.input, error ? styles.hasError : '', className].filter(Boolean).join(' ')}
        {...rest}
      />
      {hint && !error && (
        <span id={hintId} className={styles.hint}>
          {hint}
        </span>
      )}
      {error && (
        <span id={errorId} className={styles.error} role="alert">
          <AlertCircle size={12} strokeWidth={1.5} aria-hidden="true" />
          {error}
        </span>
      )}
    </div>
  );
});
