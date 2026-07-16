import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

function MentorAnalytics() {
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('enrolled-desc');

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

  if (loading) {
    return (
      <div className="page" style={{ animation: 'fadeIn 0.3s ease' }}>
        <div style={{ marginBottom: '2.5rem' }}>
          <div className="skeleton" style={{ width: '250px', height: '40px', marginBottom: '10px' }} />
          <div className="skeleton" style={{ width: '450px', height: '20px' }} />
        </div>
        
        {/* Skeleton Aggregate Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
          {[1, 2, 3, 4].map(n => (
            <div key={n} className="skeleton-card" style={{ height: '120px', padding: '1.5rem' }}>
              <div className="skeleton" style={{ width: '40px', height: '40px', borderRadius: '8px', marginBottom: '12px' }} />
              <div className="skeleton" style={{ width: '100px', height: '16px', marginBottom: '8px' }} />
              <div className="skeleton" style={{ width: '60px', height: '24px' }} />
            </div>
          ))}
        </div>

        {/* Skeleton Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '2rem' }}>
          {[1, 2, 3].map(n => (
            <div key={n} className="skeleton-card" style={{ height: '200px', padding: '1.5rem' }}>
              <div className="skeleton" style={{ width: '70%', height: '24px', marginBottom: '20px' }} />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ width: '50%' }}>
                  <div className="skeleton" style={{ width: '80px', height: '16px', marginBottom: '12px' }} />
                  <div className="skeleton" style={{ width: '40px', height: '24px', marginBottom: '20px' }} />
                  <div className="skeleton" style={{ width: '80px', height: '16px', marginBottom: '12px' }} />
                  <div className="skeleton" style={{ width: '40px', height: '24px' }} />
                </div>
                <div className="skeleton" style={{ width: '80px', height: '80px', borderRadius: '50%' }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Aggregate Stats
  const totalCourses = stats.length;
  const totalEnrolled = stats.reduce((acc, c) => acc + c.total_enrolled, 0);
  const totalCompletions = stats.reduce((acc, c) => acc + c.completions, 0);
  const globalCompletionRate = totalEnrolled > 0 ? ((totalCompletions / totalEnrolled) * 100).toFixed(1) : '0.0';

  // Filter & Sort stats
  const filteredStats = stats
    .filter(course => course.course_title.toLowerCase().includes(searchQuery.toLowerCase()))
    .sort((a, b) => {
      const aRate = a.total_enrolled > 0 ? (a.completions / a.total_enrolled) : 0;
      const bRate = b.total_enrolled > 0 ? (b.completions / b.total_enrolled) : 0;

      switch (sortBy) {
        case 'title-asc':
          return a.course_title.localeCompare(b.course_title);
        case 'title-desc':
          return b.course_title.localeCompare(a.course_title);
        case 'enrolled-desc':
          return b.total_enrolled - a.total_enrolled;
        case 'enrolled-asc':
          return a.total_enrolled - b.total_enrolled;
        case 'completions-desc':
          return b.completions - a.completions;
        case 'completions-asc':
          return a.completions - b.completions;
        case 'rate-desc':
          return bRate - aRate;
        case 'rate-asc':
          return aRate - bRate;
        default:
          return 0;
      }
    });

  return (
    <div className="page" style={{ animation: 'fadeIn 0.3s ease' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2.5rem' }}>
        <div>
          <h1 className="heading-display" style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontWeight: '500' }}>Studio Analytics</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Track your course performance, enrollment trends, and student success rates.</p>
        </div>
      </div>

      {/* Aggregate Overview Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
        {/* Card 1: Total Courses */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{
            width: '40px', height: '40px',
            borderRadius: '8px',
            background: 'var(--accent-light)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
            </svg>
          </div>
          <div>
            <p className="label" style={{ textTransform: 'uppercase', fontSize: '0.7rem' }}>Total Courses</p>
            <h3 style={{ fontSize: '1.8rem', fontWeight: '700', marginTop: '4px' }}>{totalCourses}</h3>
          </div>
        </div>

        {/* Card 2: Total Enrolled */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{
            width: '40px', height: '40px',
            borderRadius: '8px',
            background: 'var(--accent-light)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          </div>
          <div>
            <p className="label" style={{ textTransform: 'uppercase', fontSize: '0.7rem' }}>Total Enrolled</p>
            <h3 style={{ fontSize: '1.8rem', fontWeight: '700', marginTop: '4px' }}>{totalEnrolled}</h3>
          </div>
        </div>

        {/* Card 3: Completions */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{
            width: '40px', height: '40px',
            borderRadius: '8px',
            background: '#f0fdf4',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="8" r="7" />
              <polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88" />
            </svg>
          </div>
          <div>
            <p className="label" style={{ textTransform: 'uppercase', fontSize: '0.7rem' }}>Completions</p>
            <h3 style={{ fontSize: '1.8rem', fontWeight: '700', marginTop: '4px', color: 'var(--success)' }}>{totalCompletions}</h3>
          </div>
        </div>

        {/* Card 4: Global Completion Rate */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{
            width: '40px', height: '40px',
            borderRadius: '8px',
            background: '#fffbeb',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--warning)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="19" y1="5" x2="5" y2="19" />
              <circle cx="6.5" cy="6.5" r="2.5" />
              <circle cx="17.5" cy="17.5" r="2.5" />
            </svg>
          </div>
          <div>
            <p className="label" style={{ textTransform: 'uppercase', fontSize: '0.7rem' }}>Avg. Completion Rate</p>
            <h3 style={{ fontSize: '1.8rem', fontWeight: '700', marginTop: '4px', color: 'var(--warning)' }}>{globalCompletionRate}%</h3>
          </div>
        </div>
      </div>

      {/* Control Panel: Search & Filter */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '16px',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '2rem',
        paddingBottom: '1rem',
        borderBottom: '1px solid var(--border)'
      }}>
        <div style={{ display: 'flex', flex: 1, minWidth: '280px', maxWidth: '400px', position: 'relative' }}>
          <input
            type="text"
            className="form-input"
            placeholder="Search courses..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ paddingLeft: '44px' }}
          />
          <span style={{ position: 'absolute', left: '14px', top: '12px', color: 'var(--text-tertiary)' }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="label" style={{ textTransform: 'uppercase', fontWeight: '600' }}>Sort by:</span>
          <select
            className="filter-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            style={{ width: '180px', height: '42px', padding: '0 12px', backgroundPosition: 'right 12px center' }}
          >
            <option value="enrolled-desc">Enrolled (High to Low)</option>
            <option value="enrolled-asc">Enrolled (Low to High)</option>
            <option value="completions-desc">Completions (High to Low)</option>
            <option value="completions-asc">Completions (Low to High)</option>
            <option value="rate-desc">Success Rate (High to Low)</option>
            <option value="rate-asc">Success Rate (Low to High)</option>
            <option value="title-asc">Title (A to Z)</option>
            <option value="title-desc">Title (Z to A)</option>
          </select>
        </div>
      </div>

      {/* Courses List */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1.75rem' }}>
        {filteredStats.map(course => {
          const rateNum = course.total_enrolled > 0 ? (course.completions / course.total_enrolled) * 100 : 0;
          const rate = rateNum.toFixed(1);
          
          // Calculate SVG values
          const radius = 28;
          const circumference = 2 * Math.PI * radius;
          const strokeDashoffset = circumference - (rateNum / 100) * circumference;

          return (
            <div key={course.course_id} className="card card-hover" style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              height: '100%',
              padding: '1.75rem',
              transition: 'var(--transition-slow)',
            }}>
              <div>
                {/* Course Title */}
                <h2 style={{ fontSize: '1.15rem', fontWeight: '650', marginBottom: '1.25rem', lineHeight: '1.4' }}>
                  {course.course_title}
                </h2>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto' }}>
                  {/* Left Side: Stats Numbers */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: '500' }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '6px' }}>
                          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                          <circle cx="9" cy="7" r="4" />
                        </svg>
                        Enrolled Students
                      </div>
                      <p style={{ fontSize: '1.3rem', fontWeight: '700', margin: '4px 0 0 20px', color: 'var(--text-primary)' }}>
                        {course.total_enrolled}
                      </p>
                    </div>

                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: '500' }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '6px' }}>
                          <circle cx="12" cy="8" r="7" />
                          <polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88" />
                        </svg>
                        Completions
                      </div>
                      <p style={{ fontSize: '1.3rem', fontWeight: '700', margin: '4px 0 0 20px', color: 'var(--success)' }}>
                        {course.completions}
                      </p>
                    </div>
                  </div>

                  {/* Right Side: Circular Gauge */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                    <div style={{ position: 'relative', width: '72px', height: '72px' }}>
                      <svg width="72" height="72" viewBox="0 0 72 72">
                        {/* Background Circle */}
                        <circle
                          cx="36"
                          cy="36"
                          r={radius}
                          fill="transparent"
                          stroke="var(--surface)"
                          strokeWidth="5"
                        />
                        {/* Progress Circle */}
                        <circle
                          cx="36"
                          cy="36"
                          r={radius}
                          fill="transparent"
                          stroke={rateNum > 50 ? 'var(--success)' : rateNum > 20 ? 'var(--warning)' : 'var(--accent)'}
                          strokeWidth="5"
                          strokeDasharray={circumference}
                          strokeDashoffset={strokeDashoffset}
                          strokeLinecap="round"
                          transform="rotate(-90 36 36)"
                          style={{ transition: 'stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1)' }}
                        />
                      </svg>
                      {/* Percent Center Text */}
                      <div style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '0.8rem',
                        fontWeight: '700',
                        color: 'var(--text-primary)'
                      }}>
                        {rate}%
                      </div>
                    </div>
                    <span className="label" style={{ fontSize: '0.65rem', textTransform: 'uppercase' }}>Success Rate</span>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {filteredStats.length === 0 && (
        <div className="empty-state" style={{ marginTop: '2rem', padding: '4rem 2rem', background: 'var(--bg-subtle)', borderRadius: '12px', border: '1px dashed var(--border)' }}>
          <div className="empty-state-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
            </svg>
          </div>
          <h3>No course analytics found</h3>
          <p style={{ color: 'var(--text-tertiary)' }}>
            {stats.length === 0
              ? "You haven't created any courses yet. Share your knowledge with the world to see analytics!"
              : "Try adjusting your search query or sorting options."}
          </p>
          {stats.length === 0 && (
            <Link to="/mentor" className="btn btn-primary btn-sm" style={{ marginTop: '1rem' }}>
              Go to Studio
            </Link>
          )}
        </div>
      )}
    </div>
  );
}

export default MentorAnalytics;
