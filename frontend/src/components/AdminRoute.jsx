import { Navigate } from 'react-router-dom';

const AdminRoute = ({ children }) => {
    const role = localStorage.getItem('role');
    const isAuthenticated = !!localStorage.getItem('access');

    if (!isAuthenticated || role !== 'ADMIN') {
        return <Navigate to="/" />;
    }

    return children;
};

export default AdminRoute;
