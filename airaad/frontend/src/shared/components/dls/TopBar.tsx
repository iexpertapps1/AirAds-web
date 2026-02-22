import { LogOut, User } from 'lucide-react';
import { useAuthStore } from '@/features/auth/store/authStore';
import { useUIStore } from '@/shared/store/uiStore';
import { queryClient } from '@/lib/queryClient';
import { apiClient } from '@/lib/axios';
import { Button } from '@/shared/components/dls/Button';
import styles from './TopBar.module.css';

interface TopBarProps {
  title?: string | undefined;
}

export function TopBar({ title }: TopBarProps) {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const addToast = useUIStore((s) => s.addToast);

  async function handleLogout() {
    try {
      await apiClient.post('/api/v1/auth/logout/');
    } catch {
      // best-effort — proceed even if server call fails
    } finally {
      logout();
      queryClient.clear();
      addToast({ type: 'info', message: 'You have been signed out.' });
      window.location.href = '/login';
    }
  }

  return (
    <header className={styles.topbar} role="banner">
      {title && <h1 className={styles.title}>{title}</h1>}
      <div className={styles.spacer} aria-hidden="true" />
      <div className={styles.actions}>
        {user && (
          <div className={styles.userInfo} aria-label={`Signed in as ${user.full_name ?? user.email}`}>
            <span className={styles.avatar} aria-hidden="true">
              <User size={16} strokeWidth={1.5} />
            </span>
            <span className={styles.userName}>{user.full_name ?? user.email}</span>
            <span className={styles.userRole}>{user.role}</span>
          </div>
        )}
        <Button
          variant="ghost"
          size="compact"
          leftIcon={<LogOut size={16} strokeWidth={1.5} />}
          onClick={handleLogout}
          aria-label="Sign out"
        >
          Sign out
        </Button>
      </div>
    </header>
  );
}
