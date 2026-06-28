import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import api, { getWebSocketUrl } from '../api';

// ─── Helpers ──────────────────────────────────────────────────────────────────

function timeAgo(dateStr) {
    const diff = Math.floor((Date.now() - new Date(dateStr)) / 1000);
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return new Date(dateStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

const currentUser = () => localStorage.getItem('username');
const currentRole = () => localStorage.getItem('role');

function AuthorAvatar({ name, isMentor }) {
    const letter = name ? name.charAt(0).toUpperCase() : 'U';
    return (
        <span style={{
            width: '28px', height: '28px',
            borderRadius: '50%',
            background: isMentor ? 'var(--accent)' : 'var(--surface)',
            color: isMentor ? '#fff' : 'var(--text-primary)',
            fontSize: '0.75rem',
            fontWeight: '600',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: isMentor ? 'none' : '1px solid var(--border-strong)',
            flexShrink: 0
        }}>
            {letter}
        </span>
    );
}

// ─── Sub-components ────────────────────────────────────────────────────────────

function MentorBadge() {
    return (
        <span className="badge badge-accent" style={{
            fontSize: '0.65rem',
            fontWeight: '600',
            padding: '3px 8px',
            borderRadius: '4px',
            textTransform: 'uppercase',
            letterSpacing: '0.02em',
            marginLeft: '6px',
            verticalAlign: 'middle'
        }}>Mentor</span>
    );
}

function PinBadge() {
    return (
        <span className="badge badge-warning" style={{
            fontSize: '0.65rem',
            fontWeight: '600',
            padding: '3px 8px',
            borderRadius: '4px',
            textTransform: 'uppercase',
            letterSpacing: '0.02em',
            marginRight: '8px',
            verticalAlign: 'middle'
        }}>📌 Pinned</span>
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
            background: reply.is_mentor_response ? 'rgba(22, 163, 74, 0.02)' : 'var(--bg-subtle)',
            border: reply.is_mentor_response ? '1px solid rgba(22, 163, 74, 0.25)' : '1px solid var(--border)',
            borderLeft: reply.is_mentor_response ? '3px solid var(--success)' : '1px solid var(--border)',
            borderRadius: 'var(--radius-md)',
            padding: '1rem',
            marginBottom: '0.75rem',
            animation: 'fadeIn 0.2s ease'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '8px' }}>
                <span style={{ fontWeight: '600', fontSize: '0.875rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <AuthorAvatar name={reply.author_name} isMentor={reply.is_mentor_response} />
                    {reply.author_name}
                    {reply.is_mentor_response && <MentorBadge />}
                </span>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>{timeAgo(reply.created_at)}</span>
                    
                    {reply.parent === null && (
                        <button 
                            onClick={() => setShowReplyForm(!showReplyForm)}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--accent-text)', fontSize: '0.75rem', fontWeight: '600', padding: 0 }}
                        >
                            {showReplyForm ? 'Cancel' : 'Reply'}
                        </button>
                    )}
                    
                    {canDelete && (
                        <button 
                            onClick={() => onDelete(reply.id)} 
                            title="Delete reply"
                            style={{
                                background: 'none', border: 'none', cursor: 'pointer',
                                color: 'var(--error)', fontSize: '0.75rem', fontWeight: '600', padding: 0
                            }}
                        >
                            Delete
                        </button>
                    )}
                    
                    <button 
                        onClick={async () => {
                            if (confirm('Flag this reply as inappropriate?')) {
                                await api.patch(`/courses/${courseId}/qna/questions/${questionId}/replies/${reply.id}/`, { is_flagged: true });
                                alert('Reply flagged.');
                            }
                        }}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-tertiary)', fontSize: '0.75rem', padding: 0 }}
                    >
                        Flag
                    </button>
                </div>
            </div>
            
            <p style={{ margin: '0 0 0 36px', fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>{reply.body}</p>

            {showReplyForm && (
                <div style={{ marginTop: '0.75rem', marginLeft: '36px' }}>
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
                <div style={{ marginTop: '0.75rem', marginLeft: '36px', borderLeft: '2px solid var(--border)', paddingLeft: '1rem' }}>
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
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '8px', marginTop: '0.75rem' }}>
            <input
                type="text"
                value={body}
                onChange={e => setBody(e.target.value)}
                placeholder={placeholder}
                required
                className="form-input"
                style={{ flex: 1, height: '38px', fontSize: '0.85rem' }}
                disabled={submitting}
            />
            <button
                type="submit"
                disabled={submitting}
                className="btn btn-primary btn-sm"
                style={{ height: '38px', padding: '0 16px' }}
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
        <div className="card" style={{
            border: question.is_pinned ? '1px solid var(--warning)' : '1px solid var(--border)',
            borderLeft: question.is_pinned ? '4px solid var(--warning)' : '1px solid var(--border)',
            borderRadius: 'var(--radius-lg)',
            marginBottom: '1.25rem',
            padding: 0,
            overflow: 'hidden',
            boxShadow: 'var(--shadow-sm)',
            transition: 'var(--transition-slow)'
        }}>
            {/* Question header */}
            <div style={{ padding: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px' }}>
                    <div style={{ flex: 1 }}>
                        <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: '600', color: 'var(--text-primary)', lineHeight: '1.4' }}>
                            {question.is_pinned && <PinBadge />}
                            {question.title}
                        </h3>
                        <p style={{ margin: '8px 0 0 0', fontSize: '0.8rem', color: 'var(--text-tertiary)', display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px' }}>
                            <AuthorAvatar name={question.author_name} isMentor={false} />
                            <strong>{question.author_name}</strong>
                            <span>•</span>
                            <span className="mono">{timeAgo(question.created_at)}</span>
                            <span>•</span>
                            <span>{question.reply_count} {question.reply_count === 1 ? 'reply' : 'replies'}</span>
                        </p>
                    </div>
                    
                    {/* Action Buttons */}
                    <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                        {isMentorOrAdmin && (
                            <button 
                                onClick={() => onPin(question)} 
                                className="btn btn-sm"
                                style={{
                                    height: '28px', padding: '0 8px', fontSize: '0.72rem',
                                    border: '1px solid var(--border-strong)',
                                    background: question.is_pinned ? 'var(--warning)' : 'transparent',
                                    color: question.is_pinned ? '#fff' : 'var(--text-primary)',
                                    borderColor: question.is_pinned ? 'var(--warning)' : 'var(--border-strong)'
                                }}
                            >
                                {question.is_pinned ? 'Unpin' : 'Pin'}
                            </button>
                        )}
                        {canDelete && (
                            <button 
                                onClick={() => onDelete(question)} 
                                className="btn btn-sm"
                                style={{
                                    height: '28px', padding: '0 8px', fontSize: '0.72rem',
                                    border: '1px solid var(--border-strong)',
                                    background: 'transparent', color: 'var(--error)'
                                }}
                                onMouseEnter={e => { e.currentTarget.style.background = '#fff5f5'; e.currentTarget.style.borderColor = 'var(--error)'; }}
                                onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.borderColor = 'var(--border-strong)'; }}
                            >
                                Delete
                            </button>
                        )}
                        <button 
                            onClick={async () => {
                                if (confirm('Flag this question as inappropriate?')) {
                                    await api.patch(`/courses/${courseId}/qna/questions/${question.id}/`, { is_flagged: true });
                                    alert('Question flagged.');
                                }
                            }}
                            className="btn btn-sm"
                            style={{ height: '28px', padding: '0 8px', fontSize: '0.72rem', background: 'transparent', border: 'none', color: 'var(--text-tertiary)' }}
                        >
                            Flag
                        </button>
                    </div>
                </div>

                <p style={{ margin: '1rem 0 0 0', fontSize: '0.925rem', color: 'var(--text-secondary)', lineHeight: '1.65', whiteSpace: 'pre-wrap' }}>
                    {question.body}
                </p>

                <button
                    onClick={() => setExpanded(!expanded)}
                    className="btn btn-ghost btn-sm"
                    style={{
                        marginTop: '1rem',
                        color: 'var(--accent-text)',
                        padding: '4px 10px',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        fontSize: '0.8rem',
                        fontWeight: '600'
                    }}
                >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{
                        transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                        transition: 'transform 0.2s ease'
                    }}>
                        <polyline points="6 9 12 15 18 9"></polyline>
                    </svg>
                    {expanded ? 'Hide replies' : `View ${question.reply_count} ${question.reply_count === 1 ? 'reply' : 'replies'}`}
                </button>
            </div>

            {/* Replies section */}
            {expanded && (
                <div style={{ borderTop: '1px solid var(--border)', padding: '1.5rem', background: 'var(--bg-subtle)' }}>
                    {question.replies?.length === 0 ? (
                        <p style={{ color: 'var(--text-tertiary)', fontSize: '0.85rem', textAlign: 'center', padding: '1rem 0' }}>No replies yet.</p>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            {question.replies.map(reply => (
                                <ReplyItem 
                                    key={reply.id} 
                                    reply={reply} 
                                    courseId={courseId}
                                    questionId={question.id}
                                    onDelete={handleDeleteReply} 
                                    onReplyPosted={onRefresh}
                                />
                            ))}
                        </div>
                    )}

                    <div style={{ marginTop: '1rem' }}>
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
    const [searchQuery, setSearchQuery] = useState('');
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

    // Filter and sort questions (Pinned at top, then newest)
    const filteredQuestions = questions
        .filter(q => 
            q.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            q.body.toLowerCase().includes(searchQuery.toLowerCase()) ||
            q.author_name.toLowerCase().includes(searchQuery.toLowerCase())
        )
        .sort((a, b) => {
            if (a.is_pinned && !b.is_pinned) return -1;
            if (!a.is_pinned && b.is_pinned) return 1;
            return new Date(b.created_at) - new Date(a.created_at);
        });

    return (
        <div className="page" style={{ animation: 'fadeIn 0.3s ease', maxWidth: '1000px' }}>

            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2.5rem', flexWrap: 'wrap', gap: '16px' }}>
                <div>
                    <h1 className="heading-display" style={{ fontSize: '2.5rem', marginBottom: '0.4rem', fontWeight: '500' }}>Course Q&A</h1>
                    <p style={{ color: 'var(--text-secondary)', margin: 0 }}>Ask questions, share course resources, and get answers from your peers and mentors.</p>
                </div>
                <Link to={`/courses/${courseId}`} className="btn btn-secondary btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="19" y1="12" x2="5" y2="12"></line>
                        <polyline points="12 19 5 12 12 5"></polyline>
                    </svg>
                    Back to Course
                </Link>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2.5rem', alignItems: 'start' }}>

                {/* Left Pane: Ask Question Form */}
                <div className="card" style={{ padding: '2rem', position: 'sticky', top: '88px' }}>
                    <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2.5">
                          <circle cx="12" cy="12" r="10"></circle>
                          <line x1="12" y1="8" x2="12" y2="16"></line>
                          <line x1="8" y1="12" x2="16" y2="12"></line>
                        </svg>
                        Ask a Question
                    </h2>
                    {isEnrolled ? (
                        <form onSubmit={handleAskQuestion} className="form-stack">
                            <div className="form-group">
                                <label className="form-label">Title</label>
                                <input
                                    type="text"
                                    placeholder="e.g., How do I configure Django CORS?"
                                    value={newQ.title}
                                    onChange={e => setNewQ({ ...newQ, title: e.target.value })}
                                    required
                                    className="form-input"
                                    disabled={submitting}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Details</label>
                                <textarea
                                    placeholder="Describe your issue or question in detail. Provide code snippets if possible..."
                                    value={newQ.body}
                                    onChange={e => setNewQ({ ...newQ, body: e.target.value })}
                                    required
                                    rows={6}
                                    className="form-textarea"
                                    disabled={submitting}
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={submitting}
                                className="btn btn-primary"
                                style={{ width: '100%', padding: '12px' }}
                            >
                                {submitting ? 'Posting...' : 'Post Question'}
                            </button>
                        </form>
                    ) : (
                        <div className="empty-state" style={{ padding: '2rem 1rem', background: 'var(--bg-subtle)', borderRadius: '8px' }}>
                            <div className="empty-state-icon" style={{ width: '48px', height: '48px', margin: '0 auto 12px' }}>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                                </svg>
                            </div>
                            <h3 style={{ fontSize: '1rem', marginBottom: '4px' }}>Access Locked</h3>
                            <p style={{ fontSize: '0.825rem', color: 'var(--text-tertiary)' }}>Enroll in this course to ask questions and participate in discussions.</p>
                        </div>
                    )}
                </div>

                {/* Right Pane: Questions List */}
                <div style={{ gridColumn: 'span 1' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '1.5rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', margin: 0 }}>
                                Discussions
                                <span style={{ fontWeight: 'normal', fontSize: '0.85rem', color: 'var(--text-tertiary)', marginLeft: '8px' }}>
                                    ({filteredQuestions.length} question{filteredQuestions.length !== 1 ? 's' : ''})
                                </span>
                            </h2>
                        </div>
                        
                        {/* Search discussions */}
                        <div style={{ position: 'relative', width: '100%' }}>
                            <input
                                type="text"
                                className="form-input"
                                placeholder="Search questions or authors..."
                                value={searchQuery}
                                onChange={e => setSearchQuery(e.target.value)}
                                style={{ paddingLeft: '40px', height: '42px' }}
                            />
                            <span style={{ position: 'absolute', left: '14px', top: '12px', color: 'var(--text-tertiary)', display: 'flex', alignItems: 'center' }}>
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                                </svg>
                            </span>
                        </div>
                    </div>

                    {loading ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {[1, 2].map(n => (
                                <div key={n} className="skeleton-card" style={{ height: '140px', padding: '1.5rem' }}>
                                    <div className="skeleton" style={{ width: '40%', height: '20px', marginBottom: '12px' }} />
                                    <div className="skeleton" style={{ width: '70%', height: '14px', marginBottom: '12px' }} />
                                    <div className="skeleton" style={{ width: '20%', height: '14px' }} />
                                </div>
                            ))}
                        </div>
                    ) : filteredQuestions.length === 0 ? (
                        <div className="empty-state" style={{ padding: '4rem 2rem', background: 'var(--bg-subtle)', borderRadius: '12px', border: '1px dashed var(--border)' }}>
                            <div className="empty-state-icon">
                                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                                </svg>
                            </div>
                            <h3>No questions found</h3>
                            <p style={{ color: 'var(--text-tertiary)' }}>
                                {questions.length === 0 
                                    ? "No discussions have started for this course yet. Be the first to start the conversation!"
                                    : "No discussions match your search query."}
                            </p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                            {filteredQuestions.map(q => (
                                <QuestionCard
                                    key={q.id}
                                    question={q}
                                    courseId={courseId}
                                    isMentorOrAdmin={isMentorOrAdmin}
                                    onPin={handlePin}
                                    onDelete={handleDeleteQuestion}
                                    onRefresh={fetchQuestions}
                                />
                            ))}
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
}

export default QAPage;
