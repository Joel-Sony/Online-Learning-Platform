import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';

function EditCourse() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    level: '',
    language: '',
    price: '',
    is_published: false
  });
  const [modules, setModules] = useState([]);
  const [newModuleName, setNewModuleName] = useState('');

  useEffect(() => {
    api.get(`/courses/${id}/`)
      .then(res => {
        setFormData({
          title: res.data.title,
          description: res.data.description,
          category: res.data.category,
          level: res.data.level,
          language: res.data.language,
          price: res.data.price,
          is_published: res.data.is_published
        });
        setModules(res.data.modules || []);
      })
      .catch(err => console.error(err));
  }, [id]);

  const handleUpdateCourse = async (e) => {
    e.preventDefault();
    try {
      await api.patch(`/courses/${id}/`, formData);
      alert('Course updated');
    } catch (err) {
      alert('Update failed');
    }
  };

  const handleAddModule = async () => {
    if (!newModuleName) return;
    try {
      const res = await api.post('/modules/', {
        course: id,
        title: newModuleName,
        order: modules.length
      });
      setModules([...modules, { ...res.data, lessons: [] }]);
      setNewModuleName('');
    } catch (err) {
      alert('Failed to add module');
    }
  };

  return (
    <div style={{ textAlign: 'left', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '3rem' }}>
      <div>
        <h1>Edit Course Details</h1>
        <form onSubmit={handleUpdateCourse} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <input type="text" value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} required style={{ padding: '0.5rem' }} placeholder="Title" />
          <textarea value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} required style={{ padding: '0.5rem', height: '100px' }} placeholder="Description" />
          <input type="text" value={formData.category} onChange={e => setFormData({...formData, category: e.target.value})} style={{ padding: '0.5rem' }} placeholder="Category" />
          <input type="number" step="0.01" value={formData.price} onChange={e => setFormData({...formData, price: e.target.value})} style={{ padding: '0.5rem' }} placeholder="Price" />
          <label>
            <input type="checkbox" checked={formData.is_published} onChange={e => setFormData({...formData, is_published: e.target.checked})} />
            Is Published
          </label>
          <button type="submit" style={{ padding: '0.7rem', background: 'var(--accent)', color: 'white', border: 'none', borderRadius: '4px' }}>Save Course</button>
        </form>
      </div>

      <div>
        <h1>Curriculum (Modules)</h1>
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
          <input type="text" value={newModuleName} onChange={e => setNewModuleName(e.target.value)} placeholder="New Module Name" style={{ flex: 1, padding: '0.5rem' }} />
          <button onClick={handleAddModule} style={{ padding: '0.5rem 1rem' }}>Add</button>
        </div>
        
        {modules.map(module => (
          <div key={module.id} style={{ border: '1px solid var(--border)', padding: '1rem', marginBottom: '1rem', borderRadius: '4px' }}>
            <h3 style={{ margin: 0 }}>{module.title}</h3>
            <p style={{ fontSize: '0.8rem', color: 'gray' }}>{module.lessons?.length || 0} Lessons</p>
            {/* Simple lesson list could go here */}
          </div>
        ))}
      </div>
    </div>
  );
}

export default EditCourse;
