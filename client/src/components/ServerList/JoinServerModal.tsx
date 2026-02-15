import { useState } from 'react';
import { useServerStore } from '../../stores/serverStore';

export default function JoinServerModal({ onClose }: { onClose: () => void }) {
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { joinServer, setActiveServer } = useServerStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code.trim()) return;
    setLoading(true);
    setError('');
    try {
      const server = await joinServer(code.trim());
      setActiveServer(server.id);
      onClose();
    } catch {
      setError('Invalid invite code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Join a Server</h2>
        <form onSubmit={handleSubmit}>
          <div className="modal-field">
            <label>Invite Code</label>
            <input
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Paste invite code"
              autoFocus
              required
            />
          </div>
          {error && <div className="auth-error">{error}</div>}
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Joining...' : 'Join'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
