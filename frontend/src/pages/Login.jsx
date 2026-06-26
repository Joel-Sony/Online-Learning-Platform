import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/users/login/', { username, password });
      localStorage.setItem('access', res.data.access);
      localStorage.setItem('refresh', res.data.refresh);
      
      const userRes = await api.get('/users/me/');
      localStorage.setItem('role', userRes.data.role);
      localStorage.setItem('username', userRes.data.username);
      
      navigate('/');
    } catch (err) {
      setError('Invalid credentials.');
    }
  };

  return (
    <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '80vh' }}>
      <div style={{ width: '100%', maxWidth: '400px' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h1 style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>Authentication</h1>
          <p style={{ color: 'var(--text-muted)' }}>Sign in to continue.</p>
        </div>
        
        {error && <div className="form-error" style={{ marginBottom: '2rem' }}>{error}</div>}
        
        <form onSubmit={handleSubmit} className="form-stack">
          <div className="form-group">
            <label className="form-label">Username</label>
            <input 
              type="text" 
              className="form-input"
              placeholder="" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)} 
              required 
            />
          </div>
          
          <div className="form-group" style={{ marginTop: '1rem' }}>
            <label className="form-label">Password</label>
            <input 
              type="password" 
              className="form-input"
              placeholder="" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required 
            />
          </div>
          
          <button type="submit" className="btn btn-primary btn-lg" style={{ width: '100%', marginTop: '2rem' }}>
            Enter
          </button>
        </form>
        
        <div className="divider" style={{ margin: '3rem 0 2rem' }}></div>
        
        <div style={{ textAlign: 'center' }}>
          <Link to="/register" className="mono" style={{ color: 'var(--text-muted)', textDecoration: 'underline' }}>
            Create an account
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Login;
