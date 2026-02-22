import { createPortal } from 'react-dom';
import { X, CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react';
import type { Toast as ToastType } from '@/shared/store/uiStore';
import { useUIStore } from '@/shared/store/uiStore';
import styles from './Toast.module.css';

const ICONS: Record<ToastType['type'], React.ReactNode> = {
  success: <CheckCircle size={18} strokeWidth={1.5} />,
  warning: <AlertTriangle size={18} strokeWidth={1.5} />,
  error: <XCircle size={18} strokeWidth={1.5} />,
  info: <Info size={18} strokeWidth={1.5} />,
};

function ToastItem({ toast }: { toast: ToastType }) {
  const removeToast = useUIStore((s) => s.removeToast);

  return (
    <div
      className={[styles.toast, styles[toast.type]].join(' ')}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <span className={styles.icon} aria-hidden="true">
        {ICONS[toast.type]}
      </span>
      <span className={styles.message}>{toast.message}</span>
      <button
        className={styles.close}
        onClick={() => removeToast(toast.id)}
        aria-label="Dismiss notification"
      >
        <X size={16} strokeWidth={1.5} />
      </button>
    </div>
  );
}

export function ToastProvider() {
  const toasts = useUIStore((s) => s.toasts);

  return createPortal(
    <div
      className={styles.container}
      aria-label="Notifications"
      aria-live="polite"
      aria-relevant="additions removals"
    >
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} />
      ))}
    </div>,
    document.body,
  );
}
