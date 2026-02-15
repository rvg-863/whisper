import { useEffect, useState } from 'react';
import { useServerStore } from '../../stores/serverStore';
import type { Server } from '../../stores/serverStore';
import CreateServerModal from './CreateServerModal';
import JoinServerModal from './JoinServerModal';

export default function ServerList() {
  const { servers, activeServerId, fetchServers, setActiveServer } = useServerStore();
  const [showCreate, setShowCreate] = useState(false);
  const [showJoin, setShowJoin] = useState(false);

  useEffect(() => {
    fetchServers();
  }, [fetchServers]);

  const getInitials = (name: string) =>
    name.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase();

  return (
    <>
      <div className="server-sidebar">
        {servers.map((s: Server) => (
          <button
            key={s.id}
            className={`server-icon ${activeServerId === s.id ? 'active' : ''}`}
            onClick={() => setActiveServer(s.id)}
            title={s.name}
          >
            {getInitials(s.name)}
          </button>
        ))}
        <div className="server-divider" />
        <button className="server-icon add-server" onClick={() => setShowCreate(true)} title="Create Server">
          +
        </button>
        <button className="server-icon add-server" onClick={() => setShowJoin(true)} title="Join Server" style={{ fontSize: '16px' }}>
          ↗
        </button>
      </div>
      {showCreate && <CreateServerModal onClose={() => setShowCreate(false)} />}
      {showJoin && <JoinServerModal onClose={() => setShowJoin(false)} />}
    </>
  );
}
