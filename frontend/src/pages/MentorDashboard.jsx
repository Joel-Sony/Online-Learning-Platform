import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

const ROLE_COLORS = {
  STUDENT: '#2563eb',
  MENTOR: '#d97706',
  ADMIN: '#dc2626',
};

function MentorDashboard() {
  const [courses, setCourses] = useState([]);
  const [enrollments, setEnrollments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchCourses(), fetchEnrollments()]).finally(() => setLoading(false));
  }, []);

  const fetchCourses = () =>
    api.get('/courses/', { params: { page_size: 100 } }).then(res => {
      setCourses(res.data.results || res.data);
    }).catch(() => {});

  const fetchEnrollments = () =>
    api.get('/enrollments/', { params: { page_size: 20 } }).then(res => {
      setEnrollments(res.data.results || res.data);
    }).catch(() => {});

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

  const totalStudents = courses.reduce((sum, c) => sum + (Number(c.enrollment_count) || 0), 0);
  const totalLessons = courses.reduce((sum, c) => sum + (Number(c.total_duration) || 0), 0);
  const avgRating = courses.length
    ? (courses.reduce((sum, c) => sum + (Number(c.avg_rating) || 0), 0) / courses.length).toFixed(1)
    : '—';

  if (loading) return (
    <div className="page loading-state">
      <div className="spinner"></div> Loading studio...
    </div>
  );

  return (
    <div className="page" style={{ maxWidth: '1280px', margin: '0 auto', padding: '40px 48px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2.5rem' }}>
        <div>
          <span className="mono" style={{ color: 'var(--text-muted)', display: 'block', marginBottom: '0.5rem' }}>Studio</span>
          <h1 style={{ margin: 0 }}>Instructor Dashboard</h1>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <Link to="/mentor/announcement" className="btn btn-secondary">Send Announcement</Link>
          <Link to="/mentor/analytics" className="btn btn-secondary">Analytics</Link>
          <Link to="/mentor/create" className="btn btn-primary">Create Course</Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '2.5rem' }}>
        {[
          { label: 'My Courses', value: courses.length, color: ROLE_COLORS.MENTOR },
          { label: 'Total Students', value: totalStudents, color: '#059669' },
          { label: 'Total Lessons', value: totalLessons, color: '#0891b2' },
          { label: 'Avg Rating', value: avgRating, color: '#7c3aed' },
        ].map(s => (
          <div key={s.label} style={{
            background: 'var(--bg)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-lg)', padding: '1.25rem',
            boxShadow: 'var(--shadow-sm)',
          }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>{s.label}</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 700, color: s.color }}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* My Courses */}
      <div style={{ marginBottom: '2.5rem' }}>
        <h2 style={{ marginBottom: '1rem' }}>My Courses</h2>
        {courses.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr>
                  <th className="mono" style={{ padding: '0.75rem 1rem', borderBottom: '2px solid var(--border-strong)', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Course</th>
                  <th className="mono" style={{ padding: '0.75rem 1rem', borderBottom: '2px solid var(--border-strong)', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Status</th>
                  <th className="mono" style={{ padding: '0.75rem 1rem', borderBottom: '2px solid var(--border-strong)', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Students</th>
                  <th className="mono" style={{ padding: '0.75rem 1rem', borderBottom: '2px solid var(--border-strong)', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Rating</th>
                  <th className="mono" style={{ padding: '0.75rem 1rem', borderBottom: '2px solid var(--border-strong)', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Price</th>
                  <th className="mono" style={{ padding: '0.75rem 1rem', borderBottom: '2px solid var(--border-strong)', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.06em', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {courses.map(course => (
                  <tr key={course.id} style={{ borderBottom: '1px solid var(--border)', transition: 'background 0.15s' }}
                    onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-subtle)'}
                    onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                  >
                    <td style={{ padding: '1rem', fontWeight: 500, color: 'var(--text-primary)' }}>{course.title}</td>
                    <td style={{ padding: '1rem' }}>
                      <span style={{
                        display: 'inline-block', padding: '2px 10px', borderRadius: 'var(--radius-pill)',
                        fontSize: '0.72rem', fontWeight: 600,
                        background: course.is_published ? '#f0fdf4' : '#fffbeb',
                        color: course.is_published ? '#16a34a' : '#d97706',
                      }}>
                        {course.is_published ? 'Published' : course.status === 'PENDING' ? 'Pending' : course.status === 'REJECTED' ? 'Rejected' : 'Draft'}
                      </span>
                    </td>
                    <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>{Number(course.enrollment_count) || 0}</td>
                    <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>
                      {course.avg_rating ? `${Number(course.avg_rating).toFixed(1)}` : '—'}
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <span className="mono">{parseFloat(course.price) > 0 ? `$${course.price}` : 'Free'}</span>
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', alignItems: 'center' }}>
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
          </div>
        ) : (
          <div className="empty-state" style={{ border: '1px solid var(--border)', padding: '4rem' }}>
            <p>You have not created any courses yet.</p>
            <Link to="/mentor/create" className="btn btn-secondary" style={{ marginTop: '1.5rem' }}>Create your first course</Link>
          </div>
        )}
      </div>

      {/* Recent Enrollments */}
      {enrollments.length > 0 && (
        <div>
          <h2 style={{ marginBottom: '1rem' }}>Recent Enrollments</h2>
          <div style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th className="mono" style={{ padding: '0.75rem 1rem', borderBottom: '2px solid var(--border-strong)', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Student</th>
                  <th className="mono" style={{ padding: '0.75rem 1rem', borderBottom: '2px solid var(--border-strong)', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Course</th>
                  <th className="mono" style={{ padding: '0.75rem 1rem', borderBottom: '2px solid var(--border-strong)', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Date</th>
                  <th className="mono" style={{ padding: '0.75rem 1rem', borderBottom: '2px solid var(--border-strong)', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {enrollments.slice(0, 10).map(e => (
                  <tr key={e.id} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 500, color: 'var(--text-primary)' }}>{e.student_name || e.student}</td>
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)' }}>{e.course_title || `Course #${e.course}`}</td>
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)' }}>{e.enrolled_at ? new Date(e.enrolled_at).toLocaleDateString() : '—'}</td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <span style={{
                        display: 'inline-block', padding: '2px 10px', borderRadius: 'var(--radius-pill)',
                        fontSize: '0.72rem', fontWeight: 600,
                        background: e.status === 'ACTIVE' ? '#f0fdf4' : '#fef2f2',
                        color: e.status === 'ACTIVE' ? '#16a34a' : '#dc2626',
                      }}>{e.status || 'ACTIVE'}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default MentorDashboard;
