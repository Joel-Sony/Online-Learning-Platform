import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api';
import FlagModal from '../components/FlagModal';

/* ─── tiny icon helpers (match the style used on the Learn page) ──── */
function PlayIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3" /></svg>
  );
}
function DocIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" />
    </svg>
  );
}
function CheckIcon({ size = 13 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}
function ClockIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
    </svg>
  );
}
function UsersIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}
function LessonTypeIcon({ type }) {
  if (type === 'VIDEO') return <PlayIcon />;
  return <DocIcon />;
}

function formatDuration(totalMinutes) {
  const mins = Number(totalMinutes) || 0;
  if (mins <= 0) return null;
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  if (h === 0) return `${m}m`;
  if (m === 0) return `${h}h`;
  return `${h}h ${m}m`;
}

function CourseDetails() {
  const { id } = useParams();
  const [course, setCourse] = useState(null);
  const [isEnrolled, setIsEnrolled] = useState(false);
  const [enrollmentId, setEnrollmentId] = useState(null);
  const [progress, setProgress] = useState({});
  const [certificate, setCertificate] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [ratingStats, setRatingStats] = useState({ avg_rating: 0, count: 0 });
  const [loading, setLoading] = useState(true);
  const [newReview, setNewReview] = useState({ rating: 5, review_text: '' });
  const [paymentError, setPaymentError] = useState('');
  const [enrolling, setEnrolling] = useState(false);
  const [flaggingReview, setFlaggingReview] = useState(null);
  const isLoggedIn = !!localStorage.getItem('access');

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    try {
      const courseRes = await api.get(`/courses/${id}/`);
      setCourse(courseRes.data);

      const statsRes = await api.get(`/reviews/course_ratings/?course_id=${id}`);
      setRatingStats(statsRes.data);

      const reviewsRes = await api.get(`/reviews/?course=${id}`);
      setReviews(reviewsRes.data);

      const hasToken = !!localStorage.getItem('access');
      if (hasToken) {
        const enrollRes = await api.get('/enrollments/');
        const enrollment = enrollRes.data.find(e => e.course === parseInt(id));
        if (enrollment) {
          setIsEnrolled(true);
          setEnrollmentId(enrollment.id);
          const lessonsProgRes = await api.get(`/progress/?course_id=${id}`);
          const progMap = {};
          lessonsProgRes.data.forEach(p => { if (p.completed) progMap[p.lesson] = true; });
          setProgress(progMap);
          const certRes = await api.get('/certificates/');
          const cert = certRes.data.find(c => c.course === parseInt(id));
          if (cert) setCertificate(cert);
        }
      }
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  const handleStripeEnroll = async () => {
    setPaymentError('');
    setEnrolling(true);
    try {
      const res = await api.post('/enrollments/create_stripe_checkout/', { course_id: id });
      if (res.data.url) window.location.href = res.data.url;
    } catch (err) {
      setPaymentError(err.response?.data?.error || 'Stripe payment failed.');
    } finally {
      setEnrolling(false);
    }
  };

  const handlePayPalEnroll = async () => {
    setPaymentError('');
    setEnrolling(true);
    try {
      const res = await api.post('/enrollments/create_paypal_order/', { course_id: id });
      if (res.data.approval_url) window.location.href = res.data.approval_url;
    } catch (err) {
      setPaymentError(err.response?.data?.error || 'PayPal payment failed.');
    } finally {
      setEnrolling(false);
    }
  };

  const handleFreeEnroll = async () => {
    setPaymentError('');
    setEnrolling(true);
    try {
      await api.post('/enrollments/enroll_free/', { course_id: id });
      fetchData();
    } catch (err) {
      setPaymentError(err.response?.data?.error || 'Enrollment failed.');
    } finally {
      setEnrolling(false);
    }
  };

  const handleMarkComplete = async (lessonId) => {
    try {
      await api.post('/progress/mark_complete/', { lesson_id: lessonId });
      setProgress({ ...progress, [lessonId]: true });
      fetchData();
    } catch (err) { console.error(err); }
  };

  const handleUnenroll = async () => {
    if (!window.confirm('Are you sure you want to unenroll from this course? You will lose access to its materials.')) return;
    try {
      await api.delete(`/enrollments/${enrollmentId}/`);
      setIsEnrolled(false);
      setEnrollmentId(null);
      setProgress({});
      setCertificate(null);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to unenroll.');
    }
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    try {
      await api.post('/reviews/', { ...newReview, course: id });
      setNewReview({ rating: 5, review_text: '' });
      fetchData();
    } catch (err) {
      alert(err.response?.data?.[0] || 'Failed to submit review');
    }
  };

  const downloadCertificate = () => {
    if (certificate) {
      const baseUrl = api.defaults.baseURL.endsWith('/') ? api.defaults.baseURL.slice(0, -1) : api.defaults.baseURL;
      const token = localStorage.getItem('access');
      window.open(`${baseUrl}/certificates/${certificate.id}/download/?token=${token}`, '_blank');
    }
  };

  if (loading) return (
    <div className="page loading-state">
      <div className="spinner"></div> Retrieving course details...
    </div>
  );
  if (!course) return (
    <div className="page empty-state">
      <h3>Course Unavailable</h3>
      <p>This material is currently not accessible.</p>
      <Link to="/courses" className="btn btn-primary" style={{ marginTop: '2rem' }}>Return to Catalog</Link>
    </div>
  );

  const lessonCount = (course.modules || []).reduce((sum, m) => sum + (m.lessons?.length || 0), 0);
  const quizCount = (course.modules || []).reduce((sum, m) => sum + (m.quizzes?.length || 0), 0);
  const clientDuration = (course.modules || []).reduce(
    (sum, m) => sum + (m.lessons?.reduce((s, l) => s + (l.duration_minutes || 0), 0) || 0), 0
  );
  const durationLabel = formatDuration(course.total_duration || clientDuration);
  const completedCount = Object.keys(progress).length;
  const coursePct = lessonCount > 0 ? Math.round((completedCount / lessonCount) * 100) : 0;

  return (
    <>
      <div className="page" style={{ maxWidth: '1120px' }}>

        {/* ── Hero ── */}
        <div style={{
          display: 'flex', gap: '3rem', flexWrap: 'wrap',
          paddingBottom: '3rem', marginBottom: '3rem', borderBottom: '1px solid var(--border)',
        }}>
          <div style={{ flex: '1 1 420px', minWidth: 0 }}>
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
              <span className="badge badge-category">{course.category}</span>
              <span className="badge badge-default">{course.level}</span>
              {course.is_free && <span className="badge badge-success">Free</span>}
            </div>

            <h1 style={{ marginBottom: '1rem', fontSize: 'clamp(2rem, 4.2vw, 3rem)' }}>{course.title}</h1>
            <p style={{ fontSize: '1.05rem', lineHeight: '1.75', color: 'var(--text-secondary)', marginBottom: '1.75rem', maxWidth: '640px' }}>
              {course.description}
            </p>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap', fontSize: '0.85rem', color: 'var(--text-tertiary)' }}>
              <div className="rating-display">
                <span className="stars">★★★★★</span>
                <span className="rating-score">{ratingStats.avg_rating ? ratingStats.avg_rating.toFixed(1) : 'New'}</span>
                <span className="rating-count">({ratingStats.count} review{ratingStats.count === 1 ? '' : 's'})</span>
              </div>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <DocIcon /> {lessonCount} lesson{lessonCount === 1 ? '' : 's'}{quizCount > 0 && ` · ${quizCount} quiz${quizCount === 1 ? '' : 'zes'}`}
              </span>
              {durationLabel && (
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><ClockIcon /> {durationLabel}</span>
              )}
              <span>{course.language}</span>
            </div>

            {/* Instructor */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '2rem' }}>
              <div style={{
                width: '40px', height: '40px', borderRadius: '50%',
                background: 'var(--accent)', color: '#fff',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 700, fontSize: '1rem', flexShrink: 0,
              }}>
                {course.mentor_name ? course.mentor_name.charAt(0).toUpperCase() : 'M'}
              </div>
              <div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Instructor</div>
                <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{course.mentor_name}</div>
              </div>
            </div>
          </div>

          {/* Thumbnail */}
          <div style={{ flex: '1 1 380px', minWidth: '280px' }}>
            <div style={{
              width: '100%', aspectRatio: '16 / 10', borderRadius: 'var(--radius-xl)',
              overflow: 'hidden', boxShadow: 'var(--shadow-lg)', border: '1px solid var(--border)',
              background: 'var(--surface)',
            }}>
              {course.thumbnail ? (
                <img src={course.thumbnail} alt={course.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              ) : (
                <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-tertiary)' }}>
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" /><circle cx="8.5" cy="8.5" r="1.5" /><polyline points="21 15 16 10 5 21" />
                  </svg>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ── Body: syllabus + sidebar ── */}
        <div style={{ display: 'flex', gap: '3rem', flexWrap: 'wrap', alignItems: 'flex-start' }}>

          {/* Syllabus */}
          <div style={{ flex: '2 1 500px', minWidth: 0 }}>
            <h2 style={{ marginBottom: '1.75rem', fontSize: '1.5rem' }}>Syllabus</h2>

            {isEnrolled && lessonCount > 0 && (
              <div className="card" style={{ padding: '1.25rem 1.5rem', marginBottom: '1.75rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '6px' }}>
                    <span style={{ color: 'var(--text-tertiary)' }}>Your progress</span>
                    <span style={{ fontWeight: 600, color: 'var(--accent)' }}>{completedCount}/{lessonCount} · {coursePct}%</span>
                  </div>
                  <div className="progress-track"><div className="progress-fill" style={{ width: `${coursePct}%` }} /></div>
                </div>
              </div>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {course.modules?.map((module, index) => (
                <div key={module.id} className="card" style={{ padding: 0, overflow: 'hidden' }}>
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: '1rem',
                    padding: '1.1rem 1.5rem', background: 'var(--bg-subtle)', borderBottom: '1px solid var(--border)',
                  }}>
                    <span className="mono" style={{ color: 'var(--accent)', fontSize: '0.85rem' }}>
                      {(index + 1).toString().padStart(2, '0')}
                    </span>
                    <h3 style={{ margin: 0, fontSize: '1.05rem', flex: 1 }}>{module.title}</h3>
                    <span className="mono" style={{ color: 'var(--text-tertiary)', fontSize: '0.72rem' }}>
                      {module.lessons?.length || 0} lesson{module.lessons?.length === 1 ? '' : 's'}
                    </span>
                  </div>

                  <div>
                    {module.lessons?.map(lesson => {
                      const done = !!progress[lesson.id];
                      return (
                        <div key={lesson.id} style={{
                          padding: '0.85rem 1.5rem', display: 'flex', alignItems: 'center', gap: '0.85rem',
                          borderBottom: '1px solid var(--border)',
                        }}>
                          <span style={{
                            width: '22px', height: '22px', borderRadius: '50%', flexShrink: 0,
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            background: done ? 'var(--success)' : 'var(--surface)',
                            color: done ? '#fff' : 'var(--text-tertiary)',
                            border: done ? 'none' : '1px solid var(--border-strong)',
                          }}>
                            {done ? <CheckIcon size={11} /> : <LessonTypeIcon type={lesson.lesson_type} />}
                          </span>
                          <span style={{
                            flex: 1, fontSize: '0.92rem',
                            color: done ? 'var(--text-tertiary)' : 'var(--text-primary)',
                            textDecoration: done ? 'line-through' : 'none',
                          }}>
                            {lesson.title}
                          </span>
                          <span className="badge badge-default">{lesson.lesson_type}</span>
                          {isEnrolled && !done && (
                            <button onClick={() => handleMarkComplete(lesson.id)} className="btn btn-ghost btn-sm">
                              Mark Done
                            </button>
                          )}
                        </div>
                      );
                    })}

                    {module.quizzes?.map(quiz => (
                      <div key={quiz.id} style={{
                        padding: '0.85rem 1.5rem', display: 'flex', alignItems: 'center', gap: '0.85rem',
                        borderBottom: '1px solid var(--border)', background: '#fffbeb',
                      }}>
                        <span style={{
                          width: '22px', height: '22px', borderRadius: '50%', flexShrink: 0,
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          background: '#fde68a', color: 'var(--warning)',
                        }}>
                          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M9 11l3 3L22 4" /><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" /></svg>
                        </span>
                        <span style={{ flex: 1, fontSize: '0.92rem', fontWeight: 500, color: 'var(--text-primary)' }}>
                          Quiz: {quiz.title}
                        </span>
                        <span className="mono" style={{ color: 'var(--text-tertiary)', fontSize: '0.7rem' }}>Pass {quiz.passing_score}%</span>
                        {isEnrolled && (
                          <Link to={`/quiz/${quiz.id}`} className="btn btn-secondary btn-sm">Take Quiz</Link>
                        )}
                      </div>
                    ))}

                    {(!module.lessons || module.lessons.length === 0) && (!module.quizzes || module.quizzes.length === 0) && (
                      <div style={{ padding: '1rem 1.5rem', color: 'var(--text-tertiary)', fontSize: '0.9rem' }}>
                        Materials pending.
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {(!course.modules || course.modules.length === 0) && (
                <div className="card empty-state">The syllabus is currently being finalized.</div>
              )}
            </div>

            {/* Reviews */}
            <div style={{ marginTop: '3.5rem' }}>
              <h2 style={{ marginBottom: '1.75rem', fontSize: '1.5rem' }}>Student Reviews</h2>

              {isEnrolled && (
                <div className="card" style={{ marginBottom: '2rem' }}>
                  <form onSubmit={handleSubmitReview} className="form-stack">
                    <div className="form-group">
                      <label className="form-label">Your rating</label>
                      <select
                        className="form-select"
                        value={newReview.rating}
                        onChange={e => setNewReview({ ...newReview, rating: e.target.value })}
                      >
                        {[5, 4, 3, 2, 1].map(n => <option key={n} value={n}>{n} Stars — {['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'][n - 1]}</option>)}
                      </select>
                    </div>
                    <div className="form-group">
                      <label className="form-label">Your review</label>
                      <textarea
                        className="form-textarea"
                        placeholder="Share your perspective..."
                        value={newReview.review_text}
                        onChange={e => setNewReview({ ...newReview, review_text: e.target.value })}
                        required
                      />
                    </div>
                    <button type="submit" className="btn btn-primary" style={{ alignSelf: 'flex-start' }}>Submit Review</button>
                  </form>
                </div>
              )}

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                {reviews.map(review => (
                  <div key={review.id} className="card" style={{ display: 'flex', gap: '1rem' }}>
                    <div style={{
                      width: '36px', height: '36px', borderRadius: '50%', flexShrink: 0,
                      background: 'var(--surface)', color: 'var(--text-secondary)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem',
                    }}>
                      {review.student_name ? review.student_name.charAt(0).toUpperCase() : '?'}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '0.4rem', gap: '0.5rem' }}>
                        <strong style={{ color: 'var(--text-primary)' }}>{review.student_name}</strong>
                        <span className="badge badge-warning">{review.rating}/5 ★</span>
                      </div>
                      <p style={{ fontSize: '0.92rem', lineHeight: '1.6', margin: '0 0 0.5rem 0', color: 'var(--text-secondary)' }}>
                        {review.review_text}
                      </p>
                      <button
                        onClick={() => setFlaggingReview(review)}
                        className="mono"
                        style={{ background: 'none', border: 'none', color: 'var(--text-tertiary)', cursor: 'pointer', padding: 0, textDecoration: 'underline', fontSize: '0.7rem' }}
                      >
                        Flag
                      </button>
                    </div>
                  </div>
                ))}
                {reviews.length === 0 && (
                  <div className="card empty-state" style={{ fontStyle: 'italic' }}>No feedback provided yet.</div>
                )}
              </div>
            </div>
          </div>

          {/* Enrollment card — sits in normal document flow (not sticky), so it
              scrolls naturally with the page instead of pinning to the viewport. */}
          <div style={{ flex: '1 1 300px', minWidth: '280px' }}>
            <div className="card" style={{ padding: '2rem' }}>
              {isEnrolled ? (
                <div>
                  <span className="badge badge-success" style={{ marginBottom: '1rem' }}>Enrolled</span>
                  <h4 style={{ marginBottom: '1.5rem', fontSize: '1.3rem' }}>Continue your progress</h4>
                  <div className="form-stack">
                    <Link to={`/courses/${id}/learn`} className="btn btn-primary" style={{ width: '100%' }}>
                      ▶ Continue Learning
                    </Link>
                    <Link to={`/courses/${id}/qa`} className="btn btn-secondary" style={{ width: '100%' }}>
                      Enter Q&A Forum
                    </Link>
                    {certificate && (
                      <button onClick={downloadCertificate} className="btn btn-secondary" style={{ width: '100%' }}>
                        🎓 Download Certificate
                      </button>
                    )}
                    <button onClick={handleUnenroll} className="btn btn-ghost" style={{ width: '100%', color: '#d32f2f' }}>
                      Unenroll
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  {!isLoggedIn ? (
                    <div style={{ textAlign: 'center' }}>
                      <h4 style={{ marginBottom: '0.75rem' }}>Ready to start?</h4>
                      <p style={{ marginBottom: '1.5rem', fontSize: '0.9rem', color: 'var(--text-tertiary)' }}>Sign in to enrol in this course.</p>
                      <Link to="/login" className="btn btn-primary" style={{ width: '100%' }}>Sign In</Link>
                    </div>
                  ) : (
                    <div>
                      <span className="label" style={{ display: 'block', marginBottom: '0.4rem' }}>Price</span>
                      <h4 style={{ marginBottom: '1.5rem', fontSize: '2.25rem', fontFamily: 'var(--font-display)' }}>
                        {course.is_free ? 'Free' : `$${course.price}`}
                      </h4>

                      {course.is_free ? (
                        <button onClick={handleFreeEnroll} disabled={enrolling} className="btn btn-primary btn-lg" style={{ width: '100%' }}>
                          {enrolling ? 'Processing…' : 'Enrol Now'}
                        </button>
                      ) : (
                        <div className="form-stack">
                          <button onClick={handleStripeEnroll} disabled={enrolling} className="btn btn-primary btn-lg" style={{ width: '100%' }}>
                            {enrolling ? 'Processing…' : 'Pay with Card (Stripe)'}
                          </button>
                          <button onClick={handlePayPalEnroll} disabled={enrolling} className="btn btn-secondary" style={{ width: '100%' }}>
                            {enrolling ? 'Processing…' : 'Pay with PayPal'}
                          </button>
                        </div>
                      )}

                      <div style={{ marginTop: '1.75rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border)', display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                          <DocIcon /> {lessonCount} lesson{lessonCount === 1 ? '' : 's'}{quizCount > 0 ? ` · ${quizCount} quiz${quizCount === 1 ? '' : 'zes'}` : ''}
                        </div>
                        {durationLabel && (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                            <ClockIcon /> {durationLabel} of content
                          </div>
                        )}
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                          <UsersIcon /> Full lifetime access
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                          🎓 Certificate on completion
                        </div>
                      </div>
                    </div>
                  )}
                  {paymentError && (
                    <div className="form-error" style={{ marginTop: '1.25rem', fontSize: '0.8rem' }}>
                      {paymentError}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <FlagModal
        isOpen={!!flaggingReview}
        onClose={() => setFlaggingReview(null)}
        onSubmit={async (reason) => {
          if (!flaggingReview) return;
          await api.post('/reports/', { review: flaggingReview.id, reason });
          setFlaggingReview(null);
          fetchData();
        }}
        title="Flag Review"
        label="Why are you flagging this review as inappropriate?"
      />
    </>
  );
}

export default CourseDetails;
