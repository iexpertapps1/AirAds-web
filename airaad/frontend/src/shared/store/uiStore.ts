import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

interface UIState {
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark';
  toasts: Toast[];
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}

const timers = new Map<string, ReturnType<typeof setTimeout>>();

function readPersistedTheme(): 'light' | 'dark' {
  try {
    const stored = localStorage.getItem('airaad-theme');
    if (stored === 'dark' || stored === 'light') return stored;
  } catch {
    // ignore storage errors
  }
  return 'light';
}

export const useUIStore = create<UIState>()(
  immer((set) => ({
    sidebarCollapsed: false,
    theme: readPersistedTheme(),
    toasts: [],

    toggleSidebar: () => {
      set((state) => {
        state.sidebarCollapsed = !state.sidebarCollapsed;
      });
    },

    setTheme: (theme) => {
      set((state) => {
        state.theme = theme;
      });
      try {
        localStorage.setItem('airaad-theme', theme);
      } catch {
        // ignore storage errors
      }
    },

    addToast: (toast) => {
      const id = crypto.randomUUID();
      const duration = toast.duration ?? 4000;
      set((state) => {
        state.toasts.push({ ...toast, id, duration });
      });
      const timer = setTimeout(() => {
        set((state) => {
          state.toasts = state.toasts.filter((t) => t.id !== id);
        });
        timers.delete(id);
      }, duration);
      timers.set(id, timer);
    },

    removeToast: (id) => {
      const timer = timers.get(id);
      if (timer !== undefined) {
        clearTimeout(timer);
        timers.delete(id);
      }
      set((state) => {
        state.toasts = state.toasts.filter((t) => t.id !== id);
      });
    },
  })),
);
