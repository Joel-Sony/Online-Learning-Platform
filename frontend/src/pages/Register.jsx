import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';

function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    role: 'STUDENT'
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/users/register/', formData);
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.username?.[0] || err.response?.data?.email?.[0] || 'Registration failed');
    }
  };

  return (
    <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '80vh', paddingBottom: '6rem' }}>
      <div style={{ width: '100%', maxWidth: '400px' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h1 style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>Register</h1>
          <p style={{ color: 'var(--text-muted)' }}>Join the platform.</p>
        </div>
        
        {error && <div className="form-error" style={{ marginBottom: '2rem' }}>{error}</div>}
        
        <form onSubmit={handleSubmit} className="form-stack">
          <div className="form-group">
            <label className="form-label">Username</label>
            <input 
              type="text" 
              className="form-input"
              value={formData.username} 
              onChange={(e) => setFormData({...formData, username: e.target.value})} 
              required 
            />
          </div>
          
          <div className="form-group" style={{ marginTop: '0.5rem' }}>
            <label className="form-label">Email</label>
            <input 
              type="email" 
              className="form-input"
              value={formData.email} 
              onChange={(e) => setFormData({...formData, email: e.target.value})} 
              required 
            />
          </div>
          
          <div className="form-group" style={{ marginTop: '0.5rem' }}>
            <label className="form-label">Password</label>
            <input 
              type="password" 
              className="form-input"
              value={formData.password} 
              onChange={(e) => setFormData({...formData, password: e.target.value})} 
              required 
            />
          </div>

          <div className="form-group" style={{ marginTop: '1.5rem' }}>
            <label className="form-label">I want to join as a...</label>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '0.75rem' }}>
              <label style={{ 
                flex: 1, 
                border: `1.5px solid ${formData.role === 'STUDENT' ? 'var(--accent)' : 'var(--border-strong)'}`,
                borderRadius: 'var(--radius-lg)',
                background: formData.role === 'STUDENT' ? 'var(--accent-light)' : 'transparent',
                color: formData.role === 'STUDENT' ? '#fff' : 'var(--text-strong)',
                padding: '1.5rem 1rem',
                cursor: 'pointer',
                textAlign: 'center',
                transition: 'all 0.15s ease',
                userSelect: 'none',
              }}
                onMouseEnter={e => {
                  if (formData.role !== 'STUDENT') {
                    e.currentTarget.style.borderColor = 'var(--accent)';
                    e.currentTarget.style.background = 'var(--bg-subtle)';
                  }
                }}
                onMouseLeave={e => {
                  if (formData.role !== 'STUDENT') {
                    e.currentTarget.style.borderColor = 'var(--border-strong)';
                    e.currentTarget.style.background = 'transparent';
                  }
                }}
              >
                <input 
                  type="radio" 
                  name="role" 
                  value="STUDENT" 
                  checked={formData.role === 'STUDENT'}
                  onChange={() => setFormData({...formData, role: 'STUDENT'})}
                  style={{ display: 'none' }}
                />
                <div style={{ marginBottom: '0.5rem' }}>
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={formData.role === 'STUDENT' ? 'var(--accent)' : 'var(--text-tertiary)'} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                    <path d="M12 6v7"/><path d="M9 9h6"/>
                  </svg>
                </div>
                <div style={{ fontWeight: '600', fontSize: '0.95rem', color: formData.role === 'STUDENT' ? 'var(--accent)' : 'var(--text-primary)' }}>Learner</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginTop: '0.25rem' }}>Browse and take courses</div>
              </label>
              
              <label style={{ 
                flex: 1, 
                border: `1.5px solid ${formData.role === 'MENTOR' ? 'var(--accent)' : 'var(--border-strong)'}`,
                borderRadius: 'var(--radius-lg)',
                background: formData.role === 'MENTOR' ? 'var(--accent-light)' : 'transparent',
                color: formData.role === 'MENTOR' ? '#fff' : 'var(--text-strong)',
                padding: '1.5rem 1rem',
                cursor: 'pointer',
                textAlign: 'center',
                transition: 'all 0.15s ease',
                userSelect: 'none',
              }}
                onMouseEnter={e => {
                  if (formData.role !== 'MENTOR') {
                    e.currentTarget.style.borderColor = 'var(--accent)';
                    e.currentTarget.style.background = 'var(--bg-subtle)';
                  }
                }}
                onMouseLeave={e => {
                  if (formData.role !== 'MENTOR') {
                    e.currentTarget.style.borderColor = 'var(--border-strong)';
                    e.currentTarget.style.background = 'transparent';
                  }
                }}
              >
                <input 
                  type="radio" 
                  name="role" 
                  value="MENTOR" 
                  checked={formData.role === 'MENTOR'}
                  onChange={() => setFormData({...formData, role: 'MENTOR'})}
                  style={{ display: 'none' }}
                />
                <div style={{ marginBottom: '0.5rem' }}>
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={formData.role === 'MENTOR' ? 'var(--accent)' : 'var(--text-tertiary)'} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                </div>
                <div style={{ fontWeight: '600', fontSize: '0.95rem', color: formData.role === 'MENTOR' ? 'var(--accent)' : 'var(--text-primary)' }}>Instructor</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginTop: '0.25rem' }}>Create and sell courses</div>
              </label>
            </div>
          </div>
          
          <button type="submit" className="btn btn-primary btn-lg" style={{ width: '100%', marginTop: '2rem' }}>
            Create Account
          </button>
        </form>
        
        <div className="divider" style={{ margin: '3rem 0 2rem' }}></div>
        
        <div style={{ textAlign: 'center' }}>
          <Link to="/login" className="mono" style={{ color: 'var(--text-muted)', textDecoration: 'underline' }}>
            Already have an account? Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Register;
