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
            <label className="form-label">Role</label>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
              <label style={{ 
                flex: 1, 
                border: '1px solid var(--border-strong)',
                background: formData.role === 'STUDENT' ? 'var(--text-strong)' : 'transparent',
                color: formData.role === 'STUDENT' ? '#fff' : 'var(--text-strong)',
                padding: '1.25rem 1rem',
                cursor: 'pointer',
                textAlign: 'center',
                transition: 'all 0.3s'
              }}>
                <input 
                  type="radio" 
                  name="role" 
                  value="STUDENT" 
                  checked={formData.role === 'STUDENT'}
                  onChange={() => setFormData({...formData, role: 'STUDENT'})}
                  style={{ display: 'none' }}
                />
                <div style={{ fontFamily: 'var(--font-body)', fontWeight: '400', letterSpacing: '0.05em', textTransform: 'uppercase', fontSize: '0.85rem' }}>Learner</div>
              </label>
              
              <label style={{ 
                flex: 1, 
                border: '1px solid var(--border-strong)',
                background: formData.role === 'MENTOR' ? 'var(--text-strong)' : 'transparent',
                color: formData.role === 'MENTOR' ? '#fff' : 'var(--text-strong)',
                padding: '1.25rem 1rem',
                cursor: 'pointer',
                textAlign: 'center',
                transition: 'all 0.3s'
              }}>
                <input 
                  type="radio" 
                  name="role" 
                  value="MENTOR" 
                  checked={formData.role === 'MENTOR'}
                  onChange={() => setFormData({...formData, role: 'MENTOR'})}
                  style={{ display: 'none' }}
                />
                <div style={{ fontFamily: 'var(--font-body)', fontWeight: '400', letterSpacing: '0.05em', textTransform: 'uppercase', fontSize: '0.85rem' }}>Instructor</div>
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
