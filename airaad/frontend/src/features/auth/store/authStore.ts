import { create } from 'zustand';
import { subscribeWithSelector, persist, createJSONStorage } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

export type Role =
  | 'SUPER_ADMIN'
  | 'CITY_MANAGER'
  | 'DATA_ENTRY'
  | 'QA_REVIEWER'
  | 'FIELD_AGENT'
  | 'ANALYST'
  | 'SUPPORT';

export interface AuthUser {
  id: string;
  email: string;
  role: Role;
  full_name?: string;
}

interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  refreshToken: string | null;
  login: (tokens: { access: string; refresh: string }, user: AuthUser) => void;
  logout: () => void;
  setAccessToken: (token: string) => void;
}

export const useAuthStore = create<AuthState>()(
  subscribeWithSelector(
    persist(
      immer((set) => ({
        user: null,
        accessToken: null,
        refreshToken: null,

        login: (tokens, user) => {
          set((state) => {
            state.user = user;
            state.accessToken = tokens.access;
            state.refreshToken = tokens.refresh;
          });
        },

        logout: () => {
          set((state) => {
            state.user = null;
            state.accessToken = null;
            state.refreshToken = null;
          });
        },

        setAccessToken: (token) => {
          set((state) => {
            state.accessToken = token;
          });
        },
      })),
      { name: 'airaad-auth', storage: createJSONStorage(() => sessionStorage) },
    ),
  ),
);
