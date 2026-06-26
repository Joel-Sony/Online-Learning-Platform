import { useState, useEffect } from 'react';
import api from '../api';

function MentorAnalytics() {
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/mentor-analytics/')
      .then(res => {
        setStats(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading analytics...</div>;

  return (
    <div style={{ textAlign: 'left' }}>
      <h1>Course Analytics</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '2rem' }}>
        {stats.map(course => (
          <div key={course.course_id} style={{ border: '1px solid var(--border)', borderRadius: '8px', padding: '1.5rem', backgroundColor: 'var(--bg)', boxShadow: 'var(--shadow)' }}>
            <h2 style={{ fontSize: '1.2rem', margin: '0 0 1rem 0' }}>{course.course_title}</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <p style={{ color: 'var(--text)', fontSize: '0.8rem' }}>Total Enrolled</p>
                <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{course.total_enrolled}</p>
              </div>
              <div>
                <p style={{ color: 'var(--text)', fontSize: '0.8rem' }}>Completions</p>
                <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'green' }}>{course.completions}</p>
              </div>
            </div>
            <div style={{ marginTop: '1rem' }}>
              <p style={{ color: 'var(--text)', fontSize: '0.8rem' }}>Completion Rate</p>
              <p style={{ fontSize: '1.1rem' }}>
                {course.total_enrolled > 0 ? ((course.completions / course.total_enrolled) * 100).toFixed(1) : 0}%
              </p>
            </div>
          </div>
        ))}
      </div>
      {stats.length === 0 && <p>No course data available.</p>}
    </div>
  );
}

export default MentorAnalytics;
