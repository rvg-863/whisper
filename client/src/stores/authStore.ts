import { create } from 'zustand';
import api from '../api/client';

interface AuthState {
  token: string | null;
  userId: string | null;
  username: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
  hydrate: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  userId: null,
  username: null,
  isAuthenticated: false,

  hydrate: () => {
    const token = localStorage.getItem('whisper_token');
    const user = localStorage.getItem('whisper_user');
    if (token && user) {
      const { userId, username } = JSON.parse(user);
      set({ token, userId, username, isAuthenticated: true });
    }
  },

  login: async (username: string, password: string) => {
    const { data } = await api.post('/auth/login', { username, password });
    localStorage.setItem('whisper_token', data.token);
    localStorage.setItem('whisper_user', JSON.stringify({ userId: data.user_id, username: data.username }));
    set({ token: data.token, userId: data.user_id, username: data.username, isAuthenticated: true });
  },

  register: async (username: string, password: string) => {
    const { data } = await api.post('/auth/register', { username, password });
    localStorage.setItem('whisper_token', data.token);
    localStorage.setItem('whisper_user', JSON.stringify({ userId: data.user_id, username: data.username }));
    set({ token: data.token, userId: data.user_id, username: data.username, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('whisper_token');
    localStorage.removeItem('whisper_user');
    set({ token: null, userId: null, username: null, isAuthenticated: false });
  },
}));
