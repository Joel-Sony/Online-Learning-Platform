import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../api';
import RichTextEditor from '../components/RichTextEditor';

/* ─── tiny icon helpers ─────────────────────────────────────── */
const ChevronUp = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="18 15 12 9 6 15" /></svg>
);
const ChevronDown = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="6 9 12 15 18 9" /></svg>
);

/* ─── Lesson Row ─────────────────────────────────────────────── */
function LessonRow({ lesson, idx, total, onMoveUp, onMoveDown, onDelete }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '10px',
      padding: '10px 14px', background: 'var(--bg)', border: '1px solid var(--border)',
      borderRadius: 'var(--radius-sm)', marginBottom: '6px',
    }}>
      <span className="mono" style={{ color: 'var(--text-tertiary)', fontSize: '0.7rem', width: '20px', textAlign: 'center' }}>{idx + 1}</span>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-primary)' }}>{lesson.title}</div>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)' }}>{lesson.lesson_type}</div>
      </div>
      <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
        <button onClick={onMoveUp} disabled={idx === 0} style={iconBtn}><ChevronUp /></button>
        <button onClick={onMoveDown} disabled={idx === total - 1} style={iconBtn}><ChevronDown /></button>
        <button onClick={onDelete} style={{ ...iconBtn, color: '#d32f2f' }}>✕</button>
      </div>
    </div>
  );
}

const iconBtn = {
  background: 'none', border: 'none', cursor: 'pointer', padding: '4px',
  borderRadius: '4px', display: 'flex', alignItems: 'center', color: 'var(--text-tertiary)',
  transition: 'all 0.15s',
};

/* ─── Module Section ─────────────────────────────────────────── */
function ModuleSection({ module, mIdx, totalModules, onMoveUp, onMoveDown, onDeleteModule, onRefresh }) {
  const [expanded, setExpanded] = useState(true);
  const [addingLesson, setAddingLesson] = useState(false);
  const [addingQuiz, setAddingQuiz] = useState(false);
  const [lessonForm, setLessonForm] = useState({ title: '', lesson_type: 'VIDEO', video_url: '', file: null, content: '', duration_minutes: 0 });
  const [quizForm, setQuizForm] = useState({ title: '', description: '', passing_score: 60 });
  const [saving, setSaving] = useState(false);

  const handleSaveLesson = async () => {
    if (!lessonForm.title.trim()) return alert('Lesson title is required');
    setSaving(true);
    try {
      const data = new FormData();
      data.append('module', module.id);
      data.append('title', lessonForm.title.trim());
      data.append('lesson_type', lessonForm.lesson_type);
      data.append('order', module.lessons?.length || 0);
      data.append('duration_minutes', lessonForm.duration_minutes || 0);
      if (lessonForm.lesson_type === 'VIDEO') {
        if (lessonForm.video_url) data.append('video_url', lessonForm.video_url);
      } else {
        if (lessonForm.file) data.append('file', lessonForm.file);
      }
      data.append('content', lessonForm.content || '');
      await api.post('/lessons/', data, { headers: { 'Content-Type': 'multipart/form-data' } });
      setLessonForm({ title: '', lesson_type: 'VIDEO', video_url: '', file: null, content: '', duration_minutes: 0 });
      setAddingLesson(false);
      onRefresh();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to add lesson');
    } finally { setSaving(false); }
  };

  const handleSaveQuiz = async () => {
    if (!quizForm.title.trim()) return alert('Quiz title is required');
    setSaving(true);
    try {
      await api.post('/quizzes/', { module: module.id, ...quizForm, passing_score: parseInt(quizForm.passing_score) });
      setQuizForm({ title: '', description: '', passing_score: 60 });
      setAddingQuiz(false);
      onRefresh();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to add quiz');
    } finally { setSaving(false); }
  };

  const handleDeleteLesson = async (lessonId) => {
    if (!window.confirm('Delete this lesson?')) return;
    try { await api.delete(`/lessons/${lessonId}/`); onRefresh(); } catch { alert('Failed to delete lesson'); }
  };

  const handleMoveLesson = async (lesson, direction) => {
    const lessons = [...(module.lessons || [])].sort((a, b) => a.order - b.order);
    const idx = lessons.findIndex(l => l.id === lesson.id);
    const swapIdx = idx + direction;
    if (swapIdx < 0 || swapIdx >= lessons.length) return;
    try {
      await Promise.all([
        api.patch(`/lessons/${lessons[idx].id}/`, { order: swapIdx }),
        api.patch(`/lessons/${lessons[swapIdx].id}/`, { order: idx }),
      ]);
      onRefresh();
    } catch { alert('Failed to reorder'); }
  };

  return (
    <div style={{ border: '1px solid var(--border-strong)', borderRadius: 'var(--radius-md)', background: 'var(--bg)', marginBottom: '16px' }}>
      {/* Module Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '14px 16px', borderBottom: expanded ? '1px solid var(--border)' : 'none' }}>
        <span className="mono" style={{ color: 'var(--accent)', fontSize: '0.75rem', width: '22px' }}>
          {(mIdx + 1).toString().padStart(2, '0')}
        </span>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)' }}>{module.title}</div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)' }}>
            {module.lessons?.length || 0} lesson{module.lessons?.length !== 1 ? 's' : ''} · {module.quizzes?.length || 0} quiz
          </div>
        </div>
        <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
          <button onClick={onMoveUp} disabled={mIdx === 0} style={iconBtn}><ChevronUp /></button>
          <button onClick={onMoveDown} disabled={mIdx === totalModules - 1} style={iconBtn}><ChevronDown /></button>
          <button onClick={() => setExpanded(e => !e)} style={{ ...iconBtn, marginLeft: '4px' }}>
            {expanded ? <ChevronUp /> : <ChevronDown />}
          </button>
          <button onClick={onDeleteModule} style={{ ...iconBtn, color: '#d32f2f', marginLeft: '4px' }}>✕</button>
        </div>
      </div>

      {expanded && (
        <div style={{ padding: '14px 16px' }}>
          {/* Lessons */}
          {(module.lessons || []).map((lesson, lIdx) => (
            <LessonRow
              key={lesson.id}
              lesson={lesson}
              idx={lIdx}
              total={module.lessons.length}
              onMoveUp={() => handleMoveLesson(lesson, -1)}
              onMoveDown={() => handleMoveLesson(lesson, 1)}
              onDelete={() => handleDeleteLesson(lesson.id)}
            />
          ))}

          {/* Quizzes */}
          {(module.quizzes || []).map(quiz => (
            <div key={quiz.id} style={{
              display: 'flex', alignItems: 'center', gap: '10px',
              padding: '10px 14px', background: '#fffbeb', border: '1px solid #fde68a',
              borderRadius: 'var(--radius-sm)', marginBottom: '6px',
            }}>
              <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', flex: 1 }}>
                📝 {quiz.title} <span className="mono" style={{ color: 'var(--text-tertiary)' }}>(Pass: {quiz.passing_score}%)</span>
              </span>
              <Link to={`/mentor/quiz/${quiz.id}/edit`} className="btn btn-sm btn-secondary">Edit Questions</Link>
            </div>
          ))}

          {/* Add Lesson Form */}
          {addingLesson && (
            <div style={{ marginTop: '12px', padding: '16px', background: 'var(--surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border)' }} className="form-stack">
              <h4 style={{ marginBottom: '0' }}>New Lesson</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '8px', alignItems: 'end' }}>
                <input className="form-input" placeholder="Lesson title" value={lessonForm.title} onChange={e => setLessonForm(f => ({ ...f, title: e.target.value }))} />
                <select className="form-select" style={{ width: '140px' }} value={lessonForm.lesson_type} onChange={e => setLessonForm(f => ({ ...f, lesson_type: e.target.value }))}>
                  <option value="VIDEO">Video</option>
                  <option value="PDF">PDF</option>
                  <option value="DOCUMENT">Document</option>
                </select>
              </div>
              {lessonForm.lesson_type === 'VIDEO' ? (
                <input className="form-input" placeholder="Video URL (YouTube, Vimeo, or direct)" value={lessonForm.video_url} onChange={e => setLessonForm(f => ({ ...f, video_url: e.target.value }))} />
              ) : (
                <input type="file" className="form-input" onChange={e => setLessonForm(f => ({ ...f, file: e.target.files[0] }))} />
              )}
              <div>
                <label className="form-label" style={{ marginBottom: '6px' }}>Lesson Text Content</label>
                <RichTextEditor
                  value={lessonForm.content}
                  onChange={(html) => setLessonForm(f => ({ ...f, content: html }))}
                  placeholder="Write your lesson content here..."
                  minHeight="150px"
                />
              </div>
              <input className="form-input" type="number" placeholder="Duration (minutes)" value={lessonForm.duration_minutes} onChange={e => setLessonForm(f => ({ ...f, duration_minutes: e.target.value }))} />
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="btn btn-primary btn-sm" onClick={handleSaveLesson} disabled={saving}>{saving ? 'Saving…' : 'Add Lesson'}</button>
                <button className="btn btn-ghost btn-sm" onClick={() => setAddingLesson(false)}>Cancel</button>
              </div>
            </div>
          )}

          {/* Add Quiz Form */}
          {addingQuiz && (
            <div style={{ marginTop: '12px', padding: '16px', background: '#fffbeb', borderRadius: 'var(--radius-md)', border: '1px solid #fde68a' }} className="form-stack">
              <h4 style={{ marginBottom: '0' }}>New Quiz</h4>
              <input className="form-input" placeholder="Quiz title" value={quizForm.title} onChange={e => setQuizForm(f => ({ ...f, title: e.target.value }))} />
              <input className="form-input" placeholder="Description (optional)" value={quizForm.description} onChange={e => setQuizForm(f => ({ ...f, description: e.target.value }))} />
              <input className="form-input" type="number" placeholder="Passing score (%)" value={quizForm.passing_score} onChange={e => setQuizForm(f => ({ ...f, passing_score: e.target.value }))} />
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="btn btn-primary btn-sm" onClick={handleSaveQuiz} disabled={saving}>{saving ? 'Saving…' : 'Add Quiz'}</button>
                <button className="btn btn-ghost btn-sm" onClick={() => setAddingQuiz(false)}>Cancel</button>
              </div>
            </div>
          )}

          {/* Action buttons */}
          {!addingLesson && !addingQuiz && (
            <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
              <button className="btn btn-sm btn-secondary" onClick={() => setAddingLesson(true)}>+ Lesson / Attachment</button>
              <button className="btn btn-sm btn-secondary" onClick={() => setAddingQuiz(true)}>+ Quiz</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ─── Main EditCourse ────────────────────────────────────────── */
export default function EditCourse() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    title: '', description: '', category: '',
    level: 'BEGINNER', language: 'English', price: '', tags: '', is_free: false, is_published: false,
  });
  const [thumbnail, setThumbnail] = useState(null);
  const [thumbnailPreview, setThumbnailPreview] = useState(null);
  const [modules, setModules] = useState([]);
  const [newModuleName, setNewModuleName] = useState('');
  const [saving, setSaving] = useState(false);
  const [addingModule, setAddingModule] = useState(false);

  const fetchCourse = async () => {
    try {
      const res = await api.get(`/courses/${id}/`);
      const d = res.data;
      setFormData({
        title: d.title || '',
        description: d.description || '',
        category: d.category || '',
        level: d.level || 'BEGINNER',
        language: d.language || 'English',
        price: d.price || '',
        tags: d.tags || '',
        is_free: d.is_free || false,
        is_published: d.is_published || false,
      });
      if (d.thumbnail) setThumbnailPreview(d.thumbnail);
      setModules(d.modules || []);
    } catch { alert('Failed to load course'); }
  };

  useEffect(() => { fetchCourse(); }, [id]);

  const handleUpdateCourse = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (thumbnail) {
        // Multipart only when uploading a new thumbnail
        const data = new FormData();
        Object.keys(formData).forEach(k => data.append(k, formData[k]));
        data.append('thumbnail', thumbnail);
        await api.patch(`/courses/${id}/`, data, { headers: { 'Content-Type': 'multipart/form-data' } });
      } else {
        // Plain JSON — avoids "false" string being rejected by BooleanField
        await api.patch(`/courses/${id}/`, formData);
      }
      alert('Course updated successfully!');
    } catch (err) {
      const detail = err.response?.data;
      alert('Update failed: ' + (detail ? JSON.stringify(detail) : err.message));
    } finally { setSaving(false); }
  };

  const handleAddModule = async () => {
    if (!newModuleName.trim()) return;
    setAddingModule(true);
    try {
      await api.post('/modules/', { course: id, title: newModuleName.trim(), order: modules.length });
      setNewModuleName('');
      fetchCourse();
    } catch { alert('Failed to add module'); }
    finally { setAddingModule(false); }
  };

  const handleDeleteModule = async (moduleId) => {
    if (!window.confirm('Delete this module and ALL its lessons?')) return;
    try { await api.delete(`/modules/${moduleId}/`); fetchCourse(); } catch { alert('Failed to delete module'); }
  };

  const handleMoveModule = async (module, direction) => {
    const sorted = [...modules].sort((a, b) => a.order - b.order);
    const idx = sorted.findIndex(m => m.id === module.id);
    const swapIdx = idx + direction;
    if (swapIdx < 0 || swapIdx >= sorted.length) return;
    try {
      await Promise.all([
        api.patch(`/modules/${sorted[idx].id}/`, { order: swapIdx }),
        api.patch(`/modules/${sorted[swapIdx].id}/`, { order: idx }),
      ]);
      fetchCourse();
    } catch { alert('Failed to reorder modules'); }
  };

  const handleThumbnailChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setThumbnail(file);
    setThumbnailPreview(URL.createObjectURL(file));
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 48px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px', paddingBottom: '24px', borderBottom: '1px solid var(--border)' }}>
        <div>
          <Link to="/mentor" style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)' }}>← Studio</Link>
          <h1 style={{ marginTop: '8px', marginBottom: '0' }}>Edit Course</h1>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <Link to={`/courses/${id}`} className="btn btn-secondary btn-sm">Preview</Link>
          <button className="btn btn-primary btn-sm" form="course-form" type="submit" disabled={saving}>
            {saving ? 'Saving…' : 'Save Changes'}
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '48px' }}>

        {/* ── Left: Course Details ── */}
        <div>
          <h2 style={{ fontSize: '1.1rem', marginBottom: '20px' }}>Course Details</h2>
          <form id="course-form" onSubmit={handleUpdateCourse} className="form-stack">

            <div className="form-group">
              <label className="form-label">Title</label>
              <input className="form-input" value={formData.title} onChange={e => setFormData(f => ({ ...f, title: e.target.value }))} required />
            </div>

            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea className="form-textarea" value={formData.description} onChange={e => setFormData(f => ({ ...f, description: e.target.value }))} required />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div className="form-group">
                <label className="form-label">Category</label>
                <input className="form-input" value={formData.category} onChange={e => setFormData(f => ({ ...f, category: e.target.value }))} />
              </div>
              <div className="form-group">
                <label className="form-label">Language</label>
                <input className="form-input" value={formData.language} onChange={e => setFormData(f => ({ ...f, language: e.target.value }))} />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div className="form-group">
                <label className="form-label">Level</label>
                <select className="form-select" value={formData.level} onChange={e => setFormData(f => ({ ...f, level: e.target.value }))}>
                  <option value="BEGINNER">Beginner</option>
                  <option value="INTERMEDIATE">Intermediate</option>
                  <option value="ADVANCED">Advanced</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Price ($)</label>
                <input className="form-input" type="number" step="0.01" value={formData.price} onChange={e => setFormData(f => ({ ...f, price: e.target.value }))} />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Tags (comma-separated)</label>
              <input className="form-input" placeholder="python, web, beginner" value={formData.tags} onChange={e => setFormData(f => ({ ...f, tags: e.target.value }))} />
            </div>

            {/* Thumbnail */}
            <div className="form-group">
              <label className="form-label">Thumbnail</label>
              {thumbnailPreview && (
                <img src={thumbnailPreview} alt="thumbnail" style={{ width: '100%', height: '160px', objectFit: 'cover', borderRadius: 'var(--radius-md)', marginBottom: '8px', border: '1px solid var(--border)' }} />
              )}
              <input type="file" accept="image/*" className="form-input" onChange={handleThumbnailChange} />
            </div>

            {/* Toggles */}
            <div style={{ display: 'flex', gap: '24px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.875rem' }}>
                <input type="checkbox" checked={formData.is_free} onChange={e => setFormData(f => ({ ...f, is_free: e.target.checked, price: e.target.checked ? '0.00' : f.price }))} />
                Free Course
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.875rem' }}>
                <input type="checkbox" checked={formData.is_published} onChange={e => setFormData(f => ({ ...f, is_published: e.target.checked }))} />
                Published
              </label>
            </div>

          </form>
        </div>

        {/* ── Right: Curriculum Builder ── */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '20px' }}>
            <h2 style={{ fontSize: '1.1rem', marginBottom: 0 }}>Curriculum</h2>
            <span className="mono" style={{ color: 'var(--text-tertiary)', fontSize: '0.75rem' }}>
              {modules.length} module{modules.length !== 1 ? 's' : ''}
            </span>
          </div>

          {/* Module List */}
          {modules.length === 0 && (
            <div style={{ padding: '32px', border: '1px dashed var(--border-strong)', borderRadius: 'var(--radius-md)', textAlign: 'center', color: 'var(--text-tertiary)', marginBottom: '16px' }}>
              No modules yet. Add your first module below.
            </div>
          )}

          {modules.map((mod, mIdx) => (
            <ModuleSection
              key={mod.id}
              module={mod}
              mIdx={mIdx}
              totalModules={modules.length}
              onMoveUp={() => handleMoveModule(mod, -1)}
              onMoveDown={() => handleMoveModule(mod, 1)}
              onDeleteModule={() => handleDeleteModule(mod.id)}
              onRefresh={fetchCourse}
            />
          ))}

          {/* Add Module */}
          <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
            <input
              className="form-input"
              placeholder="New module title…"
              value={newModuleName}
              onChange={e => setNewModuleName(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), handleAddModule())}
              style={{ flex: 1 }}
            />
            <button className="btn btn-secondary" onClick={handleAddModule} disabled={addingModule || !newModuleName.trim()}>
              {addingModule ? '…' : '+ Add Module'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
