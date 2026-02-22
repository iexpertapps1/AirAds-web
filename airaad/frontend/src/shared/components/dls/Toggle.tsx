import styles from './Toggle.module.css';

interface ToggleProps {
  id: string;
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}

export function Toggle({ id, label, checked, onChange, disabled }: ToggleProps) {
  return (
    <label className={styles.wrapper} htmlFor={id}>
      <span className={styles.labelText}>{label}</span>
      <span className={styles.track}>
        <input
          type="checkbox"
          id={id}
          role="switch"
          aria-checked={checked}
          checked={checked}
          disabled={disabled}
          onChange={(e) => onChange(e.target.checked)}
          className={styles.input}
        />
        <span className={[styles.thumb, checked ? styles.thumbOn : ''].join(' ')} aria-hidden="true" />
      </span>
    </label>
  );
}
