import { create } from 'zustand';
import api from '../api/client';

export interface Server {
  id: string;
  name: string;
  owner_id: string;
  invite_code: string;
}

export interface Channel {
  id: string;
  server_id: string;
  name: string;
  type: string;
}

interface ServerState {
  servers: Server[];
  channels: Channel[];
  activeServerId: string | null;
  activeChannelId: string | null;

  fetchServers: () => Promise<void>;
  fetchChannels: (serverId: string) => Promise<void>;
  createServer: (name: string) => Promise<Server>;
  joinServer: (inviteCode: string) => Promise<Server>;
  createChannel: (serverId: string, name: string, type?: string) => Promise<void>;
  setActiveServer: (id: string | null) => void;
  setActiveChannel: (id: string | null) => void;
}

export const useServerStore = create<ServerState>((set, get) => ({
  servers: [],
  channels: [],
  activeServerId: null,
  activeChannelId: null,

  fetchServers: async () => {
    const { data } = await api.get('/servers');
    set({ servers: data });
  },

  fetchChannels: async (serverId: string) => {
    const { data } = await api.get(`/channels/by-server/${serverId}`);
    set({ channels: data });
  },

  createServer: async (name: string) => {
    const { data } = await api.post('/servers', { name });
    set((s) => ({ servers: [...s.servers, data] }));
    return data;
  },

  joinServer: async (inviteCode: string) => {
    const { data } = await api.post('/servers/join', { invite_code: inviteCode });
    const exists = get().servers.find((s) => s.id === data.id);
    if (!exists) set((s) => ({ servers: [...s.servers, data] }));
    return data;
  },

  createChannel: async (serverId: string, name: string, type = 'text') => {
    const { data } = await api.post('/channels', { server_id: serverId, name, type });
    set((s) => ({ channels: [...s.channels, data] }));
  },

  setActiveServer: (id) => set({ activeServerId: id, activeChannelId: null, channels: [] }),
  setActiveChannel: (id) => set({ activeChannelId: id }),
}));
