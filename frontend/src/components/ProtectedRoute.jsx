import { Navigate } from 'react-router-dom';
import { getRole, isAuthenticated } from '../auth';

const ProtectedRoute = ({ children, allowedRoles }) => {
    const role = getRole();
    const authed = isAuthenticated();

    if (!authed) {
        return <Navigate to="/login" />;
    }

    if (allowedRoles && !allowedRoles.includes(role)) {
        return <Navigate to="/" />;
    }

    return children;
};

export default ProtectedRoute;
