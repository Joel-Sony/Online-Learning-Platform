import { useState, useEffect } from 'react';
import api from '../api';

function CreateAnnouncement() {
  const [courses, setCourses] = useState([]);
  const [formData, setFormData] = useState({
    course: '',
    title: '',
    content: '',
    send_email: false
  });
  const [status, setStatus] = useState('');

  useEffect(() => {
    // Fetch mentor's courses
    api.get('/courses/')
      .then(res => {
        // Filter courses where user is mentor (assuming role check is done by backend but for UI)
        setCourses(res.data.filter(c => c.mentor_name === localStorage.getItem('username')));
      })
      .catch(err => console.error(err));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('Sending...');
    try {
      await api.post('/announcements/', formData);
      setStatus('Announcement sent successfully!');
      setFormData({ course: '', title: '', content: '', send_email: false });
    } catch (err) {
      setStatus('Error sending announcement.');
      console.error(err);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'left' }}>
      <h1>Create Course Announcement</h1>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', padding: '2rem', border: '1px solid var(--border)', borderRadius: '8px' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem' }}>Select Course</label>
          <select 
            value={formData.course} 
            onChange={e => setFormData({...formData, course: e.target.value})}
            style={{ width: '100%', padding: '0.5rem' }}
            required
          >
            <option value="">-- Select a Course --</option>
            {courses.map(c => (
              <option key={c.id} value={c.id}>{c.title}</option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem' }}>Announcement Title</label>
          <input 
            type="text" 
            value={formData.title} 
            onChange={e => setFormData({...formData, title: e.target.value})}
            style={{ width: '100%', padding: '0.5rem' }}
            required
          />
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem' }}>Message</label>
          <textarea 
            value={formData.content} 
            onChange={e => setFormData({...formData, content: e.target.value})}
            style={{ width: '100%', padding: '0.5rem', height: '150px' }}
            required
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <input 
            type="checkbox" 
            checked={formData.send_email} 
            onChange={e => setFormData({...formData, send_email: e.target.checked})}
            id="sendEmail"
          />
          <label htmlFor="sendEmail">Send email notification to all students</label>
        </div>

        <button type="submit" style={{ padding: '1rem', background: 'var(--accent)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Broadcast Announcement
        </button>
        {status && <p style={{ textAlign: 'center', fontWeight: 'bold' }}>{status}</p>}
      </form>
    </div>
  );
}

export default CreateAnnouncement;
