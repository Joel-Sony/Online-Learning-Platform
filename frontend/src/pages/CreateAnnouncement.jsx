import { useState, useEffect } from 'react';
import api from '../api';

function CreateAnnouncement() {
  const [courses, setCourses] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [loadingAnnouncements, setLoadingAnnouncements] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    course: '',
    title: '',
    content: '',
    send_email: false
  });
  const [status, setStatus] = useState('');

  const fetchData = async () => {
    try {
      // Fetch mentor's courses
      const coursesRes = await api.get('/courses/', { params: { page_size: 100 } });
      const list = coursesRes.data.results || coursesRes.data;
      const mentorCourses = list.filter(c => c.mentor_name === localStorage.getItem('username'));
      setCourses(mentorCourses);

      // Fetch all announcements and filter by those belonging to mentor's courses
      const annsRes = await api.get('/announcements/');
      const mentorCourseIds = mentorCourses.map(c => c.id);
      const mentorAnns = annsRes.data.filter(ann => mentorCourseIds.includes(ann.course));
      setAnnouncements(mentorAnns.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)));
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingAnnouncements(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setStatus('');
    try {
      const res = await api.post('/announcements/', formData);
      setStatus('Broadcast successful!');
      setFormData({ course: '', title: '', content: '', send_email: false });
      
      // Update announcements list locally
      setAnnouncements(prev => [res.data, ...prev]);
    } catch (err) {
      setStatus('Error sending announcement.');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this announcement?')) return;
    try {
      await api.delete(`/announcements/${id}/`);
      setAnnouncements(prev => prev.filter(ann => ann.id !== id));
    } catch (err) {
      console.error(err);
      alert('Error deleting announcement.');
    }
  };

  return (
    <div className="page" style={{ animation: 'fadeIn 0.3s ease' }}>
      {/* Header */}
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 className="heading-display" style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontWeight: '500' }}>Announcements Studio</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Broadcast important updates, share study resources, and email announcements directly to enrolled students.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2.5rem', alignItems: 'start' }}>
        
        {/* Left Pane: Broadcast Form */}
        <div className="card" style={{ padding: '2rem' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2.5">
              <path d="M12 19V6M5 12l7-7 7 7"/>
            </svg>
            Broadcast New
          </h2>
          
          <form onSubmit={handleSubmit} className="form-stack">
            <div className="form-group">
              <label className="form-label">Select Course</label>
              <select 
                value={formData.course} 
                onChange={e => setFormData({...formData, course: e.target.value})}
                className="form-select"
                required
                disabled={submitting}
              >
                <option value="">-- Select a Course --</option>
                {courses.map(c => (
                  <option key={c.id} value={c.id}>{c.title}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Announcement Title</label>
              <input 
                type="text" 
                className="form-input"
                placeholder="e.g. Welcome to Week 1 & Setup Guide"
                value={formData.title} 
                onChange={e => setFormData({...formData, title: e.target.value})}
                required
                disabled={submitting}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Message Content</label>
              <textarea 
                className="form-textarea"
                placeholder="Write your announcement content here. Markdown or plain text is supported..."
                value={formData.content} 
                onChange={e => setFormData({...formData, content: e.target.value})}
                required
                disabled={submitting}
                style={{ minHeight: '180px' }}
              />
            </div>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '12px 16px',
              background: 'var(--bg-subtle)',
              borderRadius: '8px',
              border: '1px solid var(--border)',
              cursor: 'pointer',
              transition: 'var(--transition-fast)'
            }}>
              <input 
                type="checkbox" 
                checked={formData.send_email} 
                onChange={e => setFormData({...formData, send_email: e.target.checked})}
                id="sendEmail"
                style={{
                  width: '18px',
                  height: '18px',
                  accentColor: 'var(--accent)',
                  cursor: 'pointer'
                }}
                disabled={submitting}
              />
              <label htmlFor="sendEmail" style={{ fontSize: '0.85rem', fontWeight: '500', color: 'var(--text-primary)', cursor: 'pointer', userSelect: 'none' }}>
                Send email notification to all students
              </label>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary btn-lg" 
              style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
              disabled={submitting}
            >
              {submitting ? (
                <>
                  <span className="spinner" style={{ width: '16px', height: '16px', borderTopColor: '#fff', borderLeftColor: 'transparent', borderBottomColor: 'transparent', borderRightColor: 'transparent' }}></span>
                  Broadcasting...
                </>
              ) : (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13"></line>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                  </svg>
                  Broadcast Announcement
                </>
              )}
            </button>
            
            {status && (
              <div style={{
                fontSize: '0.85rem',
                fontWeight: '550',
                color: status.includes('Error') ? 'var(--error)' : 'var(--success)',
                padding: '10px 14px',
                borderRadius: '6px',
                background: status.includes('Error') ? '#fff5f5' : '#f0fdf4',
                border: `1px solid ${status.includes('Error') ? '#feb2b2' : '#c6f6d5'}`,
                textAlign: 'center',
                animation: 'fadeIn 0.2s ease'
              }}>
                {status}
              </div>
            )}
          </form>
        </div>

        {/* Right Pane: Timeline History */}
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            Broadcast History
          </h2>
          
          {loadingAnnouncements ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {[1, 2].map(n => (
                <div key={n} className="skeleton-card" style={{ height: '160px', padding: '1.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <div className="skeleton" style={{ width: '120px', height: '16px' }} />
                    <div className="skeleton" style={{ width: '80px', height: '14px' }} />
                  </div>
                  <div className="skeleton" style={{ width: '60%', height: '20px', marginBottom: '10px' }} />
                  <div className="skeleton" style={{ width: '90%', height: '14px' }} />
                </div>
              ))}
            </div>
          ) : announcements.length === 0 ? (
            <div className="empty-state" style={{ padding: '3.5rem 2rem', background: 'var(--bg-subtle)', borderRadius: '12px', border: '1px dashed var(--border)' }}>
              <div className="empty-state-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                  <polyline points="22,6 12,13 2,6"></polyline>
                </svg>
              </div>
              <h3>No announcements broadcasted yet</h3>
              <p style={{ color: 'var(--text-tertiary)' }}>Select a course and write a message on the left to broadcast your first update.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {announcements.map(ann => (
                <div key={ann.id} className="card" style={{
                  padding: '1.5rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px',
                  animation: 'fadeIn 0.25s ease'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px' }}>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', alignItems: 'center' }}>
                      <span className="badge badge-category" style={{ fontSize: '0.68rem', fontWeight: '600' }}>
                        {ann.course_name}
                      </span>
                      {ann.send_email && (
                        <span className="badge" style={{ background: '#e0f2fe', color: '#0369a1', fontSize: '0.65rem', display: 'flex', alignItems: 'center', gap: '3px' }}>
                          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                            <polyline points="22,6 12,13 2,6"></polyline>
                          </svg>
                          Email Sent
                        </span>
                      )}
                    </div>
                    <span className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)' }}>
                      {new Date(ann.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                    </span>
                  </div>
                  
                  <div>
                    <h3 style={{ fontSize: '1.05rem', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '6px' }}>
                      {ann.title}
                    </h3>
                    <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
                      {ann.content}
                    </p>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', borderTop: '1px solid var(--border)', paddingTop: '10px', marginTop: '4px' }}>
                    <button
                      onClick={() => handleDelete(ann.id)}
                      title="Delete announcement"
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--text-tertiary)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: '0.72rem',
                        fontWeight: '550',
                        transition: 'color 0.15s ease, background 0.15s ease',
                        padding: '4px 8px',
                        borderRadius: '4px'
                      }}
                      onMouseEnter={e => {
                        e.currentTarget.style.color = 'var(--error)';
                        e.currentTarget.style.background = '#fff5f5';
                      }}
                      onMouseLeave={e => {
                        e.currentTarget.style.color = 'var(--text-tertiary)';
                        e.currentTarget.style.background = 'transparent';
                      }}
                    >
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      </svg>
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

export default CreateAnnouncement;
