import { create } from 'zustand';
import api from '../api/client';

export interface Message {
  id: string;
  channel_id?: string;
  conversation_id?: string;
  sender_id: string;
  sender_username: string;
  content: string;
  created_at: string;
}

interface MessageState {
  messages: Message[];
  fetchMessages: (channelId: string) => Promise<void>;
  addMessage: (msg: Message) => void;
  clearMessages: () => void;
}

export const useMessageStore = create<MessageState>((set) => ({
  messages: [],

  fetchMessages: async (channelId: string) => {
    const { data } = await api.get(`/channels/${channelId}/messages`);
    set({ messages: data });
  },

  addMessage: (msg: Message) => {
    set((s) => {
      if (s.messages.some((m) => m.id === msg.id)) return s;
      return { messages: [...s.messages, msg] };
    });
  },

  clearMessages: () => set({ messages: [] }),
}));
