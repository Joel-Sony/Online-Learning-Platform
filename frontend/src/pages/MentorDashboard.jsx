import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

function MentorDashboard() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = () => {
    api.get('/courses/', { params: { page_size: 100 } })
      .then(res => {
        setCourses(res.data.results || res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you certain you wish to delete this course? This action cannot be undone.')) {
      try {
        await api.delete(`/courses/${id}/`);
        fetchCourses();
      } catch (err) {
        alert('Failed to delete course');
      }
    }
  };

  if (loading) return (
    <div className="page loading-state">
      <div className="spinner"></div> Accessing studio...
    </div>
  );

  return (
    <div className="page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '4rem', borderBottom: '1px solid var(--border)', paddingBottom: '2rem' }}>
        <div>
          <span className="mono" style={{ color: 'var(--text-muted)', display: 'block', marginBottom: '1rem' }}>Studio</span>
          <h1 style={{ margin: 0 }}>Instructor Dashboard</h1>
        </div>
        <Link to="/mentor/create" className="btn btn-primary">
          Publish New
        </Link>
      </div>

      <div style={{ width: '100%' }}>
        {courses.length > 0 ? (
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr>
                <th className="mono" style={{ padding: '1rem', borderBottom: '1px solid var(--border-strong)', color: 'var(--text-muted)', fontWeight: 'normal' }}>Course Title</th>
                <th className="mono" style={{ padding: '1rem', borderBottom: '1px solid var(--border-strong)', color: 'var(--text-muted)', fontWeight: 'normal' }}>Status</th>
                <th className="mono" style={{ padding: '1rem', borderBottom: '1px solid var(--border-strong)', color: 'var(--text-muted)', fontWeight: 'normal' }}>Price</th>
                <th className="mono" style={{ padding: '1rem', borderBottom: '1px solid var(--border-strong)', color: 'var(--text-muted)', fontWeight: 'normal', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {courses.map(course => (
                <tr key={course.id} style={{ borderBottom: '1px solid var(--border)', transition: 'background 0.3s' }} onMouseEnter={e => e.currentTarget.style.background = 'var(--surface)'} onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
                  <td style={{ padding: '1.5rem 1rem', fontSize: '1.1rem' }}>{course.title}</td>
                  <td style={{ padding: '1.5rem 1rem' }}>
                    <span className="mono" style={{ color: course.is_published ? 'var(--text-strong)' : 'var(--text-muted)' }}>
                      {course.is_published ? 'Published' : 'Draft'}
                    </span>
                  </td>
                  <td style={{ padding: '1.5rem 1rem' }}>
                    <span className="mono">{parseFloat(course.price) > 0 ? `$${course.price}` : 'Free'}</span>
                  </td>
                  <td style={{ padding: '1.5rem 1rem', textAlign: 'right' }}>
                    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', alignItems: 'center' }}>
                      <Link to={`/courses/${course.id}`} className="mono" style={{ textDecoration: 'underline', fontSize: '0.8rem' }}>View</Link>
                      <Link to={`/mentor/edit/${course.id}`} className="mono" style={{ textDecoration: 'underline', fontSize: '0.8rem' }}>Edit</Link>
                      <button onClick={() => handleDelete(course.id)} className="mono" style={{ color: '#d32f2f', textDecoration: 'underline', background: 'none', border: 'none', cursor: 'pointer', padding: 0, fontSize: '0.8rem' }}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state" style={{ border: '1px solid var(--border)', padding: '4rem' }}>
            <p>You have not published any courses yet.</p>
            <Link to="/mentor/create" className="btn btn-secondary" style={{ marginTop: '1.5rem' }}>Create your first course</Link>
          </div>
        )}
      </div>
    </div>
  );
}

export default MentorDashboard;
