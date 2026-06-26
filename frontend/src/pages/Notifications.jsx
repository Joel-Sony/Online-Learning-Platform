import { useState, useEffect } from 'react';
import api from '../api';

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      const res = await api.get('/notifications/');
      setNotifications(res.data);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  const markRead = async (id) => {
    try {
      await api.post(`/notifications/${id}/mark_read/`);
      setNotifications(notifications.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch (err) { console.error(err); }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'left' }}>
      <h1>Notifications</h1>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {notifications.map(n => (
          <div key={n.id} style={{ 
            padding: '1.5rem', 
            border: '1px solid var(--border)', 
            borderRadius: '8px',
            backgroundColor: n.is_read ? 'transparent' : 'var(--accent-bg)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div>
              <h3 style={{ margin: '0 0 0.5rem 0' }}>{n.title}</h3>
              <p style={{ margin: 0 }}>{n.message}</p>
              <span style={{ fontSize: '0.8rem', color: 'gray' }}>{new Date(n.created_at).toLocaleString()}</span>
            </div>
            {!n.is_read && (
              <button onClick={() => markRead(n.id)} style={{ padding: '0.5rem 1rem' }}>Mark as Read</button>
            )}
          </div>
        ))}
        {notifications.length === 0 && <p>No notifications found.</p>}
      </div>
    </div>
  );
}

export default Notifications;
