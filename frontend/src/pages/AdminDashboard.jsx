import { useState, useEffect } from 'react';
import api from '../api';

function AdminDashboard() {
    const [activeSection, setActiveSection] = useState('reports');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [userSearch, setUserSearch] = useState('');

    const IconBarChart = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>;
    const IconUsers = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>;
    const IconCheck = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>;
    const IconBook = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>;
    const IconFlag = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/></svg>;
    const IconDollar = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>;

    const sections = [
        { id: 'reports', label: 'Reports', Icon: IconBarChart },
        { id: 'users', label: 'Users', Icon: IconUsers },
        { id: 'mentors', label: 'Mentor Approvals', Icon: IconCheck },
        { id: 'courses', label: 'Course Approvals', Icon: IconBook },
        { id: 'moderation', label: 'Moderation', Icon: IconFlag },
        { id: 'refunds', label: 'Refunds', Icon: IconDollar },
    ];

    useEffect(() => {
        fetchData();
    }, [activeSection]);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            let res;
            switch (activeSection) {
                case 'reports':
                    res = await api.get('/admin/reports/');
                    break;
                case 'users':
                    res = await api.get('/admin/users/');
                    break;
                case 'mentors':
                    res = await api.get('/admin/mentors/pending/');
                    break;
                case 'courses':
                    res = await api.get('/admin/courses/pending/');
                    break;
                case 'moderation':
                    const reviewsRes = await api.get('/admin/reviews/flagged/');
                    const qnaRes = await api.get('/admin/qna/flagged/');
                    res = { data: { reviews: reviewsRes.data, questions: qnaRes.data.questions, replies: qnaRes.data.replies } };
                    break;
                case 'refunds':
                    res = await api.get('/admin/refunds/');
                    break;
                default:
                    res = { data: [] };
            }
            setData(res.data);
        } catch (err) {
            setError('Failed to fetch data');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleAction = async (endpoint, method = 'post', body = {}) => {
        try {
            await api({ url: endpoint, method, data: body });
            fetchData();
        } catch (err) {
            alert(err.response?.data?.error || 'Action failed');
        }
    };

    const list = (items) => Array.isArray(items) ? items : [];

    const renderReports = () => {
        const stats = data?.stats;
        if (!stats) return <p className="mono" style={{ color: 'var(--text-muted)' }}>No report data available.</p>;
        const courses = list(data?.top_courses);
        const mentors = list(data?.top_mentors);

        const statCards = [
            { label: 'Total Users', value: stats.total_users, color: '#4f46e5' },
            { label: 'Total Mentors', value: stats.total_mentors, color: '#0891b2' },
            { label: 'Total Students', value: stats.total_students, color: '#059669' },
            { label: 'Total Courses', value: stats.total_courses, color: '#d97706' },
            { label: 'Total Enrollments', value: stats.total_enrollments, color: '#dc2626' },
            { label: 'Total Revenue', value: `$${stats.total_revenue}`, color: '#7c3aed' },
        ];

        return (
            <div>
                <h2 style={{ marginBottom: '1.5rem' }}>Platform Reports</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
                    {statCards.map(s => (
                        <div key={s.label} style={{
                            background: 'var(--bg)',
                            border: '1px solid var(--border)',
                            borderRadius: 'var(--radius-lg)',
                            padding: '1.25rem',
                            boxShadow: 'var(--shadow-sm)',
                        }}>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>{s.label}</div>
                            <div style={{ fontSize: '1.75rem', fontWeight: 700, color: s.color }}>{s.value}</div>
                        </div>
                    ))}
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                    <div style={{
                        background: 'var(--bg)',
                        border: '1px solid var(--border)',
                        borderRadius: 'var(--radius-lg)',
                        padding: '1.25rem',
                    }}>
                        <h3 style={{ fontSize: '0.9rem', marginBottom: '1rem', color: 'var(--text-primary)' }}>Top 5 Courses</h3>
                        {courses.length > 0 ? (
                            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                                {courses.map((c, i) => (
                                    <li key={c.id} style={{
                                        display: 'flex', alignItems: 'center', gap: '0.75rem',
                                        padding: '0.6rem 0', borderBottom: i < courses.length - 1 ? '1px solid var(--border)' : 'none',
                                    }}>
                                        <span style={{
                                            width: '24px', height: '24px', borderRadius: '50%',
                                            background: 'var(--accent-light)', color: 'var(--accent)',
                                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                                            fontSize: '0.7rem', fontWeight: 600, flexShrink: 0,
                                        }}>{i + 1}</span>
                                        <span style={{ flex: 1, fontSize: '0.85rem' }}>{c.title}</span>
                                        <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>{c.enrollment_count} enrolled</span>
                                    </li>
                                ))}
                            </ul>
                        ) : <p className="mono" style={{ color: 'var(--text-muted)' }}>No courses yet.</p>}
                    </div>
                    <div style={{
                        background: 'var(--bg)',
                        border: '1px solid var(--border)',
                        borderRadius: 'var(--radius-lg)',
                        padding: '1.25rem',
                    }}>
                        <h3 style={{ fontSize: '0.9rem', marginBottom: '1rem', color: 'var(--text-primary)' }}>Top 5 Mentors</h3>
                        {mentors.length > 0 ? (
                            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                                {mentors.map((m, i) => (
                                    <li key={m.id} style={{
                                        display: 'flex', alignItems: 'center', gap: '0.75rem',
                                        padding: '0.6rem 0', borderBottom: i < mentors.length - 1 ? '1px solid var(--border)' : 'none',
                                    }}>
                                        <span style={{
                                            width: '24px', height: '24px', borderRadius: '50%',
                                            background: '#fef3c7', color: '#d97706',
                                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                                            fontSize: '0.7rem', fontWeight: 600, flexShrink: 0,
                                        }}>{i + 1}</span>
                                        <span style={{ flex: 1, fontSize: '0.85rem' }}>{m.username}</span>
                                        <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>{Number(m.avg_rating || 0).toFixed(1)}</span>
                                    </li>
                                ))}
                            </ul>
                        ) : <p className="mono" style={{ color: 'var(--text-muted)' }}>No mentors yet.</p>}
                    </div>
                </div>
            </div>
        );
    };

    const tableStyle = {
        width: '100%',
        borderCollapse: 'collapse',
        background: 'var(--bg)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        overflow: 'hidden',
    };

    const thStyle = {
        textAlign: 'left',
        padding: '0.75rem 1rem',
        fontSize: '0.75rem',
        fontWeight: 600,
        color: 'var(--text-tertiary)',
        textTransform: 'uppercase',
        letterSpacing: '0.06em',
        background: 'var(--surface)',
        borderBottom: '1px solid var(--border-strong)',
    };

    const tdStyle = {
        padding: '0.7rem 1rem',
        fontSize: '0.85rem',
        color: 'var(--text-secondary)',
        borderBottom: '1px solid var(--border)',
    };

    const badge = (text, variant) => {
        const colors = {
            success: { bg: '#f0fdf4', color: '#16a34a' },
            danger: { bg: '#fef2f2', color: '#dc2626' },
            warning: { bg: '#fffbeb', color: '#d97706' },
            info: { bg: '#eff6ff', color: '#2563eb' },
        };
        const c = colors[variant] || colors.info;
        return (
            <span style={{
                display: 'inline-block',
                padding: '2px 10px',
                borderRadius: 'var(--radius-pill)',
                fontSize: '0.72rem',
                fontWeight: 600,
                background: c.bg,
                color: c.color,
            }}>{text}</span>
        );
    };

    const actionBtn = (label, onClick, variant = 'secondary') => (
        <button
            onClick={onClick}
            className={`btn btn-sm ${variant === 'danger' ? 'btn-secondary' : variant === 'primary' ? 'btn-primary' : 'btn-secondary'}`}
            style={{
                marginRight: '6px',
                fontSize: '0.72rem',
                padding: '4px 12px',
                ...(variant === 'danger' ? { color: '#dc2626', borderColor: '#fca5a5' } : {}),
            }}
        >
            {label}
        </button>
    );

    const renderUsers = () => {
        const users = list(data);
        const filtered = userSearch ? users.filter(u =>
            u.username.toLowerCase().includes(userSearch.toLowerCase()) ||
            u.email?.toLowerCase().includes(userSearch.toLowerCase())
        ) : users;

        return (
            <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h2 style={{ margin: 0 }}>Users</h2>
                    <input
                        type="text"
                        placeholder="Search by username or email..."
                        value={userSearch}
                        onChange={e => setUserSearch(e.target.value)}
                        className="form-input"
                        style={{ maxWidth: '300px', fontSize: '0.85rem' }}
                    />
                </div>
                <table style={tableStyle}>
                    <thead>
                        <tr>
                            <th style={thStyle}>ID</th>
                            <th style={thStyle}>Username</th>
                            <th style={thStyle}>Role</th>
                            <th style={thStyle}>Status</th>
                            <th style={thStyle}>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filtered.length > 0 ? filtered.map(user => (
                            <tr key={user.id} style={{ transition: 'background 0.1s' }}
                                onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-subtle)'}
                                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                            >
                                <td style={tdStyle}>{user.id}</td>
                                <td style={{ ...tdStyle, fontWeight: 500, color: 'var(--text-primary)' }}>{user.username}</td>
                                <td style={tdStyle}>{badge(user.role, user.role === 'ADMIN' ? 'info' : user.role === 'MENTOR' ? 'warning' : 'success')}</td>
                                <td style={tdStyle}>{user.is_active ? badge('Active', 'success') : badge('Banned', 'danger')}</td>
                                <td style={tdStyle}>
                                    {actionBtn(user.is_active ? 'Ban' : 'Unban', () => handleAction(`/admin/users/${user.id}/ban/`), user.is_active ? 'danger' : 'secondary')}
                                    {actionBtn('Delete', () => handleAction(`/admin/users/${user.id}/`, 'delete'), 'danger')}
                                </td>
                            </tr>
                        )) : (
                            <tr>
                                <td colSpan="5" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                                    {userSearch ? 'No users match your search.' : 'No users found.'}
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        );
    };

    const renderMentors = () => (
        <div>
            <h2 style={{ marginBottom: '1rem' }}>Mentor Approvals</h2>
            <table style={tableStyle}>
                <thead>
                    <tr>
                        <th style={thStyle}>Username</th>
                        <th style={thStyle}>Email</th>
                        <th style={thStyle}>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {list(data).length > 0 ? list(data).map(mentor => (
                        <tr key={mentor.id}
                            onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-subtle)'}
                            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                        >
                            <td style={{ ...tdStyle, fontWeight: 500, color: 'var(--text-primary)' }}>{mentor.username}</td>
                            <td style={tdStyle}>{mentor.email}</td>
                            <td style={tdStyle}>
                                {actionBtn('Approve', () => handleAction(`/admin/mentors/${mentor.id}/approve/`), 'primary')}
                                {actionBtn('Reject', () => handleAction(`/admin/mentors/${mentor.id}/reject/`), 'danger')}
                            </td>
                        </tr>
                    )) : (
                        <tr>
                            <td colSpan="3" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>No pending mentor approvals.</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );

    const renderCourses = () => (
        <div>
            <h2 style={{ marginBottom: '1rem' }}>Course Approvals</h2>
            <table style={tableStyle}>
                <thead>
                    <tr>
                        <th style={thStyle}>Title</th>
                        <th style={thStyle}>Mentor</th>
                        <th style={thStyle}>Category</th>
                        <th style={thStyle}>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {list(data).length > 0 ? list(data).map(course => (
                        <tr key={course.id}
                            onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-subtle)'}
                            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                        >
                            <td style={{ ...tdStyle, fontWeight: 500, color: 'var(--text-primary)' }}>{course.title}</td>
                            <td style={tdStyle}>{course.mentor_name}</td>
                            <td style={tdStyle}>{badge(course.category, 'warning')}</td>
                            <td style={tdStyle}>
                                {actionBtn('Approve', () => handleAction(`/admin/courses/${course.id}/approve/`), 'primary')}
                                {actionBtn('Reject', () => {
                                    const reason = prompt('Reason for rejection?');
                                    if (reason) handleAction(`/admin/courses/${course.id}/reject/`, 'post', { reason });
                                }, 'danger')}
                            </td>
                        </tr>
                    )) : (
                        <tr>
                            <td colSpan="4" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>No pending course approvals.</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );

    const renderModeration = () => (
        <div>
            <h2 style={{ marginBottom: '1rem' }}>Moderation</h2>

            <h3 style={{ fontSize: '0.9rem', marginBottom: '0.75rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <IconFlag /> Flagged Reviews
            </h3>
            <table style={tableStyle}>
                <thead>
                    <tr>
                        <th style={thStyle}>Review</th>
                        <th style={thStyle}>Student</th>
                        <th style={thStyle}>Reason</th>
                        <th style={thStyle}>Reported By</th>
                        <th style={thStyle}>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {list(data?.reviews).length > 0 ? list(data.reviews).map(r => (
                        <tr key={r.id}
                            onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-subtle)'}
                            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                        >
                            <td style={tdStyle}>{r.review_text}</td>
                            <td style={tdStyle}>{r.student_name}</td>
                            <td style={tdStyle}>{(r.reports && r.reports[0]?.reason) || '—'}</td>
                            <td style={tdStyle}>{(r.reports && r.reports[0]?.reported_by) || '—'}</td>
                            <td style={tdStyle}>
                                <div style={{ display: 'flex', gap: '6px' }}>
                                    {actionBtn('Unflag', () => handleAction(`/admin/reviews/${r.id}/unflag/`), 'secondary')}
                                    {actionBtn('Delete', () => handleAction(`/admin/reviews/${r.id}/delete_review/`), 'danger')}
                                </div>
                            </td>
                        </tr>
                    )) : (
                        <tr>
                            <td colSpan="5" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>No flagged reviews.</td>
                        </tr>
                    )}
                </tbody>
            </table>

            <h3 style={{ fontSize: '0.9rem', margin: '1.5rem 0 0.75rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <IconFlag /> Flagged Q&amp;A
            </h3>
            <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1, background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1rem' }}>
                    <h4 style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.75rem' }}>Questions</h4>
                    {list(data?.questions).length > 0 ? list(data.questions).map(q => (
                        <div key={q.id} style={{
                            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                            padding: '0.5rem 0', borderBottom: '1px solid var(--border)',
                        }}>
                            <span style={{ fontSize: '0.85rem' }}>{q.title}</span>
                            {actionBtn('Delete', () => handleAction(`/admin/qna/${q.id}/delete_question/`), 'danger')}
                        </div>
                    )) : <p className="mono" style={{ color: 'var(--text-muted)' }}>No flagged questions.</p>}
                </div>
                <div style={{ flex: 1, background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1rem' }}>
                    <h4 style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.75rem' }}>Replies</h4>
                    {list(data?.replies).length > 0 ? list(data.replies).map(r => (
                        <div key={r.id} style={{
                            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                            padding: '0.5rem 0', borderBottom: '1px solid var(--border)',
                        }}>
                            <span style={{ fontSize: '0.85rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '300px' }}>{r.body}</span>
                            {actionBtn('Delete', () => handleAction(`/admin/qna/${r.id}/delete_reply/`), 'danger')}
                        </div>
                    )) : <p className="mono" style={{ color: 'var(--text-muted)' }}>No flagged replies.</p>}
                </div>
            </div>
        </div>
    );

    const renderRefunds = () => (
        <div>
            <h2 style={{ marginBottom: '1rem' }}>Refund Requests</h2>
            <table style={tableStyle}>
                <thead>
                    <tr>
                        <th style={thStyle}>User</th>
                        <th style={thStyle}>Course</th>
                        <th style={thStyle}>Amount</th>
                        <th style={thStyle}>Provider</th>
                        <th style={thStyle}>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {list(data).length > 0 ? list(data).map(payment => (
                        <tr key={payment.id}
                            onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-subtle)'}
                            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                        >
                            <td style={{ ...tdStyle, fontWeight: 500, color: 'var(--text-primary)' }}>{payment.user_name}</td>
                            <td style={tdStyle}>{payment.course_title}</td>
                            <td style={tdStyle}><span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>${payment.amount}</span></td>
                            <td style={tdStyle}>{badge(payment.provider, payment.provider === 'STRIPE' ? 'info' : 'warning')}</td>
                            <td style={tdStyle}>
                                {actionBtn('Approve', () => handleAction(`/admin/refunds/${payment.id}/approve/`), 'primary')}
                                {actionBtn('Reject', () => {
                                    const reason = prompt('Reason for rejection?');
                                    if (reason) handleAction(`/admin/refunds/${payment.id}/reject/`, 'post', { reason });
                                }, 'danger')}
                            </td>
                        </tr>
                    )) : (
                        <tr>
                            <td colSpan="5" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>No refund requests.</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );

    return (
        <div className="page" style={{ maxWidth: '1280px', margin: '0 auto', padding: '40px 48px', display: 'flex', gap: '2rem' }}>
            <aside style={{
                width: '220px',
                flexShrink: 0,
            }}>
                <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18"/></svg>
                    Admin Panel
                </h2>
                <nav style={{
                    background: 'var(--bg)',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius-lg)',
                    overflow: 'hidden',
                }}>
                    {sections.map(s => (
                        <button
                            key={s.id}
                            onClick={() => setActiveSection(s.id)}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '10px',
                                width: '100%',
                                padding: '0.7rem 1rem',
                                border: 'none',
                                borderBottom: '1px solid var(--border)',
                                background: activeSection === s.id ? 'var(--accent-light)' : 'transparent',
                                color: activeSection === s.id ? 'var(--accent)' : 'var(--text-secondary)',
                                fontWeight: activeSection === s.id ? 600 : 400,
                                cursor: 'pointer',
                                fontSize: '0.85rem',
                                textAlign: 'left',
                                transition: 'all 0.1s',
                            }}
                            onMouseEnter={e => { if (activeSection !== s.id) e.currentTarget.style.background = 'var(--bg-subtle)'; }}
                            onMouseLeave={e => { if (activeSection !== s.id) e.currentTarget.style.background = 'transparent'; }}
                        >
                            <s.Icon />
                            {s.label}
                        </button>
                    ))}
                </nav>
            </aside>

            <main style={{ flex: 1, minWidth: 0 }}>
                {loading ? (
                    <div className="loading-state" style={{ padding: '3rem 0' }}>
                        <div className="spinner" />
                        Loading...
                    </div>
                ) : (
                    <>
                        {error && (
                            <div style={{
                                background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 'var(--radius-md)',
                                padding: '0.75rem 1rem', marginBottom: '1rem', color: '#dc2626', fontSize: '0.85rem',
                            }}>
                                {error}
                            </div>
                        )}
                        {activeSection === 'reports' && renderReports()}
                        {activeSection === 'users' && renderUsers()}
                        {activeSection === 'mentors' && renderMentors()}
                        {activeSection === 'courses' && renderCourses()}
                        {activeSection === 'moderation' && renderModeration()}
                        {activeSection === 'refunds' && renderRefunds()}
                    </>
                )}
            </main>
        </div>
    );
}

export default AdminDashboard;
