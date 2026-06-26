import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api, { apiBase } from '../api';

function LearningDashboard() {
  const [enrollments, setEnrollments] = useState([]);
  const [certificates, setCertificates] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEnrollments();
    fetchCertificates();
  }, []);

  const fetchCertificates = async () => {
    try {
      const res = await api.get('/certificates/');
      // Build a map of course_id -> certificate for easy lookup
      const map = {};
      res.data.forEach(cert => { map[cert.course] = cert; });
      setCertificates(map);
    } catch (err) {
      console.error('Could not load certificates:', err);
    }
  };

  const fetchEnrollments = async () => {
    try {
      const res = await api.get('/enrollments/');
      const enrolledData = res.data;
      
      const dataWithProgress = await Promise.all(enrolledData.map(async (e) => {
        const progRes = await api.get(`/progress/course_progress/?course_id=${e.course}`);
        return { ...e, progress: progRes.data };
      }));
      
      setEnrollments(dataWithProgress);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  const handleRefund = async (enrollmentId) => {
    if (!window.confirm('Are you sure you want to request a refund for this course?')) return;
    try {
      await api.post(`/enrollments/${enrollmentId}/request_refund/`);
      alert('Refund request submitted successfully.');
      fetchEnrollments();
    } catch (err) {
      alert(err.response?.data?.error || 'Refund request failed.');
    }
  };

  const handleUnenroll = async (enrollmentId) => {
    if (!window.confirm('Are you sure you want to unenroll from this course? You will lose access to its materials.')) return;
    try {
      await api.delete(`/enrollments/${enrollmentId}/`);
      fetchEnrollments();
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to unenroll.');
    }
  };

  if (loading) return (
    <div className="page loading-state">
      <div className="spinner"></div> Retrieving your dashboard...
    </div>
  );

  const inProgress = enrollments.filter(e => e.progress.progress_percentage < 100);
  const completed = enrollments.filter(e => e.progress.progress_percentage === 100);

  return (
    <div className="page">
      <div style={{ marginBottom: '4rem', paddingBottom: '2rem', borderBottom: '1px solid var(--border)' }}>
        <span className="mono" style={{ color: 'var(--text-muted)', display: 'block', marginBottom: '1rem' }}>Dashboard</span>
        <h1 style={{ marginBottom: '0' }}>Your Learning</h1>
      </div>
      
      <div style={{ marginBottom: '6rem' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '1rem', marginBottom: '3rem' }}>
          <h2 style={{ margin: 0, fontSize: '1.75rem' }}>Active Studies</h2>
          <span className="mono" style={{ color: 'var(--text-muted)' }}>{inProgress.length}</span>
        </div>

        {inProgress.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '3rem' }}>
            {inProgress.map(enrollment => (
              <div key={enrollment.id} style={{ display: 'flex', flexDirection: 'column' }}>
                <div style={{ paddingBottom: '1.5rem' }}>
                  <div style={{ 
                    height: '200px', 
                    width: '100%', 
                    background: 'var(--surface)',
                    marginBottom: '1.5rem',
                    border: '1px solid var(--border)',
                    position: 'relative'
                  }}>
                    {enrollment.course_details.thumbnail ? (
                      <img src={enrollment.course_details.thumbnail} alt={enrollment.course_details.title} style={{ width: '100%', height: '100%', objectFit: 'cover', filter: 'grayscale(15%) contrast(1.05)' }} />
                    ) : (
                      <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--border-strong)' }}>
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                      </div>
                    )}
                  </div>
                  <h3 style={{ marginBottom: '1.5rem', fontSize: '1.3rem', lineHeight: '1.4' }}>{enrollment.course_details.title}</h3>
                  
                  <div style={{ marginBottom: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                    <span className="mono" style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Progress</span>
                    <span className="mono" style={{ color: 'var(--text-strong)' }}>
                      {enrollment.progress.progress_percentage}%
                    </span>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill" style={{ width: `${enrollment.progress.progress_percentage}%` }}></div>
                  </div>
                </div>
                
                <div style={{ 
                  display: 'flex', 
                  gap: '1rem',
                  marginTop: '1rem'
                }}>
                  <Link to={`/courses/${enrollment.course}`} className="btn btn-primary" style={{ flex: 1 }}>
                    Continue
                  </Link>
                  {enrollment.status !== 'REFUNDED' && (
                    <button onClick={() => handleRefund(enrollment.id)} className="btn btn-secondary">
                      Refund
                    </button>
                  )}
                  <button onClick={() => handleUnenroll(enrollment.id)} className="btn btn-ghost" style={{ color: '#d32f2f', marginLeft: 'auto' }}>
                    Unenroll
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state" style={{ border: '1px solid var(--border)', padding: '4rem' }}>
            <p>You have no active studies.</p>
            <Link to="/courses" className="btn btn-primary" style={{ marginTop: '1.5rem' }}>View Catalog</Link>
          </div>
        )}
      </div>

      <div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '1rem', marginBottom: '3rem' }}>
          <h2 style={{ margin: 0, fontSize: '1.75rem' }}>Completed</h2>
          <span className="mono" style={{ color: 'var(--text-muted)' }}>{completed.length}</span>
        </div>

        {completed.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '3rem' }}>
                 {completed.map(enrollment => (
              <div key={enrollment.id} style={{ display: 'flex', flexDirection: 'column', border: '1px solid var(--border-strong)', background: 'var(--surface)' }}>
                <div style={{ height: '180px', width: '100%', borderBottom: '1px solid var(--border-strong)', position: 'relative' }}>
                  {enrollment.course_details.thumbnail ? (
                    <img src={enrollment.course_details.thumbnail} alt={enrollment.course_details.title} style={{ width: '100%', height: '100%', objectFit: 'cover', filter: 'grayscale(15%) contrast(1.05)' }} />
                  ) : (
                    <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--border-strong)' }}>
                      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                    </div>
                  )}
                </div>
                <div style={{ padding: '2rem', display: 'flex', flexDirection: 'column', flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                    <h3 style={{ fontSize: '1.25rem', margin: 0, paddingRight: '1rem' }}>{enrollment.course_details.title}</h3>
                    <div style={{ color: 'var(--success)' }}>
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    </div>
                  </div>
                  <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {certificates[enrollment.course] && (
                      <a
                        href={`${apiBase}/certificates/${certificates[enrollment.course].id}/download/`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-primary"
                        style={{ width: '100%', textAlign: 'center' }}
                      >
                        🎓 Download Certificate
                      </a>
                    )}
                    <Link to={`/courses/${enrollment.course}`} className="btn btn-secondary" style={{ width: '100%' }}>Review Material</Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="mono" style={{ color: 'var(--text-muted)' }}>No completed studies yet.</p>
        )}
      </div>
    </div>
  );
}

export default LearningDashboard;
