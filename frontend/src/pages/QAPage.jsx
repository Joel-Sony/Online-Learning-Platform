import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import api, { getWebSocketUrl } from '../api';

// ─── Helpers ──────────────────────────────────────────────────────────────────

function timeAgo(dateStr) {
    const diff = Math.floor((Date.now() - new Date(dateStr)) / 1000);
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return new Date(dateStr).toLocaleDateString();
}

const currentUser = () => localStorage.getItem('username');
const currentRole = () => localStorage.getItem('role');

// ─── Sub-components ────────────────────────────────────────────────────────────

function MentorBadge() {
    return (
        <span style={{
            fontSize: '0.65rem', fontWeight: 'bold', background: '#2ecc71',
            color: 'white', padding: '0.15rem 0.5rem', borderRadius: '999px',
            marginLeft: '0.5rem', verticalAlign: 'middle'
        }}>MENTOR</span>
    );
}

function PinBadge() {
    return (
        <span style={{
            fontSize: '0.65rem', fontWeight: 'bold', background: '#f39c12',
            color: 'white', padding: '0.15rem 0.5rem', borderRadius: '999px',
            marginLeft: '0.5rem', verticalAlign: 'middle'
        }}>📌 PINNED</span>
    );
}

function ReplyItem({ reply, courseId, questionId, onDelete, onReplyPosted }) {
    const [showReplyForm, setShowReplyForm] = useState(false);
    const canDelete =
        reply.author_name === currentUser() ||
        currentRole() === 'ADMIN' ||
        currentRole() === 'MENTOR';

    return (
        <div style={{
            background: reply.is_mentor_response ? '#f0fff4' : '#f8f9fa',
            border: reply.is_mentor_response ? '1px solid #2ecc71' : '1px solid #eee',
            borderRadius: '6px', padding: '0.8rem 1rem', marginBottom: '0.6rem'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                <span style={{ fontWeight: 'bold', fontSize: '0.85rem' }}>
                    {reply.author_name}
                    {reply.is_mentor_response && <MentorBadge />}
                </span>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.75rem', color: '#999' }}>{timeAgo(reply.created_at)}</span>
                    {reply.parent === null && (
                        <button 
                            onClick={() => setShowReplyForm(!showReplyForm)}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#007bff', fontSize: '0.75rem' }}
                        >
                            {showReplyForm ? 'Cancel' : 'Reply'}
                        </button>
                    )}
                    {canDelete && (
                        <button onClick={() => onDelete(reply.id)} style={{
                            background: 'none', border: 'none', cursor: 'pointer',
                            color: '#e74c3c', fontSize: '0.75rem'
                        }}>✕</button>
                    )}
                    <button 
                        onClick={async () => {
                            if (confirm('Flag this reply as inappropriate?')) {
                                await api.patch(`/courses/${courseId}/qna/questions/${questionId}/replies/${reply.id}/`, { is_flagged: true });
                                alert('Reply flagged.');
                            }
                        }}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#999', fontSize: '0.75rem' }}
                    >Flag</button>
                </div>
            </div>
            <p style={{ margin: 0, fontSize: '0.9rem', lineHeight: '1.5' }}>{reply.body}</p>

            {showReplyForm && (
                <div style={{ marginTop: '0.5rem' }}>
                    <ReplyForm 
                        questionId={questionId} 
                        courseId={courseId} 
                        parentId={reply.id} 
                        onReplyPosted={() => {
                            setShowReplyForm(false);
                            onReplyPosted();
                        }}
                        placeholder={`Replying to ${reply.author_name}...`}
                    />
                </div>
            )}

            {/* Nested children (one level deep) */}
            {reply.children?.length > 0 && (
                <div style={{ marginTop: '0.6rem', marginLeft: '1.5rem', borderLeft: '2px solid #ddd', paddingLeft: '0.8rem' }}>
                    {reply.children.map(child => (
                        <ReplyItem 
                            key={child.id} 
                            reply={child} 
                            courseId={courseId}
                            questionId={questionId}
                            onDelete={onDelete} 
                            onReplyPosted={onReplyPosted}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

function ReplyForm({ questionId, courseId, parentId = null, onReplyPosted, placeholder = 'Write a reply...' }) {
    const [body, setBody] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!body.trim()) return;
        setSubmitting(true);
        try {
            const payload = { body, question: questionId };
            if (parentId) payload.parent = parentId;
            await api.post(`/courses/${courseId}/qna/questions/${questionId}/replies/`, payload);
            setBody('');
            onReplyPosted();
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to post reply.');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.5rem', marginTop: '0.8rem' }}>
            <input
                type="text"
                value={body}
                onChange={e => setBody(e.target.value)}
                placeholder={placeholder}
                required
                style={{ flex: 1, padding: '0.5rem 0.8rem', borderRadius: '6px', border: '1px solid #ddd', fontSize: '0.9rem' }}
            />
            <button
                type="submit"
                disabled={submitting}
                style={{ padding: '0.5rem 1rem', background: '#007bff', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.85rem' }}
            >
                {submitting ? '...' : 'Reply'}
            </button>
        </form>
    );
}

function QuestionCard({ question, courseId, isMentorOrAdmin, onPin, onDelete, onRefresh }) {
    const [expanded, setExpanded] = useState(false);
    const canDelete =
        question.author_name === currentUser() ||
        currentRole() === 'ADMIN' ||
        isMentorOrAdmin;

    const handleDeleteReply = async (replyId) => {
        if (!window.confirm('Delete this reply?')) return;
        try {
            await api.delete(`/courses/${courseId}/qna/questions/${question.id}/replies/${replyId}/`);
            onRefresh();
        } catch { alert('Failed to delete reply.'); }
    };

    return (
        <div style={{
            border: question.is_pinned ? '2px solid #f39c12' : '1px solid #e0e0e0',
            borderRadius: '10px', marginBottom: '1.5rem', background: 'white',
            boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
        }}>
            {/* Question header */}
            <div style={{ padding: '1.2rem 1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1 }}>
                        <h3 style={{ margin: '0 0 0.3rem 0', fontSize: '1.05rem', color: '#2c3e50' }}>
                            {question.is_pinned && <PinBadge />}
                            {' '}{question.title}
                        </h3>
                        <p style={{ margin: 0, fontSize: '0.8rem', color: '#888' }}>
                            by <strong>{question.author_name}</strong> · {timeAgo(question.created_at)} · {question.reply_count} {question.reply_count === 1 ? 'reply' : 'replies'}
                        </p>
                    </div>
                    <div style={{ display: 'flex', gap: '0.4rem', marginLeft: '1rem' }}>
                        {isMentorOrAdmin && (
                            <button onClick={() => onPin(question)} style={{
                                padding: '0.3rem 0.6rem', fontSize: '0.75rem', borderRadius: '4px',
                                border: '1px solid #f39c12', background: question.is_pinned ? '#f39c12' : 'white',
                                color: question.is_pinned ? 'white' : '#f39c12', cursor: 'pointer'
                            }}>
                                {question.is_pinned ? 'Unpin' : 'Pin'}
                            </button>
                        )}
                        {canDelete && (
                            <button onClick={() => onDelete(question)} style={{
                                padding: '0.3rem 0.6rem', fontSize: '0.75rem', borderRadius: '4px',
                                border: '1px solid #e74c3c', background: 'white', color: '#e74c3c', cursor: 'pointer'
                            }}>Delete</button>
                        )}
                        <button 
                            onClick={async () => {
                                if (confirm('Flag this question as inappropriate?')) {
                                    await api.patch(`/courses/${courseId}/qna/questions/${question.id}/`, { is_flagged: true });
                                    alert('Question flagged.');
                                }
                            }}
                            style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem', color: '#999', background: 'none', border: 'none', cursor: 'pointer' }}
                        >Flag</button>
                    </div>
                </div>

                <p style={{ margin: '0.8rem 0 0 0', fontSize: '0.95rem', color: '#555', lineHeight: '1.6' }}>{question.body}</p>

                <button
                    onClick={() => setExpanded(!expanded)}
                    style={{ marginTop: '0.8rem', background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', fontSize: '0.85rem', padding: 0 }}
                >
                    {expanded ? '▲ Hide replies' : `▼ Show ${question.reply_count} ${question.reply_count === 1 ? 'reply' : 'replies'}`}
                </button>
            </div>

            {/* Replies section */}
            {expanded && (
                <div style={{ borderTop: '1px solid #f0f0f0', padding: '1rem 1.5rem' }}>
                    {question.replies?.length === 0 ? (
                        <p style={{ color: '#aaa', fontSize: '0.9rem' }}>No replies yet.</p>
                    ) : (
                        question.replies.map(reply => (
                            <ReplyItem 
                                key={reply.id} 
                                reply={reply} 
                                courseId={courseId}
                                questionId={question.id}
                                onDelete={handleDeleteReply} 
                                onReplyPosted={onRefresh}
                            />
                        ))
                    )}

                    <div style={{ marginTop: '0.5rem' }}>
                        <ReplyForm
                            questionId={question.id}
                            courseId={courseId}
                            onReplyPosted={onRefresh}
                            placeholder="Write a reply..."
                        />
                    </div>
                </div>
            )}
        </div>
    );
}

// ─── Main Page ─────────────────────────────────────────────────────────────────

function QAPage() {
    const { id: courseId } = useParams();
    const [questions, setQuestions] = useState([]);
    const [newQ, setNewQ] = useState({ title: '', body: '' });
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [isEnrolled, setIsEnrolled] = useState(false);
    const [isMentorOrAdmin, setIsMentorOrAdmin] = useState(false);
    const socketRef = useRef(null);

    useEffect(() => {
        checkAccess();
        fetchQuestions();

        // Real-time via existing course QA WebSocket group
        const token = localStorage.getItem('access');
        if (token) {
            const socketUrl = getWebSocketUrl(`/ws/course/${courseId}/qa/?token=${token}`);
            socketRef.current = new WebSocket(socketUrl);
            socketRef.current.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.msg_type === 'new_question') {
                    setQuestions(prev => [data.message, ...prev]);
                } else if (data.msg_type === 'new_reply') {
                    // Refresh to get correct nested structure
                    fetchQuestions();
                }
            };
            socketRef.current.onerror = (err) => console.error('WS error:', err);
        }

        return () => { if (socketRef.current) socketRef.current.close(); };
    }, [courseId]);

    const checkAccess = async () => {
        const role = currentRole();
        if (role === 'ADMIN') { setIsMentorOrAdmin(true); setIsEnrolled(true); return; }
        if (role === 'MENTOR') { setIsMentorOrAdmin(true); setIsEnrolled(true); return; }
        try {
            const res = await api.get('/enrollments/');
            const found = res.data.find(e => e.course === parseInt(courseId));
            if (found) setIsEnrolled(true);
        } catch { /* Not logged in */ }
    };

    const fetchQuestions = async () => {
        try {
            const res = await api.get(`/courses/${courseId}/qna/questions/`);
            setQuestions(res.data);
        } catch (err) {
            console.error('Failed to load questions', err);
        } finally {
            setLoading(false);
        }
    };

    const handleAskQuestion = async (e) => {
        e.preventDefault();
        if (!isEnrolled) return alert('You must be enrolled to post a question.');
        setSubmitting(true);
        try {
            await api.post(`/courses/${courseId}/qna/questions/`, newQ);
            setNewQ({ title: '', body: '' });
            // WebSocket will update list; also refresh for fresh data
            fetchQuestions();
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to post question.');
        } finally {
            setSubmitting(false);
        }
    };

    const handlePin = async (question) => {
        try {
            await api.post(`/courses/${courseId}/qna/questions/${question.id}/pin/`);
            fetchQuestions();
        } catch { alert('Failed to pin/unpin.'); }
    };

    const handleDeleteQuestion = async (question) => {
        if (!window.confirm(`Delete "${question.title}"?`)) return;
        try {
            await api.delete(`/courses/${courseId}/qna/questions/${question.id}/`);
            fetchQuestions();
        } catch { alert('Failed to delete question.'); }
    };

    return (
        <div style={{ textAlign: 'left', maxWidth: '960px', margin: '0 auto', padding: '0 1rem' }}>

            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1 style={{ margin: '0 0 0.2rem 0', color: '#2c3e50' }}>Course Q&A</h1>
                    <p style={{ margin: 0, color: '#888', fontSize: '0.9rem' }}>Ask questions, share knowledge, get mentor answers.</p>
                </div>
                <Link to={`/courses/${courseId}`} style={{
                    color: '#007bff', textDecoration: 'none', fontSize: '0.9rem',
                    border: '1px solid #007bff', padding: '0.4rem 0.8rem', borderRadius: '6px'
                }}>← Back to Course</Link>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2.5rem', alignItems: 'start' }}>

                {/* Ask Question Form */}
                <div style={{ background: 'white', padding: '1.5rem', borderRadius: '10px', boxShadow: '0 2px 8px rgba(0,0,0,0.07)', position: 'sticky', top: '1rem' }}>
                    <h2 style={{ marginTop: 0, color: '#2c3e50', fontSize: '1.1rem' }}>Ask a Question</h2>
                    {isEnrolled ? (
                        <form onSubmit={handleAskQuestion} style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                            <input
                                type="text"
                                placeholder="Short, clear title"
                                value={newQ.title}
                                onChange={e => setNewQ({ ...newQ, title: e.target.value })}
                                required
                                style={{ padding: '0.7rem', borderRadius: '6px', border: '1px solid #ddd', fontSize: '0.9rem' }}
                            />
                            <textarea
                                placeholder="Describe your question in detail..."
                                value={newQ.body}
                                onChange={e => setNewQ({ ...newQ, body: e.target.value })}
                                required
                                rows={5}
                                style={{ padding: '0.7rem', borderRadius: '6px', border: '1px solid #ddd', fontSize: '0.9rem', resize: 'vertical' }}
                            />
                            <button
                                type="submit"
                                disabled={submitting}
                                style={{ padding: '0.8rem', background: '#007bff', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
                            >
                                {submitting ? 'Posting...' : 'Post Question'}
                            </button>
                        </form>
                    ) : (
                        <div style={{ textAlign: 'center', padding: '1.5rem 0', color: '#888' }}>
                            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔒</div>
                            <p style={{ margin: 0 }}>Enroll in this course to participate in Q&A.</p>
                        </div>
                    )}
                </div>

                {/* Questions List */}
                <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.2rem' }}>
                        <h2 style={{ margin: 0, color: '#2c3e50', fontSize: '1.1rem' }}>
                            Discussions
                            <span style={{ fontWeight: 'normal', fontSize: '0.85rem', color: '#999', marginLeft: '0.5rem' }}>
                                ({questions.length} question{questions.length !== 1 ? 's' : ''})
                            </span>
                        </h2>
                    </div>

                    {loading ? (
                        <div style={{ textAlign: 'center', padding: '3rem', color: '#999' }}>Loading discussions...</div>
                    ) : questions.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '3rem 0', color: '#aaa' }}>
                            <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>💬</div>
                            <p>No questions yet. Be the first to ask!</p>
                        </div>
                    ) : (
                        questions.map(q => (
                            <QuestionCard
                                key={q.id}
                                question={q}
                                courseId={courseId}
                                isMentorOrAdmin={isMentorOrAdmin}
                                onPin={handlePin}
                                onDelete={handleDeleteQuestion}
                                onRefresh={fetchQuestions}
                            />
                        ))
                    )}
                </div>

            </div>
        </div>
    );
}

export default QAPage;
