import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

function CreateCourse() {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    level: 'BEGINNER',
    language: 'English',
    price: '0.00',
    is_published: false
  });
  const [thumbnail, setThumbnail] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = new FormData();
    Object.keys(formData).forEach(key => data.append(key, formData[key]));
    if (thumbnail) data.append('thumbnail', thumbnail);

    try {
      await api.post('/courses/', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      navigate('/mentor');
    } catch (err) {
      alert('Failed to create course');
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'left' }}>
      <h1>Create New Course</h1>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div>
          <label>Title</label>
          <input type="text" value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} required style={{ width: '100%', padding: '0.5rem' }} />
        </div>
        <div>
          <label>Description</label>
          <textarea value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} required style={{ width: '100%', padding: '0.5rem', height: '100px' }} />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div>
            <label>Category</label>
            <input type="text" value={formData.category} onChange={e => setFormData({...formData, category: e.target.value})} required style={{ width: '100%', padding: '0.5rem' }} />
          </div>
          <div>
            <label>Language</label>
            <input type="text" value={formData.language} onChange={e => setFormData({...formData, language: e.target.value})} required style={{ width: '100%', padding: '0.5rem' }} />
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div>
            <label>Level</label>
            <select value={formData.level} onChange={e => setFormData({...formData, level: e.target.value})} style={{ width: '100%', padding: '0.5rem' }}>
              <option value="BEGINNER">Beginner</option>
              <option value="INTERMEDIATE">Intermediate</option>
              <option value="ADVANCED">Advanced</option>
            </select>
          </div>
          <div>
            <label>Price ($)</label>
            <input type="number" step="0.01" value={formData.price} onChange={e => setFormData({...formData, price: e.target.value})} required style={{ width: '100%', padding: '0.5rem' }} />
          </div>
        </div>
        <div>
          <label>Thumbnail</label>
          <input type="file" onChange={e => setThumbnail(e.target.files[0])} style={{ width: '100%' }} />
        </div>
        <div>
          <label>
            <input type="checkbox" checked={formData.is_published} onChange={e => setFormData({...formData, is_published: e.target.checked})} />
            Publish immediately
          </label>
        </div>
        <button type="submit" style={{ padding: '1rem', background: 'var(--accent)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Create Course
        </button>
      </form>
    </div>
  );
}

export default CreateCourse;
