import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

/* ── Mini course card for the homepage ─────────────────────── */
function HomeCourseCard({ course }) {
  return (
    <Link to={`/courses/${course.id}`} className="course-card" style={{ minWidth: '280px', width: '280px' }}>
      <div className="course-card-thumb">
        {course.thumbnail ? (
          <img src={course.thumbnail} alt={course.title} />
        ) : (
          <div className="course-card-thumb-placeholder">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
          </div>
        )}
      </div>
      <div className="course-card-body">
        <span className="badge badge-category" style={{ alignSelf: 'flex-start' }}>{course.category}</span>
        <h3 className="course-card-title">{course.title}</h3>
        <span className="course-card-instructor">{course.mentor_name}</span>
        <div className="course-card-footer" style={{ marginTop: '12px' }}>
          <div className="rating-display">
            <span className="stars">★</span>
            <span className="rating-score">{course.avg_rating?.toFixed(1) || '—'}</span>
          </div>
          <span className="course-card-price">
            {parseFloat(course.price) > 0 ? `$${parseFloat(course.price).toFixed(0)}` : 'Free'}
          </span>
        </div>
      </div>
    </Link>
  );
}

function Home() {
  const [courses, setCourses] = useState([]);
  const [topRated, setTopRated] = useState([]);
  const [loading, setLoading] = useState(true);
  const isLoggedIn = !!localStorage.getItem('access');
  const role = localStorage.getItem('role');

  useEffect(() => {
    Promise.all([
      api.get('/courses/', { params: { ordering: '-created_at', page_size: 8 } }),
      api.get('/courses/', { params: { ordering: '-avg_rating', page_size: 6 } }),
    ])
      .then(([newRes, ratedRes]) => {
        setCourses(newRes.data.results || newRes.data);
        setTopRated(ratedRes.data.results || ratedRes.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div style={{ width: '100%' }}>

      {/* ── Hero ──────────────────────────────────────────────── */}
      <section style={{
        background: 'linear-gradient(135deg, #fafafe 0%, #f5f3ff 50%, #eff6ff 100%)',
        borderBottom: '1px solid var(--border)',
        padding: '80px 0 72px',
      }}>
        <div className="container">
          <div style={{ maxWidth: '640px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '24px' }}>
              <span style={{
                fontSize: '0.75rem',
                fontWeight: '600',
                color: 'var(--accent)',
                background: 'var(--accent-light)',
                padding: '4px 12px',
                borderRadius: 'var(--radius-pill)',
                letterSpacing: '0.04em',
                textTransform: 'uppercase',
              }}>New Courses Available</span>
            </div>

            <h1 style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(2.5rem, 5vw, 3.75rem)',
              fontWeight: '500',
              lineHeight: '1.08',
              letterSpacing: '-0.03em',
              color: 'var(--text-primary)',
              marginBottom: '24px',
            }}>
              Learn In-Demand<br />
              <span style={{ color: 'var(--accent)' }}>Skills</span> That Matter
            </h1>

            <p style={{
              fontSize: '1.1rem',
              color: 'var(--text-secondary)',
              lineHeight: '1.7',
              marginBottom: '40px',
              maxWidth: '520px',
            }}>
              A curated selection of industry-led courses designed for ambitious professionals.
              Rigorous instruction, no filler.
            </p>

            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
              <Link to="/courses" className="btn btn-primary btn-xl">
                Browse Courses
              </Link>
              {isLoggedIn && role === 'STUDENT' ? (
                <Link to="/learning" className="btn btn-secondary btn-xl">
                  Continue Learning
                </Link>
              ) : (
                <Link to="/register" className="btn btn-secondary btn-xl">
                  Get Started Free
                </Link>
              )}
            </div>

            {/* Social proof */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '24px', marginTop: '48px' }}>
              {[
                { value: courses.length + '+', label: 'Courses' },
                { value: '4.8', label: 'Avg Rating' },
                { value: '100%', label: 'Online' },
              ].map(stat => (
                <div key={stat.label}>
                  <div style={{ fontSize: '1.25rem', fontWeight: '700', color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>{stat.value}</div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-tertiary)', marginTop: '1px' }}>{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── New Releases ──────────────────────────────────────── */}
      <section style={{ padding: '64px 0' }}>
        <div className="container">
          <div className="section-header">
            <h2>New Releases</h2>
            <Link to="/courses?ordering=-created_at" className="section-link">
              View all
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </Link>
          </div>

          {loading ? (
            <div style={{ display: 'flex', gap: '24px' }}>
              {Array(4).fill(0).map((_, i) => (
                <div key={i} className="skeleton-card" style={{ minWidth: '280px', width: '280px' }}>
                  <div className="skeleton" style={{ height: '157px' }} />
                  <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <div className="skeleton" style={{ height: '12px', width: '60px' }} />
                    <div className="skeleton" style={{ height: '16px', width: '90%' }} />
                    <div className="skeleton" style={{ height: '16px', width: '70%' }} />
                    <div className="skeleton" style={{ height: '12px', width: '50%' }} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="scroll-section">
              {courses.map(c => <HomeCourseCard key={c.id} course={c} />)}
            </div>
          )}
        </div>
      </section>

      {/* ── Top Rated ────────────────────────────────────────── */}
      {topRated.length > 0 && (
        <section style={{ padding: '0 0 64px' }}>
          <div className="container">
            <div className="section-header">
              <h2>Top Rated</h2>
              <Link to="/courses?ordering=-avg_rating" className="section-link">
                View all
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
              </Link>
            </div>
            <div className="scroll-section">
              {topRated.map(c => <HomeCourseCard key={c.id} course={c} />)}
            </div>
          </div>
        </section>
      )}

      {/* ── Category Pills ────────────────────────────────────── */}
      <section style={{ padding: '0 0 64px' }}>
        <div className="container">
          <div className="section-header">
            <h2>Browse by Category</h2>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
            {['Development', 'Business', 'Design', 'Marketing', 'Music', 'Photography'].map(cat => (
              <Link
                key={cat}
                to={`/courses?category=${cat}`}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '10px 20px',
                  borderRadius: 'var(--radius-pill)',
                  border: '1.5px solid var(--border)',
                  background: 'var(--bg)',
                  color: 'var(--text-secondary)',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  transition: 'var(--transition-base)',
                  textDecoration: 'none',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.borderColor = 'var(--accent)';
                  e.currentTarget.style.color = 'var(--accent)';
                  e.currentTarget.style.background = 'var(--accent-light)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.borderColor = 'var(--border)';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                  e.currentTarget.style.background = 'var(--bg)';
                }}
              >
                {cat}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────────── */}
      <footer style={{ borderTop: '1px solid var(--border)', padding: '32px 0' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{
              width: '24px', height: '24px',
              background: 'var(--accent)',
              borderRadius: '6px',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              fontSize: '0.7rem',
              fontWeight: '700',
            }}>L</span>
            <span style={{ fontWeight: '600', fontSize: '0.9rem', color: 'var(--text-primary)' }}>Platform</span>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)' }}>© 2026 Platform. All rights reserved.</span>
        </div>
      </footer>
    </div>
  );
}

export default Home;
