import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useNotifications } from '../hooks/useNotifications';

function NotificationDropdown() {
  const { notifications, unreadCount, markAsRead, markAllRead } = useNotifications();
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div style={{ position: 'relative' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '34px', height: '34px',
          background: isOpen ? 'var(--surface)' : 'transparent',
          border: '1px solid transparent',
          borderRadius: 'var(--radius-sm)',
          cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'var(--text-secondary)',
          position: 'relative',
          transition: 'var(--transition-fast)',
        }}
        onMouseEnter={e => e.currentTarget.style.background = 'var(--surface)'}
        onMouseLeave={e => { if (!isOpen) e.currentTarget.style.background = 'transparent'; }}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
        </svg>
        {unreadCount > 0 && (
          <span style={{
            position: 'absolute', top: '3px', right: '3px',
            width: '8px', height: '8px',
            background: 'var(--accent)', borderRadius: '50%',
            border: '2px solid var(--bg)',
          }} />
        )}
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            style={{ position: 'fixed', inset: 0, zIndex: 150 }}
            onClick={() => setIsOpen(false)}
          />
          <div className="notification-dropdown" style={{ zIndex: 200 }}>
            {/* Header */}
            <div style={{
              padding: '14px 18px',
              borderBottom: '1px solid var(--border)',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              position: 'sticky', top: 0, background: 'var(--bg)',
            }}>
              <span style={{ fontWeight: '600', fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                Notifications {unreadCount > 0 && (
                  <span style={{ background: 'var(--accent)', color: '#fff', borderRadius: '20px', padding: '1px 7px', fontSize: '0.7rem', marginLeft: '6px' }}>
                    {unreadCount}
                  </span>
                )}
              </span>
              {unreadCount > 0 && (
                <button onClick={markAllRead} style={{
                  background: 'none', border: 'none', cursor: 'pointer',
                  fontSize: '0.78rem', color: 'var(--accent)', fontFamily: 'var(--font-body)',
                }}>
                  Mark all read
                </button>
              )}
            </div>

            {/* Items */}
            {notifications.length === 0 ? (
              <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--text-tertiary)', fontSize: '0.875rem' }}>
                No notifications yet
              </div>
            ) : (
              notifications.slice(0, 10).map(n => (
                <div
                  key={n.id}
                  onClick={() => {
                    if (!n.is_read) markAsRead(n.id);
                    if (n.type === 'ANNOUNCEMENT' && n.course) {
                      setIsOpen(false);
                      navigate(`/courses/${n.course}/learn?tab=announcements`);
                    }
                  }}
                  className={`notification-item ${!n.is_read ? 'unread' : ''}`}
                  style={{ position: 'relative' }}
                >
                  {!n.is_read && (
                    <span style={{
                      position: 'absolute', left: 0, top: 0, bottom: 0,
                      width: '3px', background: 'var(--accent)', borderRadius: '0 2px 2px 0'
                    }} />
                  )}
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', alignItems: 'center', paddingLeft: n.is_read ? 0 : '8px' }}>
                    <span className="badge badge-accent" style={{ fontSize: '0.68rem' }}>
                      {n.type?.replace(/_/g, ' ')}
                    </span>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)' }}>{formatTime(n.created_at)}</span>
                  </div>
                  <p style={{
                    fontSize: '0.85rem',
                    color: n.is_read ? 'var(--text-secondary)' : 'var(--text-primary)',
                    lineHeight: '1.5',
                    margin: 0,
                    paddingLeft: n.is_read ? 0 : '8px',
                  }}>
                    {n.message}
                  </p>
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default NotificationDropdown;
