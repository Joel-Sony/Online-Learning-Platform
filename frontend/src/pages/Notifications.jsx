import { useState, useEffect } from 'react';
import api from '../api';

function formatTime(dateString) {
  const date = new Date(dateString);
  const diff = Math.floor((Date.now() - date) / 1000);
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return date.toLocaleDateString();
}

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchNotifications(); }, []);

  const fetchNotifications = async () => {
    try {
      const res = await api.get('/notifications/');
      setNotifications(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const markRead = async (id) => {
    try {
      await api.post(`/notifications/${id}/read/`);
      setNotifications(prev => prev.map(n => (n.id === id ? { ...n, is_read: true } : n)));
    } catch (err) { console.error(err); }
  };

  const markAllRead = async () => {
    try {
      await api.post('/notifications/read-all/');
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (err) { console.error(err); }
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="page" style={{ maxWidth: '760px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 'var(--sp-4)' }}>
        <div>
          <span className="label">Inbox</span>
          <h1 style={{ marginTop: '4px' }}>Notifications</h1>
        </div>
        {unreadCount > 0 && (
          <button className="btn btn-secondary btn-sm" onClick={markAllRead}>
            Mark all read ({unreadCount})
          </button>
        )}
      </div>

      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-2)' }}>
          {[0, 1, 2].map(i => (
            <div key={i} className="skeleton" style={{ height: '76px', borderRadius: 'var(--radius-lg)' }} />
          ))}
        </div>
      ) : notifications.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 'var(--sp-8)', color: 'var(--text-tertiary)' }}>
          You have no notifications yet.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-2)' }}>
          {notifications.map(n => (
            <div
              key={n.id}
              className="card"
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: 'var(--sp-3)',
                padding: 'var(--sp-3)',
                background: n.is_read ? 'var(--bg)' : 'var(--accent-light)',
                borderColor: n.is_read ? 'var(--border)' : 'transparent',
              }}
            >
              <div style={{ minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--sp-1)', marginBottom: '6px' }}>
                  <span className="badge badge-accent" style={{ fontSize: '0.68rem' }}>
                    {n.type?.replace(/_/g, ' ')}
                  </span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)' }}>
                    {formatTime(n.created_at)}
                  </span>
                </div>
                <p style={{ margin: 0, color: n.is_read ? 'var(--text-secondary)' : 'var(--text-primary)' }}>
                  {n.message}
                </p>
              </div>
              {!n.is_read && (
                <button className="btn btn-ghost btn-sm" style={{ flexShrink: 0 }} onClick={() => markRead(n.id)}>
                  Mark read
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Notifications;
