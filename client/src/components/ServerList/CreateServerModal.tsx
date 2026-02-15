import { useState } from 'react';
import { useServerStore } from '../../stores/serverStore';

export default function CreateServerModal({ onClose }: { onClose: () => void }) {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const { createServer, setActiveServer } = useServerStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setLoading(true);
    try {
      const server = await createServer(name.trim());
      setActiveServer(server.id);
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Create a Server</h2>
        <form onSubmit={handleSubmit}>
          <div className="modal-field">
            <label>Server Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="My Server"
              autoFocus
              required
              maxLength={64}
            />
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
