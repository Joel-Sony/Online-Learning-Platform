import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
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
  const [thumbnailPreview, setThumbnailPreview] = useState(null);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  const handleThumbnail = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setThumbnail(file);
    setThumbnailPreview(URL.createObjectURL(file));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    const data = new FormData();
    Object.keys(formData).forEach(key => data.append(key, formData[key]));
    if (thumbnail) data.append('thumbnail', thumbnail);

    try {
      const res = await api.post('/courses/', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      // Jump straight into the curriculum builder for the new course.
      navigate(`/mentor/edit/${res.data.id}`);
    } catch (err) {
      const detail = err.response?.data;
      setError(detail ? (typeof detail === 'string' ? detail : JSON.stringify(detail)) : 'Failed to create course.');
      setSaving(false);
    }
  };

  return (
    <div className="page" style={{ maxWidth: '680px' }}>
      <Link to="/mentor" style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)' }}>← Studio</Link>
      <div style={{ marginTop: '8px', marginBottom: 'var(--sp-4)' }}>
        <span className="label">New course</span>
        <h1 style={{ marginTop: '4px' }}>Create a Course</h1>
        <p style={{ marginTop: '6px' }}>Start with the basics — you'll add modules and lessons next.</p>
      </div>

      {error && <div className="form-error" style={{ marginBottom: 'var(--sp-3)' }}>{error}</div>}

      <form onSubmit={handleSubmit} className="form-stack">
        <div className="form-group">
          <label className="form-label">Title</label>
          <input className="form-input" type="text" value={formData.title}
            onChange={e => setFormData({ ...formData, title: e.target.value })} required />
        </div>

        <div className="form-group">
          <label className="form-label">Description</label>
          <textarea className="form-textarea" value={formData.description}
            onChange={e => setFormData({ ...formData, description: e.target.value })} required />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--sp-2)' }}>
          <div className="form-group">
            <label className="form-label">Category</label>
            <input className="form-input" type="text" value={formData.category}
              onChange={e => setFormData({ ...formData, category: e.target.value })} required />
          </div>
          <div className="form-group">
            <label className="form-label">Language</label>
            <input className="form-input" type="text" value={formData.language}
              onChange={e => setFormData({ ...formData, language: e.target.value })} required />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--sp-2)' }}>
          <div className="form-group">
            <label className="form-label">Level</label>
            <select className="form-select" value={formData.level}
              onChange={e => setFormData({ ...formData, level: e.target.value })}>
              <option value="BEGINNER">Beginner</option>
              <option value="INTERMEDIATE">Intermediate</option>
              <option value="ADVANCED">Advanced</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Price ($)</label>
            <input className="form-input" type="number" step="0.01" min="0" value={formData.price}
              onChange={e => setFormData({ ...formData, price: e.target.value })} required />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Thumbnail</label>
          {thumbnailPreview && (
            <img src={thumbnailPreview} alt="thumbnail preview"
              style={{ width: '100%', height: '160px', objectFit: 'cover', borderRadius: 'var(--radius-md)', marginBottom: '8px', border: '1px solid var(--border)' }} />
          )}
          <input type="file" accept="image/*" className="form-input" onChange={handleThumbnail} />
        </div>

        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.875rem' }}>
          <input type="checkbox" checked={formData.is_published}
            onChange={e => setFormData({ ...formData, is_published: e.target.checked })} />
          Publish immediately
        </label>

        <button type="submit" className="btn btn-primary btn-lg" style={{ marginTop: 'var(--sp-2)' }} disabled={saving}>
          {saving ? 'Creating…' : 'Create Course'}
        </button>
      </form>
    </div>
  );
}

export default CreateCourse;
