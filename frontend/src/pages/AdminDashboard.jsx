import { useState, useEffect } from 'react';
import api from '../api';

function AdminDashboard() {
    const [activeSection, setActiveSection] = useState('reports');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const sections = [
        { id: 'reports', label: 'Reports' },
        { id: 'users', label: 'Users' },
        { id: 'mentors', label: 'Mentor Approvals' },
        { id: 'courses', label: 'Course Approvals' },
        { id: 'moderation', label: 'Moderation' },
        { id: 'refunds', label: 'Refunds' },
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

    const renderReports = () => {
        const stats = data?.stats;
        if (!stats) return <p className="mono" style={{ color: 'var(--text-muted)' }}>No report data available.</p>;
        const courses = Array.isArray(data?.top_courses) ? data.top_courses : [];
        const mentors = Array.isArray(data?.top_mentors) ? data.top_mentors : [];
        return (
            <div>
                <h2>Platform Reports</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
                    <div className="card"><h3>Total Users</h3><p>{stats.total_users}</p></div>
                    <div className="card"><h3>Total Mentors</h3><p>{stats.total_mentors}</p></div>
                    <div className="card"><h3>Total Students</h3><p>{stats.total_students}</p></div>
                    <div className="card"><h3>Total Courses</h3><p>{stats.total_courses}</p></div>
                    <div className="card"><h3>Total Enrollments</h3><p>{stats.total_enrollments}</p></div>
                    <div className="card"><h3>Total Revenue</h3><p>${stats.total_revenue}</p></div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                    <div>
                        <h3>Top 5 Courses</h3>
                        {courses.length > 0 ? (
                            <ul>{courses.map(c => <li key={c.id}>{c.title} ({c.enrollment_count} students)</li>)}</ul>
                        ) : <p className="mono" style={{ color: 'var(--text-muted)' }}>No courses yet.</p>}
                    </div>
                    <div>
                        <h3>Top 5 Mentors</h3>
                        {mentors.length > 0 ? (
                            <ul>{mentors.map(m => <li key={m.id}>{m.username} ({Number(m.avg_rating || 0).toFixed(1)} ⭐)</li>)}</ul>
                        ) : <p className="mono" style={{ color: 'var(--text-muted)' }}>No mentors yet.</p>}
                    </div>
                </div>
            </div>
        );
    };

    const list = (items) => Array.isArray(items) ? items : [];

    const renderUsers = () => (
        <table>
            <thead>
                <tr><th>ID</th><th>Username</th><th>Role</th><th>Active</th><th>Actions</th></tr>
            </thead>
            <tbody>
                {list(data).length > 0 ? list(data).map(user => (
                    <tr key={user.id}>
                        <td>{user.id}</td>
                        <td>{user.username}</td>
                        <td>{user.role}</td>
                        <td>{user.is_active ? 'Yes' : 'No'}</td>
                        <td>
                            <button onClick={() => handleAction(`/admin/users/${user.id}/ban/`)}>
                                {user.is_active ? 'Ban' : 'Unban'}
                            </button>
                            <button onClick={() => handleAction(`/admin/users/${user.id}/`, 'delete')} style={{ color: 'red' }}>Delete</button>
                        </td>
                    </tr>
                )) : <tr><td colSpan="5" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>No users found.</td></tr>}
            </tbody>
        </table>
    );

    const renderMentors = () => (
        <table>
            <thead>
                <tr><th>Username</th><th>Email</th><th>Actions</th></tr>
            </thead>
            <tbody>
                {list(data).length > 0 ? list(data).map(mentor => (
                    <tr key={mentor.id}>
                        <td>{mentor.username}</td>
                        <td>{mentor.email}</td>
                        <td>
                            <button onClick={() => handleAction(`/admin/mentors/${mentor.id}/approve/`)}>Approve</button>
                            <button onClick={() => handleAction(`/admin/mentors/${mentor.id}/reject/`)} style={{ color: 'red' }}>Reject</button>
                        </td>
                    </tr>
                )) : <tr><td colSpan="3" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>No pending mentors.</td></tr>}
            </tbody>
        </table>
    );

    const renderCourses = () => (
        <table>
            <thead>
                <tr><th>Title</th><th>Mentor</th><th>Category</th><th>Actions</th></tr>
            </thead>
            <tbody>
                {list(data).length > 0 ? list(data).map(course => (
                    <tr key={course.id}>
                        <td>{course.title}</td>
                        <td>{course.mentor_name}</td>
                        <td>{course.category}</td>
                        <td>
                            <button onClick={() => handleAction(`/admin/courses/approval/${course.id}/approve/`)}>Approve</button>
                            <button onClick={() => {
                                const reason = prompt('Reason for rejection?');
                                if (reason) handleAction(`/admin/courses/approval/${course.id}/reject/`, 'post', { reason });
                            }} style={{ color: 'red' }}>Reject</button>
                        </td>
                    </tr>
                )) : <tr><td colSpan="4" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>No pending courses.</td></tr>}
            </tbody>
        </table>
    );

    const renderModeration = () => (
        <div>
            <h3>Flagged Reviews</h3>
            <table>
                <thead><tr><th>Review</th><th>Student</th><th>Actions</th></tr></thead>
                <tbody>
                    {list(data?.reviews).length > 0 ? list(data.reviews).map(r => (
                        <tr key={r.id}>
                            <td>{r.review_text}</td>
                            <td>{r.student_name}</td>
                            <td><button onClick={() => handleAction(`/admin/reviews/${r.id}/delete_review/`, 'delete')}>Delete</button></td>
                        </tr>
                    )) : <tr><td colSpan="3" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>No flagged reviews.</td></tr>}
                </tbody>
            </table>
            <h3 style={{ marginTop: '2rem' }}>Flagged Q&A</h3>
            <h4>Questions</h4>
            {list(data?.questions).length > 0 ? list(data.questions).map(q => (
                <div key={q.id}>{q.title} <button onClick={() => handleAction(`/admin/qna/${q.id}/delete_question/`, 'delete')}>Delete</button></div>
            )) : <p className="mono" style={{ color: 'var(--text-muted)' }}>No flagged questions.</p>}
            <h4>Replies</h4>
            {list(data?.replies).length > 0 ? list(data.replies).map(r => (
                <div key={r.id}>{r.body} <button onClick={() => handleAction(`/admin/qna/${r.id}/delete_reply/`, 'delete')}>Delete</button></div>
            )) : <p className="mono" style={{ color: 'var(--text-muted)' }}>No flagged replies.</p>}
        </div>
    );

    const renderRefunds = () => (
        <table>
            <thead>
                <tr><th>User</th><th>Course</th><th>Amount</th><th>Provider</th><th>Actions</th></tr>
            </thead>
            <tbody>
                {list(data).length > 0 ? list(data).map(payment => (
                    <tr key={payment.id}>
                        <td>{payment.user_name}</td>
                        <td>{payment.course_title}</td>
                        <td>${payment.amount}</td>
                        <td>{payment.provider}</td>
                        <td>
                            <button onClick={() => handleAction(`/admin/refunds/${payment.id}/approve/`)}>Approve</button>
                            <button onClick={() => {
                                const reason = prompt('Reason for rejection?');
                                if (reason) handleAction(`/admin/refunds/${payment.id}/reject/`, 'post', { reason });
                            }} style={{ color: 'red' }}>Reject</button>
                        </td>
                    </tr>
                )) : <tr><td colSpan="5" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>No refund requests.</td></tr>}
            </tbody>
        </table>
    );

    return (
        <div style={{ display: 'flex', gap: '2rem' }}>
            <aside style={{ width: '200px', borderRight: '1px solid #ddd' }}>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                    {sections.map(s => (
                        <li key={s.id} 
                            onClick={() => setActiveSection(s.id)}
                            style={{ 
                                padding: '0.5rem', 
                                cursor: 'pointer', 
                                backgroundColor: activeSection === s.id ? '#eee' : 'transparent',
                                fontWeight: activeSection === s.id ? 'bold' : 'normal'
                            }}>
                            {s.label}
                        </li>
                    ))}
                </ul>
            </aside>
            <main style={{ flex: 1 }}>
                {loading ? <p>Loading...</p> : (
                    <>
                        {error && <p style={{ color: 'red' }}>{error}</p>}
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
