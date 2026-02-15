import { useEffect, useRef, useState } from 'react';
import { useServerStore } from '../../stores/serverStore';
import { useMessageStore } from '../../stores/messageStore';
import type { Message } from '../../stores/messageStore';
import { useAuthStore } from '../../stores/authStore';
import { useWebSocket } from '../../hooks/useWebSocket';

export default function ChatView() {
  const { activeChannelId, channels } = useServerStore();
  const { messages, fetchMessages, addMessage, clearMessages } = useMessageStore();
  const userId = useAuthStore((s) => s.userId);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const prevChannelRef = useRef<string | null>(null);

  const { send, connected } = useWebSocket((data) => {
    if (data.type === 'message' && data.channel_id === activeChannelId) {
      addMessage(data as unknown as Message);
    }
  });

  const activeChannel = channels.find((c) => c.id === activeChannelId);

  // Join/leave channel rooms and fetch messages
  useEffect(() => {
    if (prevChannelRef.current) {
      send({ type: 'leave_channel', channel_id: prevChannelRef.current });
    }
    if (activeChannelId) {
      clearMessages();
      fetchMessages(activeChannelId);
      send({ type: 'join_channel', channel_id: activeChannelId });
      prevChannelRef.current = activeChannelId;
    }
    return () => {
      if (prevChannelRef.current) {
        send({ type: 'leave_channel', channel_id: prevChannelRef.current });
      }
    };
  }, [activeChannelId]); // eslint-disable-line react-hooks/exhaustive-deps

  // Auto-scroll on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !activeChannelId) return;
    send({ type: 'message', channel_id: activeChannelId, content: input.trim() });
    setInput('');
  };

  if (!activeChannelId || !activeChannel) {
    return (
      <div className="chat-area">
        <div className="chat-empty">Select a channel to start chatting</div>
      </div>
    );
  }

  const formatTime = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-area">
      <div className="chat-header">
        <span className="hash">#</span>
        <span className="channel-name">{activeChannel.name}</span>
        {!connected && (
          <span style={{ marginLeft: 'auto', fontSize: '11px', color: 'var(--danger)', fontFamily: 'var(--font-mono)' }}>
            reconnecting...
          </span>
        )}
      </div>

      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className="message-row">
            <div className="message-avatar">
              {msg.sender_username[0].toUpperCase()}
            </div>
            <div className="message-body">
              <div className="message-header">
                <span className="message-username" style={msg.sender_id === userId ? { color: 'var(--accent)' } : undefined}>
                  {msg.sender_username}
                </span>
                <span className="message-time">{formatTime(msg.created_at)}</span>
              </div>
              <div className="message-content">{msg.content}</div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <form className="chat-input-wrapper" onSubmit={handleSend}>
          <input
            className="chat-input"
            placeholder={`Message #${activeChannel.name}`}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            autoFocus
          />
          <button className="chat-send-btn" type="submit" disabled={!input.trim()}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}
