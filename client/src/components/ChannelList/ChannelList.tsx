import { useEffect, useState } from 'react';
import { useServerStore } from '../../stores/serverStore';
import { useAuthStore } from '../../stores/authStore';

export default function ChannelList() {
  const { servers, channels, activeServerId, activeChannelId, fetchChannels, setActiveChannel, createChannel } = useServerStore();
  const { username, logout } = useAuthStore();
  const [showNewChannel, setShowNewChannel] = useState(false);
  const [newChannelName, setNewChannelName] = useState('');
  const [copied, setCopied] = useState(false);

  const activeServer = servers.find((s) => s.id === activeServerId);

  useEffect(() => {
    if (activeServerId) {
      fetchChannels(activeServerId);
    }
  }, [activeServerId, fetchChannels]);

  const handleCreateChannel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeServerId || !newChannelName.trim()) return;
    await createChannel(activeServerId, newChannelName.trim());
    setNewChannelName('');
    setShowNewChannel(false);
  };

  const copyInvite = () => {
    if (activeServer) {
      navigator.clipboard.writeText(activeServer.invite_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }
  };

  if (!activeServer) {
    return (
      <div className="channel-sidebar">
        <div className="channel-header">Whisper</div>
        <div className="chat-empty" style={{ padding: '20px', fontSize: '13px' }}>
          Select or create a server
        </div>
        <div className="channel-user-panel">
          <div className="user-avatar">{username?.[0]?.toUpperCase()}</div>
          <div className="user-info">
            <div className="username">{username}</div>
            <div className="status">online</div>
          </div>
          <button className="icon-btn" onClick={logout} title="Sign out">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" />
            </svg>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="channel-sidebar">
      <div className="channel-header">
        <span>{activeServer.name}</span>
        <div className="channel-header-actions">
          <button className="icon-btn" onClick={copyInvite} title="Copy invite code">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {copied
                ? <polyline points="20 6 9 17 4 12" />
                : <><rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></>
              }
            </svg>
          </button>
          <button className="icon-btn" onClick={() => setShowNewChannel(true)} title="Create channel">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
            </svg>
          </button>
        </div>
      </div>

      <div className="channel-list">
        {channels.map((ch) => (
          <button
            key={ch.id}
            className={`channel-item ${activeChannelId === ch.id ? 'active' : ''}`}
            onClick={() => setActiveChannel(ch.id)}
          >
            <span className="hash">{ch.type === 'voice' ? '🔊' : '#'}</span>
            {ch.name}
          </button>
        ))}
      </div>

      {showNewChannel && (
        <div style={{ padding: '8px' }}>
          <form onSubmit={handleCreateChannel} style={{ display: 'flex', gap: '4px' }}>
            <input
              value={newChannelName}
              onChange={(e) => setNewChannelName(e.target.value)}
              placeholder="channel-name"
              autoFocus
              style={{
                flex: 1,
                padding: '6px 10px',
                background: 'var(--bg-void)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-primary)',
                fontSize: '13px',
                outline: 'none',
              }}
            />
          </form>
        </div>
      )}

      <div className="channel-user-panel">
        <div className="user-avatar">{username?.[0]?.toUpperCase()}</div>
        <div className="user-info">
          <div className="username">{username}</div>
          <div className="status">online</div>
        </div>
        <button className="icon-btn" onClick={logout} title="Sign out">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" />
          </svg>
        </button>
      </div>
    </div>
  );
}
