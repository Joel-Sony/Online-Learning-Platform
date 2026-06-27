import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api, { apiBase } from '../api';

/* ─── Helpers ─────────────────────────────────────────────────── */
function CheckIcon({ size = 14 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function PlayIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
      <polygon points="5 3 19 12 5 21 5 3" />
    </svg>
  );
}

function DocIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  );
}

/* ─── Lesson Icon ─────────────────────────────────────────────── */
function LessonTypeIcon({ type }) {
  if (type === 'VIDEO') return <PlayIcon />;
  return <DocIcon />;
}

/* ─── Video Embed ─────────────────────────────────────────────── */
function VideoEmbed({ url }) {
  if (!url) return null;

  // YouTube
  const ytMatch = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
  if (ytMatch) {
    return (
      <div style={{ position: 'relative', paddingBottom: '56.25%', height: 0, borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
        <iframe
          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none' }}
          src={`https://www.youtube.com/embed/${ytMatch[1]}`}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          title="Lesson video"
        />
      </div>
    );
  }

  // Vimeo
  const vimeoMatch = url.match(/vimeo\.com\/(\d+)/);
  if (vimeoMatch) {
    return (
      <div style={{ position: 'relative', paddingBottom: '56.25%', height: 0, borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
        <iframe
          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none' }}
          src={`https://player.vimeo.com/video/${vimeoMatch[1]}`}
          allow="autoplay; fullscreen; picture-in-picture"
          allowFullScreen
          title="Lesson video"
        />
      </div>
    );
  }

  // Raw video file
  return (
    <video controls style={{ width: '100%', borderRadius: 'var(--radius-lg)', background: '#000' }}>
      <source src={url} />
      Your browser does not support the video tag.
    </video>
  );
}

/* ─── Main Component ──────────────────────────────────────────── */
export default function LearnCourse() {
  const { id, lessonId } = useParams();
  const navigate = useNavigate();

  const [course, setCourse] = useState(null);
  const [completedLessons, setCompletedLessons] = useState({});
  const [currentLesson, setCurrentLesson] = useState(null);
  const [allLessons, setAllLessons] = useState([]);  // flat list for prev/next
  const [loading, setLoading] = useState(true);
  const [markingComplete, setMarkingComplete] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [expandedModules, setExpandedModules] = useState({});
  const [certificate, setCertificate] = useState(null);
  const [quizForModule, setQuizForModule] = useState(null); // shows inline quiz

  /* ── Fetch course + progress ─────────────────────────────── */
  const fetchData = useCallback(async () => {
    try {
      const [courseRes, progressRes, certRes] = await Promise.all([
        api.get(`/courses/${id}/`),
        api.get(`/progress/`),
        api.get('/certificates/')
      ]);

      const c = courseRes.data;
      setCourse(c);

      // Build flat lesson array
      const flat = [];
      (c.modules || []).forEach(mod => {
        (mod.lessons || []).forEach(l => flat.push({ ...l, moduleTitle: mod.title }));
      });
      setAllLessons(flat);

      // Build completed map
      const map = {};
      progressRes.data.forEach(p => { if (p.completed) map[p.lesson] = true; });
      setCompletedLessons(map);

      // Find cert for this course
      const cert = certRes.data.find(c => c.course === parseInt(id));
      if (cert) setCertificate(cert);

      // Expand all modules by default
      const expanded = {};
      (c.modules || []).forEach(m => { expanded[m.id] = true; });
      setExpandedModules(expanded);

      // Set active lesson
      if (flat.length > 0) {
        const target = lessonId ? flat.find(l => l.id === parseInt(lessonId)) : null;
        setCurrentLesson(target || flat[0]);
      }

      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  }, [id, lessonId]);

  useEffect(() => { fetchData(); }, [fetchData]);

  /* ── Navigate to a lesson ────────────────────────────────── */
  const goToLesson = (lesson) => {
    setCurrentLesson(lesson);
    setQuizForModule(null);
    // Persist last visited lesson so LearningDashboard can resume
    try { localStorage.setItem(`lastLesson_${id}`, lesson.id); } catch {}
    navigate(`/courses/${id}/learn/${lesson.id}`, { replace: true });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  /* ── Mark complete ───────────────────────────────────────── */
  const handleMarkComplete = async () => {
    if (!currentLesson || completedLessons[currentLesson.id]) return;
    setMarkingComplete(true);
    try {
      await api.post('/progress/mark_complete/', { lesson_id: currentLesson.id });
      const updated = { ...completedLessons, [currentLesson.id]: true };
      setCompletedLessons(updated);
      // Re-fetch to get updated certificate
      await fetchData();
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to mark lesson complete');
    } finally {
      setMarkingComplete(false);
    }
  };

  /* ── Prev / Next ─────────────────────────────────────────── */
  const currentIdx = allLessons.findIndex(l => l.id === currentLesson?.id);
  const prevLesson = currentIdx > 0 ? allLessons[currentIdx - 1] : null;
  const nextLesson = currentIdx < allLessons.length - 1 ? allLessons[currentIdx + 1] : null;

  /* ── Progress numbers ────────────────────────────────────── */
  const totalLessons = allLessons.length;
  const completedCount = Object.keys(completedLessons).length;
  const progressPct = totalLessons > 0 ? Math.round((completedCount / totalLessons) * 100) : 0;

  /* ── Loading / error ─────────────────────────────────────── */
  if (loading) return (
    <div className="page loading-state">
      <div className="spinner" />
      Loading course...
    </div>
  );

  if (!course) return (
    <div className="page empty-state">
      <h3>Course Not Found</h3>
      <Link to="/learning" className="btn btn-secondary" style={{ marginTop: '1rem' }}>Back to Dashboard</Link>
    </div>
  );

  /* ── Quiz module for current lesson ─────────────────────── */
  const currentModule = course.modules?.find(m =>
    m.lessons?.some(l => l.id === currentLesson?.id)
  );
  const moduleQuizzes = currentModule?.quizzes || [];

  /* ── Render ──────────────────────────────────────────────── */
  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 64px)', overflow: 'hidden', position: 'relative' }}>

      {/* ── Sidebar ── */}
      <aside style={{
        width: sidebarOpen ? '320px' : '0',
        minWidth: sidebarOpen ? '320px' : '0',
        overflow: 'hidden',
        transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
        borderRight: '1px solid var(--border)',
        background: 'var(--bg)',
        display: 'flex',
        flexDirection: 'column',
      }}>
        {/* Sidebar Header */}
        <div style={{ padding: '20px 20px 16px', borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
          <Link to={`/courses/${id}`} style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-tertiary)', fontSize: '0.78rem', marginBottom: '12px' }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15 18 9 12 15 6" /></svg>
            Back to Course
          </Link>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 600, lineHeight: 1.3, marginBottom: '12px', color: 'var(--text-primary)' }}>{course.title}</h3>

          {/* Progress bar */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>{completedCount}/{totalLessons} lessons</span>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--accent)' }}>{progressPct}%</span>
          </div>
          <div className="progress-track" style={{ height: '6px' }}>
            <div className="progress-fill" style={{ width: `${progressPct}%` }} />
          </div>
        </div>

        {/* Module List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '8px 0' }}>
          {(course.modules || []).map((mod, mIdx) => {
            const modCompleted = mod.lessons?.filter(l => completedLessons[l.id]).length || 0;
            const isExpanded = expandedModules[mod.id];
            return (
              <div key={mod.id}>
                {/* Module Header */}
                <button
                  onClick={() => setExpandedModules(prev => ({ ...prev, [mod.id]: !prev[mod.id] }))}
                  style={{
                    width: '100%', background: 'none', border: 'none', cursor: 'pointer',
                    padding: '12px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    gap: '8px', textAlign: 'left',
                  }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)', marginBottom: '2px' }}>
                      MODULE {mIdx + 1} · {modCompleted}/{mod.lessons?.length || 0}
                    </div>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {mod.title}
                    </div>
                  </div>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" strokeWidth="2" style={{ transform: isExpanded ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s', flexShrink: 0 }}>
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                </button>

                {/* Lesson Items */}
                {isExpanded && (
                  <div>
                    {(mod.lessons || []).map((lesson) => {
                      const isActive = currentLesson?.id === lesson.id;
                      const isDone = !!completedLessons[lesson.id];
                      return (
                        <button
                          key={lesson.id}
                          onClick={() => goToLesson(lesson)}
                          style={{
                            width: '100%', background: isActive ? 'var(--accent-light)' : 'none',
                            border: 'none', borderLeft: isActive ? '3px solid var(--accent)' : '3px solid transparent',
                            cursor: 'pointer', padding: '10px 20px 10px 17px',
                            display: 'flex', alignItems: 'center', gap: '10px', textAlign: 'left',
                            transition: 'all 0.15s ease',
                          }}
                          onMouseEnter={e => { if (!isActive) e.currentTarget.style.background = 'var(--bg-subtle)'; }}
                          onMouseLeave={e => { if (!isActive) e.currentTarget.style.background = 'none'; }}
                        >
                          <span style={{
                            width: '20px', height: '20px', borderRadius: '50%', flexShrink: 0,
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            background: isDone ? 'var(--success)' : isActive ? 'var(--accent)' : 'var(--surface)',
                            color: isDone || isActive ? '#fff' : 'var(--text-tertiary)',
                            border: isDone || isActive ? 'none' : '1px solid var(--border-strong)',
                          }}>
                            {isDone ? <CheckIcon size={10} /> : <LessonTypeIcon type={lesson.lesson_type} />}
                          </span>
                          <span style={{
                            fontSize: '0.83rem', lineHeight: 1.4, flex: 1,
                            color: isActive ? 'var(--accent)' : isDone ? 'var(--text-tertiary)' : 'var(--text-secondary)',
                            fontWeight: isActive ? 600 : 400,
                            textDecoration: isDone && !isActive ? 'line-through' : 'none',
                          }}>
                            {lesson.title}
                          </span>
                        </button>
                      );
                    })}

                    {/* Quiz rows */}
                    {(mod.quizzes || []).map(quiz => (
                      <Link
                        key={quiz.id}
                        to={`/quiz/${quiz.id}`}
                        style={{
                          display: 'flex', alignItems: 'center', gap: '10px',
                          padding: '10px 20px 10px 20px', textDecoration: 'none',
                          color: 'var(--text-secondary)', fontSize: '0.83rem',
                          borderLeft: '3px solid transparent',
                        }}
                        onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-subtle)'}
                        onMouseLeave={e => e.currentTarget.style.background = 'none'}
                      >
                        <span style={{
                          width: '20px', height: '20px', borderRadius: '50%', flexShrink: 0,
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          background: '#fffbeb', border: '1px solid #fde68a', color: 'var(--warning)',
                        }}>
                          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M9 11l3 3L22 4" /><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" /></svg>
                        </span>
                        <span style={{ fontStyle: 'italic' }}>Quiz: {quiz.title}</span>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Certificate Banner */}
        {certificate && (
          <div style={{ padding: '16px 20px', background: '#f0fdf4', borderTop: '1px solid #bbf7d0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '1.2rem' }}>🎓</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--success)', marginBottom: '4px' }}>Course Completed!</div>
                <a
                  href={`${apiBase}/certificates/${certificate.id}/download/?token=${localStorage.getItem('access')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ fontSize: '0.75rem', color: 'var(--success)', textDecoration: 'underline' }}
                >
                  Download Certificate →
                </a>
              </div>
            </div>
          </div>
        )}
      </aside>

      {/* ── Main Lesson Area ── */}
      <main style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>

        {/* Top bar */}
        <div style={{
          height: '52px', flexShrink: 0,
          borderBottom: '1px solid var(--border)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '0 24px', background: 'var(--bg)',
          position: 'sticky', top: 0, zIndex: 10,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button
              onClick={() => setSidebarOpen(o => !o)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '6px', borderRadius: 'var(--radius-sm)', display: 'flex', alignItems: 'center', color: 'var(--text-secondary)' }}
              title="Toggle curriculum sidebar"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" /><path d="M9 3v18" />
              </svg>
            </button>
            {currentLesson && (
              <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
                {currentLesson.moduleTitle && <span style={{ color: 'var(--text-tertiary)' }}>{currentLesson.moduleTitle} · </span>}
                {currentLesson.title}
              </span>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)' }}>{progressPct}% complete</span>
            {currentLesson && !completedLessons[currentLesson.id] && (
              <button
                className="btn btn-sm btn-secondary"
                onClick={handleMarkComplete}
                disabled={markingComplete}
              >
                {markingComplete ? 'Saving…' : '✓ Mark Complete'}
              </button>
            )}
            {currentLesson && completedLessons[currentLesson.id] && (
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', color: 'var(--success)', fontWeight: 500 }}>
                <CheckIcon /> Completed
              </span>
            )}
          </div>
        </div>

        {/* Lesson Content */}
        <div style={{ flex: 1, padding: '40px 48px', maxWidth: '900px', width: '100%', margin: '0 auto' }}>
          {currentLesson ? (
            <>
              <div style={{ marginBottom: '32px' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--accent)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase', letterSpacing: '0.08em', display: 'block', marginBottom: '8px' }}>
                  {currentLesson.lesson_type}
                </span>
                <h1 style={{ fontSize: 'clamp(1.5rem, 3vw, 2.25rem)', marginBottom: '0' }}>{currentLesson.title}</h1>
              </div>

              {/* Video */}
              {currentLesson.lesson_type === 'VIDEO' && currentLesson.video_url && (
                <div style={{ marginBottom: '32px' }}>
                  <VideoEmbed url={currentLesson.video_url} />
                </div>
              )}

              {/* File attachment */}
              {currentLesson.file && (
                <div style={{ marginBottom: '32px', padding: '20px 24px', background: 'var(--bg-subtle)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ width: '44px', height: '44px', background: 'var(--accent-light)', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <DocIcon />
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '2px' }}>Lesson Attachment</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)' }}>PDF / Document</div>
                  </div>
                  <a
                    href={currentLesson.file}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-sm btn-secondary"
                  >
                    Download
                  </a>
                </div>
              )}

              {/* No content placeholder */}
              {!currentLesson.video_url && !currentLesson.file && (
                <div style={{ padding: '48px 32px', background: 'var(--surface)', borderRadius: 'var(--radius-lg)', textAlign: 'center', marginBottom: '32px' }}>
                  <div style={{ fontSize: '2rem', marginBottom: '12px' }}>📄</div>
                  <p style={{ color: 'var(--text-tertiary)' }}>This lesson has no media content. Use the navigation below to proceed.</p>
                </div>
              )}

              {/* Module Quizzes */}
              {moduleQuizzes.length > 0 && (
                <div style={{ marginBottom: '32px', padding: '20px 24px', background: '#fffbeb', border: '1px solid #fde68a', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
                    <span style={{ fontSize: '1.1rem' }}>📝</span>
                    <h4 style={{ margin: 0, color: 'var(--warning)' }}>Module Quiz Available</h4>
                  </div>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '14px' }}>
                    Test your knowledge before moving on.
                  </p>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    {moduleQuizzes.map(quiz => (
                      <Link key={quiz.id} to={`/quiz/${quiz.id}`} className="btn btn-sm btn-secondary">
                        Take Quiz: {quiz.title}
                      </Link>
                    ))}
                  </div>
                </div>
              )}

              {/* Prev / Next navigation */}
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '32px', borderTop: '1px solid var(--border)' }}>
                {prevLesson ? (
                  <button onClick={() => goToLesson(prevLesson)} className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15 18 9 12 15 6" /></svg>
                    <span>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em', lineHeight: 1 }}>Previous</div>
                      <div style={{ fontWeight: 500, maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{prevLesson.title}</div>
                    </span>
                  </button>
                ) : <div />}

                {nextLesson ? (
                  <button onClick={() => goToLesson(nextLesson)} className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '0.68rem', color: 'rgba(255,255,255,0.7)', textTransform: 'uppercase', letterSpacing: '0.06em', lineHeight: 1 }}>Next</div>
                      <div style={{ fontWeight: 500, maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{nextLesson.title}</div>
                    </span>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 18 15 12 9 6" /></svg>
                  </button>
                ) : (
                  <div style={{ textAlign: 'right' }}>
                    {progressPct === 100 ? (
                      <div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--success)', fontWeight: 600, marginBottom: '8px' }}>🎉 You've completed the course!</div>
                        {certificate && (
                          <a
                            href={`${apiBase}/certificates/${certificate.id}/download/?token=${localStorage.getItem('access')}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn btn-primary"
                          >
                            🎓 Download Certificate
                          </a>
                        )}
                      </div>
                    ) : (
                      <button
                        className="btn btn-secondary"
                        onClick={handleMarkComplete}
                        disabled={completedLessons[currentLesson?.id]}
                      >
                        {completedLessons[currentLesson?.id] ? '✓ Completed' : 'Mark Complete to Finish'}
                      </button>
                    )}
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="empty-state">
              <h3>No lessons found</h3>
              <p>This course doesn't have any lessons yet.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
