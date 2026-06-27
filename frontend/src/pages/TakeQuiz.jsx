import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';

function TakeQuiz() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Quiz progression state
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedChoices, setSelectedChoices] = useState({}); // { questionId: choiceId }
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchQuiz();
  }, [id]);

  const fetchQuiz = async () => {
    try {
      const res = await api.get(`/quizzes/${id}/`);
      setQuiz(res.data);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to load the quiz. Make sure you are enrolled in this course.');
      setLoading(false);
    }
  };

  const handleChoiceSelect = (questionId, choiceId) => {
    setSelectedChoices(prev => ({
      ...prev,
      [questionId]: choiceId
    }));
  };

  const handleNext = () => {
    if (currentQuestionIndex < quiz.questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    // Check that all questions have answers
    const unanswered = quiz.questions.filter(q => !selectedChoices[q.id]);
    if (unanswered.length > 0) {
      if (!window.confirm(`You have not answered all questions (${unanswered.length} remaining). Submit anyway?`)) {
        return;
      }
    }

    setSubmitting(true);
    try {
      const res = await api.post(`/quizzes/${id}/submit/`, {
        answers: selectedChoices
      });
      setResult(res.data);
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to submit quiz attempt.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return (
    <div className="page loading-state">
      <div className="spinner"></div> Loading Quiz...
    </div>
  );

  if (error) return (
    <div className="page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
      <div className="card" style={{ maxWidth: '500px', width: '100%', textAlign: 'center', padding: '40px' }}>
        <div className="empty-state">
          <div className="empty-state-icon" style={{ color: 'var(--error)', background: '#fef2f2' }}>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          </div>
          <h2 style={{ color: 'var(--text-primary)' }}>Access Denied</h2>
          <p>{error}</p>
          <button onClick={() => navigate(-1)} className="btn btn-secondary" style={{ marginTop: '24px' }}>Go Back</button>
        </div>
      </div>
    </div>
  );

  if (!quiz || !quiz.questions || quiz.questions.length === 0) {
    return (
      <div className="page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="card" style={{ maxWidth: '500px', width: '100%', textAlign: 'center', padding: '40px' }}>
          <div className="empty-state">
            <h2 style={{ color: 'var(--text-primary)' }}>No Questions Available</h2>
            <p>This quiz is currently empty. Please check back later.</p>
            <button onClick={() => navigate(-1)} className="btn btn-secondary" style={{ marginTop: '24px' }}>Go Back</button>
          </div>
        </div>
      </div>
    );
  }

  if (result) {
    return (
      <div className="page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh', padding: '40px' }}>
        <div className="card" style={{ maxWidth: '600px', width: '100%', padding: '48px', textAlign: 'center' }}>
          <div className="empty-state">
            {result.passed ? (
              <div className="empty-state-icon" style={{ color: 'var(--success)', background: '#f0fdf4', margin: '0 auto 24px' }}>
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              </div>
            ) : (
              <div className="empty-state-icon" style={{ color: 'var(--error)', background: '#fef2f2', margin: '0 auto 24px' }}>
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
              </div>
            )}

            <h1 style={{ fontSize: '2.25rem', fontWeight: '700', marginBottom: '8px' }}>
              {result.passed ? 'Quiz Passed!' : 'Quiz Failed'}
            </h1>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>
              {result.passed
                ? 'Great job! You have satisfied the passing score requirement.'
                : 'Do not worry, you can study the materials and try again.'}
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', background: 'var(--surface)', padding: '24px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border)', marginBottom: '40px' }}>
              <div>
                <span className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', textTransform: 'uppercase' }}>Your Score</span>
                <span style={{ fontSize: '2rem', fontWeight: '700', color: result.passed ? 'var(--success)' : 'var(--error)' }}>{result.score}%</span>
              </div>
              <div>
                <span className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', textTransform: 'uppercase' }}>Requirement</span>
                <span style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--text-primary)' }}>{quiz.passing_score}%</span>
              </div>
              <div style={{ gridColumn: '1 / -1', borderTop: '1px solid var(--border)', paddingTop: '16px', display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Correct Answers:</span>
                <span className="mono" style={{ fontWeight: '600' }}>{result.correct_answers} / {result.total_questions}</span>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
              {!result.passed && (
                <button onClick={() => { setResult(null); setCurrentQuestionIndex(0); setSelectedChoices({}); }} className="btn btn-primary btn-lg">
                  Try Again
                </button>
              )}
              <button onClick={() => navigate(-1)} className={result.passed ? 'btn btn-primary btn-lg' : 'btn btn-secondary btn-lg'}>
                Back to Course
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const currentQuestion = quiz.questions[currentQuestionIndex];
  const progressPercent = ((currentQuestionIndex + 1) / quiz.questions.length) * 100;

  return (
    <div className="page" style={{ display: 'flex', justifyContent: 'center', padding: '40px 24px' }}>
      <div className="card" style={{ maxWidth: '700px', width: '100%', padding: '40px' }}>
        
        {/* Quiz Info Header */}
        <div style={{ marginBottom: '32px', borderBottom: '1px solid var(--border)', paddingBottom: '20px' }}>
          <span className="mono" style={{ color: 'var(--accent)', fontSize: '0.85rem', display: 'block', marginBottom: '8px' }}>
            MODULE QUIZ
          </span>
          <h1 style={{ fontSize: '1.75rem', fontWeight: '600', marginBottom: '8px' }}>{quiz.title}</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>{quiz.description}</p>
        </div>

        {/* Progress Tracker */}
        <div style={{ marginBottom: '40px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '10px' }}>
            <span className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Question {currentQuestionIndex + 1} of {quiz.questions.length}
            </span>
            <span className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-strong)' }}>
              {Math.round(progressPercent)}% Complete
            </span>
          </div>
          <div className="progress-track" style={{ height: '6px' }}>
            <div className="progress-fill" style={{ width: `${progressPercent}%` }}></div>
          </div>
        </div>

        {/* Question & Choices Area */}
        <div style={{ minHeight: '260px', marginBottom: '40px' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '500', marginBottom: '24px', lineHeight: '1.5' }}>
            {currentQuestion.text}
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {currentQuestion.choices?.map(choice => {
              const isSelected = selectedChoices[currentQuestion.id] === choice.id;
              return (
                <label
                  key={choice.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '16px 20px',
                    borderRadius: 'var(--radius-md)',
                    border: isSelected ? '1px solid var(--accent)' : '1px solid var(--border)',
                    background: isSelected ? 'var(--accent-light)' : 'var(--surface)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <input
                    type="radio"
                    name={`question-${currentQuestion.id}`}
                    checked={isSelected}
                    onChange={() => handleChoiceSelect(currentQuestion.id, choice.id)}
                    style={{
                      marginRight: '16px',
                      accentColor: 'var(--accent)',
                      transform: 'scale(1.2)',
                      cursor: 'pointer'
                    }}
                  />
                  <span style={{ fontSize: '0.95rem', color: isSelected ? 'var(--accent)' : 'var(--text-primary)', fontWeight: isSelected ? '500' : '400' }}>
                    {choice.text}
                  </span>
                </label>
              );
            })}
          </div>
        </div>

        {/* Nav Controls */}
        <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border)', paddingTop: '28px' }}>
          <button
            onClick={handlePrev}
            disabled={currentQuestionIndex === 0}
            className="btn btn-secondary"
            style={{ opacity: currentQuestionIndex === 0 ? 0.4 : 1 }}
          >
            ← Previous
          </button>

          {currentQuestionIndex < quiz.questions.length - 1 ? (
            <button
              onClick={handleNext}
              disabled={!selectedChoices[currentQuestion.id]}
              className="btn btn-primary"
              style={{ opacity: !selectedChoices[currentQuestion.id] ? 0.6 : 1 }}
            >
              Next →
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="btn btn-primary"
              style={{ background: 'var(--success)', border: 'none' }}
            >
              {submitting ? 'Submitting...' : 'Finish & Submit'}
            </button>
          )}
        </div>

      </div>
    </div>
  );
}

export default TakeQuiz;
