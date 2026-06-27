import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../api';

function EditQuiz() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState(null);
  
  const [newQuestionText, setNewQuestionText] = useState('');
  
  // Choice form state
  const [addingChoicesTo, setAddingChoicesTo] = useState(null);
  const [choiceForm, setChoiceForm] = useState({ text: '', is_correct: false });

  const fetchQuiz = async () => {
    try {
      const res = await api.get(`/quizzes/${id}/`);
      setQuiz(res.data);
    } catch (err) {
      console.error(err);
      alert('Failed to load quiz details');
    }
  };

  useEffect(() => {
    fetchQuiz();
  }, [id]);

  const handleAddQuestion = async () => {
    if (!newQuestionText) return;
    try {
      await api.post('/quiz-questions/', {
        quiz: id,
        text: newQuestionText,
        order: quiz.questions?.length || 0
      });
      setNewQuestionText('');
      fetchQuiz();
    } catch (err) {
      alert('Failed to add question');
    }
  };

  const handleAddChoice = async (questionId) => {
    if (!choiceForm.text) return;
    try {
      await api.post('/quiz-choices/', {
        question: questionId,
        text: choiceForm.text,
        is_correct: choiceForm.is_correct
      });
      setAddingChoicesTo(null);
      setChoiceForm({ text: '', is_correct: false });
      fetchQuiz();
    } catch (err) {
      alert('Failed to add choice');
    }
  };

  const handleDeleteQuestion = async (questionId) => {
    if (!window.confirm('Delete this question?')) return;
    try {
      await api.delete(`/quiz-questions/${questionId}/`);
      fetchQuiz();
    } catch (err) {
      alert('Failed to delete question');
    }
  };

  const handleDeleteChoice = async (choiceId) => {
    try {
      await api.delete(`/quiz-choices/${choiceId}/`);
      fetchQuiz();
    } catch (err) {
      alert('Failed to delete choice');
    }
  };

  if (!quiz) return <div className="page loading-state"><div className="spinner"></div></div>;

  return (
    <div className="page" style={{ maxWidth: '800px' }}>
      <div style={{ marginBottom: '2rem' }}>
        <Link to={`/mentor/edit/${quiz.module.course}`} className="mono" style={{ color: 'var(--text-muted)' }}>&larr; Back to Course</Link>
        <h1 style={{ marginTop: '1rem', marginBottom: '0.5rem' }}>Edit Quiz: {quiz.title}</h1>
        <p style={{ color: 'var(--text-muted)' }}>Passing Score: {quiz.passing_score}%</p>
      </div>

      <div style={{ marginBottom: '3rem', padding: '1.5rem', border: '1px solid var(--border)', background: 'var(--surface)', borderRadius: '8px' }}>
        <h3>Add Question</h3>
        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
          <input 
            type="text" 
            className="form-input" 
            placeholder="Enter question text..." 
            value={newQuestionText} 
            onChange={e => setNewQuestionText(e.target.value)} 
            style={{ flex: 1 }}
          />
          <button className="btn btn-primary" onClick={handleAddQuestion}>Add Question</button>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        {quiz.questions?.map((q, idx) => (
          <div key={q.id} style={{ border: '1px solid var(--border-strong)', padding: '1.5rem', borderRadius: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
              <h4 style={{ margin: 0 }}>{idx + 1}. {q.text}</h4>
              <button className="btn btn-sm btn-ghost" style={{ color: '#d32f2f' }} onClick={() => handleDeleteQuestion(q.id)}>Delete</button>
            </div>

            {q.choices?.length > 0 && (
              <ul style={{ listStyle: 'none', padding: 0, marginBottom: '1.5rem' }}>
                {q.choices.map(choice => (
                  <li key={choice.id} style={{ padding: '0.5rem', background: choice.is_correct ? 'rgba(76, 175, 80, 0.1)' : 'transparent', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>
                      {choice.is_correct && <span style={{ color: 'var(--success)', marginRight: '8px', fontWeight: 'bold' }}>✓</span>}
                      {choice.text}
                    </span>
                    <button className="btn btn-sm" style={{ background: 'transparent', border: 'none', color: '#d32f2f', cursor: 'pointer' }} onClick={() => handleDeleteChoice(choice.id)}>&times;</button>
                  </li>
                ))}
              </ul>
            )}

            {addingChoicesTo === q.id ? (
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', background: 'var(--bg)', padding: '1rem', borderRadius: '4px', border: '1px solid var(--border)' }}>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="Choice text..." 
                  value={choiceForm.text} 
                  onChange={e => setChoiceForm({...choiceForm, text: e.target.value})}
                  style={{ flex: 1 }}
                />
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', whiteSpace: 'nowrap' }}>
                  <input 
                    type="checkbox" 
                    checked={choiceForm.is_correct} 
                    onChange={e => setChoiceForm({...choiceForm, is_correct: e.target.checked})} 
                  />
                  Correct Answer
                </label>
                <button className="btn btn-primary btn-sm" onClick={() => handleAddChoice(q.id)}>Save</button>
                <button className="btn btn-ghost btn-sm" onClick={() => { setAddingChoicesTo(null); setChoiceForm({text:'', is_correct:false}); }}>Cancel</button>
              </div>
            ) : (
              <button className="btn btn-secondary btn-sm" onClick={() => setAddingChoicesTo(q.id)}>+ Add Choice</button>
            )}
          </div>
        ))}
        {quiz.questions?.length === 0 && (
          <p style={{ color: 'var(--text-muted)' }}>No questions added yet.</p>
        )}
      </div>
    </div>
  );
}

export default EditQuiz;
