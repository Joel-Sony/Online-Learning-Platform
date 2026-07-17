import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import NotificationDropdown from './NotificationDropdown';
import { getRole, getUsername, isAuthenticated } from '../auth';

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const role = getRole();
  const authed = isAuthenticated();
  const username = getUsername() || '';
  const [showUserMenu, setShowUserMenu] = useState(false);

  useEffect(() => {
    setShowUserMenu(false);
  }, [location]);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav style={{
      position: 'sticky',
      top: 0,
      zIndex: 100,
      background: 'rgba(255,255,255,0.92)',
      backdropFilter: 'blur(12px)',
      WebkitBackdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border)',
      height: '64px',
      display: 'flex',
      alignItems: 'center',
    }}>
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        width: '100%',
        padding: '0 48px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '24px',
      }}>
        {/* Left: Logo + Nav Links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Link to="/" style={{
            fontFamily: 'var(--font-body)',
            fontSize: '1.125rem',
            fontWeight: '700',
            color: 'var(--text-primary)',
            letterSpacing: '-0.025em',
            marginRight: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}>
            <span style={{
              width: '28px', height: '28px',
              background: 'var(--accent)',
              borderRadius: '8px',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              fontSize: '0.8rem',
              fontWeight: '700',
            }}>L</span>
            Platform
          </Link>

          <div style={{ width: '1px', height: '20px', background: 'var(--border)', margin: '0 8px' }} />

          <Link
            to="/courses"
            className={`nav-link ${isActive('/courses') ? 'active' : ''}`}
          >
            Catalog
          </Link>

          {authed && role === 'STUDENT' && (
            <Link to="/learning" className={`nav-link ${isActive('/learning') ? 'active' : ''}`}>
              My Learning
            </Link>
          )}

          {authed && role === 'MENTOR' && (
            <>
              <Link to="/mentor" className={`nav-link ${isActive('/mentor') ? 'active' : ''}`}>
                Studio
              </Link>
              <Link to="/mentor/analytics" className={`nav-link ${isActive('/mentor/analytics') ? 'active' : ''}`}>
                Analytics
              </Link>
              <Link to="/mentor/announcement" className={`nav-link ${isActive('/mentor/announcement') ? 'active' : ''}`}>
                Announce
              </Link>
            </>
          )}

          {authed && role === 'ADMIN' && (
            <Link to="/admin" className={`nav-link ${isActive('/admin') ? 'active' : ''}`}>
              Admin
            </Link>
          )}
        </div>

        {/* Center: Search Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const query = e.target.search.value;
            if (query.trim()) navigate(`/courses?search=${encodeURIComponent(query)}`);
          }}
          style={{ flex: 1, maxWidth: '440px' }}
        >
          <div className="search-bar" style={{ width: '100%' }}>
            <span className="search-bar-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
            </span>
            <input
              name="search"
              type="text"
              className="search-bar-input"
              placeholder="Search courses, instructors, topics..."
              style={{ width: '100%' }}
            />
          </div>
        </form>

        {/* Right: Auth + Notifications */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {authed ? (
            <>
              <NotificationDropdown />

              {/* Avatar & Logout Section */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', transition: 'all 0.3s ease' }}>
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  title={showUserMenu ? "Collapse profile" : "Expand profile"}
                  style={{
                    height: '34px',
                    minWidth: '34px',
                    padding: showUserMenu ? '0 12px' : '0',
                    borderRadius: showUserMenu ? '17px' : '50%',
                    background: 'var(--accent)',
                    color: '#fff',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '0.8rem',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    fontFamily: 'var(--font-body)',
                    transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
                    flexShrink: 0,
                    boxShadow: 'var(--shadow-sm)',
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--accent-hover)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'var(--accent)'}
                >
                  {showUserMenu ? (
                    <>
                      <span style={{
                        width: '20px', height: '20px',
                        borderRadius: '50%',
                        background: 'rgba(255,255,255,0.25)',
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '0.75rem',
                        fontWeight: '700',
                        flexShrink: 0
                      }}>
                        {username ? username.charAt(0).toUpperCase() : 'U'}
                      </span>
                      <span style={{ 
                        animation: 'fadeIn 0.2s ease', 
                        whiteSpace: 'nowrap',
                        color: '#fff',
                        letterSpacing: '-0.01em'
                      }}>
                        {username}
                      </span>
                      <span style={{
                        fontSize: '0.6rem',
                        fontWeight: '700',
                        textTransform: 'uppercase',
                        letterSpacing: '0.06em',
                        padding: '1px 6px',
                        borderRadius: '4px',
                        background: role === 'ADMIN' ? 'rgba(220,38,38,0.3)' : role === 'MENTOR' ? 'rgba(217,119,6,0.3)' : 'rgba(37,99,235,0.3)',
                        color: '#fff',
                        animation: 'fadeIn 0.2s ease',
                      }}>
                        {role}
                      </span>
                    </>
                  ) : (
                    <span style={{ position: 'relative', display: 'inline-flex' }}>
                      {username ? username.charAt(0).toUpperCase() : 'U'}
                      <span style={{
                        position: 'absolute', bottom: '-2px', right: '-2px',
                        width: '8px', height: '8px', borderRadius: '50%',
                        border: '2px solid var(--accent)',
                        background: role === 'ADMIN' ? '#dc2626' : role === 'MENTOR' ? '#d97706' : '#2563eb',
                      }} />
                    </span>
                  )}
                </button>

                {showUserMenu && (
                  <button
                    onClick={handleLogout}
                    title="Sign out"
                    style={{
                      height: '30px',
                      padding: '0 10px',
                      borderRadius: '8px',
                      background: 'var(--error)',
                      color: '#fff',
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: '0.75rem',
                      fontWeight: '650',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      animation: 'fadeIn 0.2s ease',
                      boxShadow: 'var(--shadow-sm)',
                      transition: 'all 0.15s ease',
                      whiteSpace: 'nowrap',
                    }}
                    onMouseEnter={e => e.currentTarget.style.opacity = '0.9'}
                    onMouseLeave={e => e.currentTarget.style.opacity = '1'}
                  >
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>
                    </svg>
                    Logout
                  </button>
                )}
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">Sign In</Link>
              <Link to="/register" className="btn btn-primary btn-sm">
                Get Started
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
