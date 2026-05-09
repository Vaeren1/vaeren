import { create } from "zustand";

export interface AuthUser {
  pk: number;
  email: string;
  tenant_role?: string;
  mfa_enabled?: boolean;
}

interface AuthState {
  user: AuthUser | null;
  ephemeralToken: string | null;
  setUser: (u: AuthUser | null) => void;
  setMfaChallenge: (token: string) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  ephemeralToken: null,
  setUser: (u) => set({ user: u, ephemeralToken: null }),
  setMfaChallenge: (token) => set({ ephemeralToken: token, user: null }),
  clear: () => set({ user: null, ephemeralToken: null }),
}));
