import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import CourseDetails from './pages/CourseDetails';
import MentorDashboard from './pages/MentorDashboard';
import CreateCourse from './pages/CreateCourse';
import EditCourse from './pages/EditCourse';
import MentorAnalytics from './pages/MentorAnalytics';

import LearningDashboard from './pages/LearningDashboard';
import QAPage from './pages/QAPage';
import Notifications from './pages/Notifications';
import CourseList from './pages/CourseList';
import CreateAnnouncement from './pages/CreateAnnouncement';
import PaymentSuccess from './pages/PaymentSuccess';
import PaymentFailed from './pages/PaymentFailed';


import AdminDashboard from './pages/AdminDashboard';
import AdminRoute from './components/AdminRoute';

function App() {
  return (
    <Router>
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Navbar />
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/courses" element={<CourseList />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/courses/:id" element={<CourseDetails />} />
            <Route path="/mentor" element={<MentorDashboard />} />
            <Route path="/mentor/create" element={<CreateCourse />} />
            <Route path="/mentor/edit/:id" element={<EditCourse />} />
            <Route path="/mentor/analytics" element={<MentorAnalytics />} />

            <Route path="/learning" element={<LearningDashboard />} />
            <Route path="/courses/:id/qa" element={<QAPage />} />
            <Route path="/notifications" element={<Notifications />} />
            <Route path="/mentor/announcement" element={<CreateAnnouncement />} />
            <Route path="/payment-success" element={<PaymentSuccess />} />
            <Route path="/payment-failed" element={<PaymentFailed />} />

            <Route 
              path="/admin" 
              element={
                <AdminRoute>
                  <AdminDashboard />
                </AdminRoute>
              } 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
