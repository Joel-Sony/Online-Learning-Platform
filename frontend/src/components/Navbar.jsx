import { Link, useNavigate, useLocation } from 'react-router-dom';
import NotificationDropdown from './NotificationDropdown';

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const role = localStorage.getItem('role');
  const isAuthenticated = !!localStorage.getItem('access');
  const username = localStorage.getItem('username') || '';

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

          {isAuthenticated && role === 'STUDENT' && (
            <>
              <Link to="/learning" className={`nav-link ${isActive('/learning') ? 'active' : ''}`}>
                My Learning
              </Link>
            </>
          )}

          {isAuthenticated && role === 'MENTOR' && (
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
          {isAuthenticated ? (
            <>
              <NotificationDropdown />

              {/* Avatar */}
              <button
                onClick={handleLogout}
                title="Sign out"
                style={{
                  width: '34px', height: '34px',
                  borderRadius: '50%',
                  background: 'var(--accent)',
                  color: '#fff',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '0.8rem',
                  fontWeight: '600',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontFamily: 'var(--font-body)',
                  transition: 'var(--transition-base)',
                  flexShrink: 0,
                  title: 'Sign out'
                }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--accent-hover)'}
                onMouseLeave={e => e.currentTarget.style.background = 'var(--accent)'}
              >
                {username ? username.charAt(0).toUpperCase() : 'U'}
              </button>
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
