import { useAuthStore } from '@/features/auth/store/authStore';
import type { Role } from '@/features/auth/store/authStore';

export function usePermission(allowedRoles: Role[]): boolean {
  return useAuthStore((s) => s.user !== null && allowedRoles.includes(s.user.role));
}
