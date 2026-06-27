import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api';

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
      window.open(`${baseUrl}/certificates/${certificate.id}/download/`, '_blank');
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

  return (
    <div className="page" style={{ maxWidth: '1000px', paddingTop: '2rem' }}>
      {/* Header Section */}
      <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginBottom: '2rem' }}>
          <span className="mono" style={{ color: 'var(--accent)' }}>{course.category}</span>
          <span className="mono" style={{ color: 'var(--text-muted)' }}>/</span>
          <span className="mono" style={{ color: 'var(--text-muted)' }}>{course.level}</span>
        </div>
        <h1 style={{ marginBottom: '1.5rem', fontSize: 'clamp(2.5rem, 6vw, 4.5rem)' }}>{course.title}</h1>
        <p style={{ fontSize: '1.1rem', color: 'var(--text)', maxWidth: '600px', margin: '0 auto', lineHeight: '1.8' }}>
          {course.description}
        </p>
      </div>

      <div style={{ 
        width: '100%', 
        height: '400px', 
        marginBottom: '4rem',
        border: '1px solid var(--border)',
        position: 'relative'
      }}>
        {course.thumbnail ? (
          <img src={course.thumbnail} alt={course.title} style={{ width: '100%', height: '100%', objectFit: 'cover', filter: 'grayscale(10%) contrast(1.05)' }} />
        ) : (
          <div style={{ width: '100%', height: '100%', background: 'var(--surface)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span className="mono" style={{ color: 'var(--text-muted)' }}>No imagery provided</span>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', paddingBottom: '3rem', borderBottom: '1px solid var(--border)', marginBottom: '4rem' }}>
        <div>
          <span className="mono" style={{ display: 'block', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Instructor</span>
          <h4 style={{ margin: 0, fontSize: '1.5rem' }}>{course.mentor_name}</h4>
        </div>
        
        <div style={{ textAlign: 'right' }}>
          <span className="mono" style={{ display: 'block', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Rating</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'flex-end' }}>
            <span style={{ fontSize: '1.25rem', fontFamily: 'var(--font-display)' }}>
              {ratingStats.avg_rating ? ratingStats.avg_rating.toFixed(1) : 'New'}
            </span>
            <span className="mono" style={{ color: 'var(--text-muted)' }}>({ratingStats.count} reviews)</span>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '4rem', flexWrap: 'wrap' }}>
        <div style={{ flex: '2 1 500px' }}>
          <h2 style={{ marginBottom: '2.5rem', fontSize: '2rem' }}>Syllabus</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
            {course.modules?.map((module, index) => (
              <div key={module.id}>
                <div style={{ 
                  display: 'flex',
                  alignItems: 'baseline',
                  gap: '1.5rem',
                  borderBottom: '1px solid var(--border-strong)',
                  paddingBottom: '1rem',
                  marginBottom: '1rem'
                }}>
                  <span className="mono" style={{ color: 'var(--accent)', fontSize: '1rem' }}>
                    {(index + 1).toString().padStart(2, '0')}
                  </span>
                  <h3 style={{ margin: 0, fontSize: '1.4rem' }}>{module.title}</h3>
                </div>
                
                <div>
                  {module.lessons?.map(lesson => (
                    <div key={lesson.id} style={{ 
                      padding: '1rem 0 1rem 3rem', 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'baseline',
                      borderBottom: '1px solid var(--border)'
                    }}>
                      <div style={{ display: 'flex', gap: '1rem', alignItems: 'baseline' }}>
                        <span style={{ 
                          color: progress[lesson.id] ? 'var(--text-muted)' : 'var(--text-strong)',
                          textDecoration: progress[lesson.id] ? 'line-through' : 'none',
                          fontSize: '1.05rem'
                        }}>
                          {lesson.title}
                        </span>
                        <span className="mono" style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>
                          [{lesson.lesson_type}]
                        </span>
                      </div>
                      
                      {isEnrolled && (
                        <button 
                          onClick={() => handleMarkComplete(lesson.id)} 
                          disabled={progress[lesson.id]} 
                          className="mono"
                          style={{ 
                            background: 'none', 
                            border: 'none', 
                            cursor: progress[lesson.id] ? 'default' : 'pointer',
                            color: progress[lesson.id] ? 'var(--accent)' : 'var(--text-strong)',
                            textDecoration: progress[lesson.id] ? 'none' : 'underline'
                          }}
                        >
                          {progress[lesson.id] ? 'Completed' : 'Mark Done'}
                        </button>
                      )}
                    </div>
                  ))}
                  {module.quizzes?.map(quiz => (
                    <div key={quiz.id} style={{ 
                      padding: '1rem 0 1rem 3rem', 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'baseline',
                      borderBottom: '1px solid var(--border)'
                    }}>
                      <div style={{ display: 'flex', gap: '1rem', alignItems: 'baseline' }}>
                        <span style={{ color: 'var(--text-strong)', fontSize: '1.05rem', fontWeight: '500' }}>
                          📝 Quiz: {quiz.title}
                        </span>
                        <span className="mono" style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>
                          [Passing Score: {quiz.passing_score}%]
                        </span>
                      </div>
                      
                      {isEnrolled && (
                        <Link 
                          to={`/quiz/${quiz.id}`} 
                          className="mono"
                          style={{ 
                            color: 'var(--accent)', 
                            textDecoration: 'underline',
                            fontWeight: '600'
                          }}
                        >
                          Take Quiz
                        </Link>
                      )}
                    </div>
                  ))}
                  {(!module.lessons || module.lessons.length === 0) && (!module.quizzes || module.quizzes.length === 0) && (
                    <div style={{ padding: '1rem 0 1rem 3rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                      Materials pending.
                    </div>
                  )}
                </div>
              </div>
            ))}
            {(!course.modules || course.modules.length === 0) && (
              <p style={{ color: 'var(--text-muted)' }}>The syllabus is currently being finalized.</p>
            )}
          </div>
        </div>

        {/* Enrollment / Sidebar */}
        <div style={{ flex: '1 1 300px' }}>
          <div style={{ 
            position: 'sticky', 
            top: '120px',
            background: 'var(--surface)',
            padding: '2.5rem',
            border: '1px solid var(--border)'
          }}>
            {isEnrolled ? (
              <div>
                <span className="mono" style={{ color: 'var(--accent)', display: 'block', marginBottom: '1rem' }}>Status</span>
                <h4 style={{ marginBottom: '2rem', fontSize: '1.5rem' }}>Enrolled</h4>
                <div className="form-stack">
                  <Link to={`/courses/${id}/qa`} className="btn btn-primary" style={{ width: '100%' }}>
                    Enter Q&A Forum
                  </Link>
                  {certificate && (
                    <button onClick={downloadCertificate} className="btn btn-secondary" style={{ width: '100%' }}>
                      Download Certificate
                    </button>
                  )}
                  <button onClick={handleUnenroll} className="btn btn-ghost" style={{ width: '100%', color: '#d32f2f', border: '1px solid transparent' }}>
                    Unenroll
                  </button>
                </div>
              </div>
            ) : (
              <div>
                {!isLoggedIn ? (
                  <div style={{ textAlign: 'center' }}>
                    <h4 style={{ marginBottom: '1rem' }}>Registration</h4>
                    <p style={{ marginBottom: '2rem', fontSize: '0.9rem' }}>Please authenticate to access this material.</p>
                    <Link to="/login" className="btn btn-primary" style={{ width: '100%' }}>Sign In</Link>
                  </div>
                ) : (
                  <div>
                    <span className="mono" style={{ color: 'var(--text-muted)', display: 'block', marginBottom: '0.5rem' }}>Investment</span>
                    <h4 style={{ marginBottom: '2rem', fontSize: '2.5rem', fontFamily: 'var(--font-display)' }}>
                      {course.is_free ? 'Complimentary' : `$${course.price}`}
                    </h4>
                    
                    {course.is_free ? (
                      <button onClick={handleFreeEnroll} disabled={enrolling} className="btn btn-primary" style={{ width: '100%' }}>
                        {enrolling ? 'Processing...' : 'Register Now'}
                      </button>
                    ) : (
                      <div className="form-stack">
                        <button onClick={handleStripeEnroll} disabled={enrolling} className="btn btn-primary" style={{ width: '100%' }}>
                          {enrolling ? 'Processing...' : 'Pay with Card (Stripe)'}
                        </button>
                        <button onClick={handlePayPalEnroll} disabled={enrolling} className="btn btn-secondary" style={{ width: '100%' }}>
                          {enrolling ? 'Processing...' : 'Pay with PayPal'}
                        </button>
                      </div>
                    )}
                  </div>
                )}
                {paymentError && (
                  <div className="form-error" style={{ marginTop: '1.5rem', fontSize: '0.8rem' }}>
                    {paymentError}
                  </div>
                )}
              </div>
            )}
          </div>
          
          <div style={{ marginTop: '4rem' }}>
            <h4 style={{ marginBottom: '2rem', fontSize: '1.5rem', borderBottom: '1px solid var(--border)', paddingBottom: '1rem' }}>Student Reviews</h4>
            
            {isEnrolled && (
              <div style={{ marginBottom: '3rem' }}>
                <form onSubmit={handleSubmitReview} className="form-stack">
                  <select 
                    className="form-select"
                    value={newReview.rating} 
                    onChange={e => setNewReview({...newReview, rating: e.target.value})} 
                  >
                    {[5,4,3,2,1].map(n => <option key={n} value={n}>{n} Stars - {['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'][n-1]}</option>)}
                  </select>
                  <textarea 
                    className="form-textarea"
                    placeholder="Share your perspective..." 
                    value={newReview.review_text} 
                    onChange={e => setNewReview({...newReview, review_text: e.target.value})}
                    required
                  />
                  <button type="submit" className="btn btn-secondary" style={{ alignSelf: 'flex-start' }}>Submit</button>
                </form>
              </div>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              {reviews.map(review => (
                <div key={review.id}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '0.5rem' }}>
                    <strong style={{ color: 'var(--text-strong)' }}>{review.student_name}</strong>
                    <span className="mono" style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{review.rating}/5</span>
                  </div>
                  <p style={{ fontSize: '0.95rem', lineHeight: '1.6', margin: '0 0 0.5rem 0' }}>
                    "{review.review_text}"
                  </p>
                  <button 
                    onClick={async () => {
                      if (confirm('Flag this review as inappropriate?')) {
                        await api.patch(`/reviews/${review.id}/`, { is_flagged: true });
                        alert('Review flagged.');
                        fetchData();
                      }
                    }}
                    className="mono" style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: 0, textDecoration: 'underline', fontSize: '0.7rem' }}
                  >
                    Flag
                  </button>
                </div>
              ))}
              {reviews.length === 0 && (
                <p style={{ color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.9rem' }}>No feedback provided yet.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CourseDetails;
