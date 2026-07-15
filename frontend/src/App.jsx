import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import CourseDetails from './pages/CourseDetails';
import MentorDashboard from './pages/MentorDashboard';
import CreateCourse from './pages/CreateCourse';
import EditCourse from './pages/EditCourse';
import MentorAnalytics from './pages/MentorAnalytics';
import EditQuiz from './pages/EditQuiz';
import LearnCourse from './pages/LearnCourse';

import LearningDashboard from './pages/LearningDashboard';
import QAPage from './pages/QAPage';
import Notifications from './pages/Notifications';
import CourseList from './pages/CourseList';
import CreateAnnouncement from './pages/CreateAnnouncement';
import PaymentSuccess from './pages/PaymentSuccess';
import PaymentFailed from './pages/PaymentFailed';
import TakeQuiz from './pages/TakeQuiz';

import AdminDashboard from './pages/AdminDashboard';

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
            <Route path="/courses/:id/qa" element={<QAPage />} />
            <Route path="/quiz/:id" element={<TakeQuiz />} />
            <Route path="/courses/:id/learn" element={<LearnCourse />} />
            <Route path="/courses/:id/learn/:lessonId" element={<LearnCourse />} />

            <Route path="/learning" element={
              <ProtectedRoute allowedRoles={['STUDENT']}>
                <LearningDashboard />
              </ProtectedRoute>
            } />

            <Route path="/notifications" element={
              <ProtectedRoute allowedRoles={['STUDENT', 'MENTOR', 'ADMIN']}>
                <Notifications />
              </ProtectedRoute>
            } />
            <Route path="/payment-success" element={
              <ProtectedRoute allowedRoles={['STUDENT', 'MENTOR', 'ADMIN']}>
                <PaymentSuccess />
              </ProtectedRoute>
            } />
            <Route path="/payment-failed" element={
              <ProtectedRoute allowedRoles={['STUDENT', 'MENTOR', 'ADMIN']}>
                <PaymentFailed />
              </ProtectedRoute>
            } />

            <Route path="/mentor" element={
              <ProtectedRoute allowedRoles={['MENTOR', 'ADMIN']}>
                <MentorDashboard />
              </ProtectedRoute>
            } />
            <Route path="/mentor/create" element={
              <ProtectedRoute allowedRoles={['MENTOR', 'ADMIN']}>
                <CreateCourse />
              </ProtectedRoute>
            } />
            <Route path="/mentor/edit/:id" element={
              <ProtectedRoute allowedRoles={['MENTOR', 'ADMIN']}>
                <EditCourse />
              </ProtectedRoute>
            } />
            <Route path="/mentor/quiz/:id/edit" element={
              <ProtectedRoute allowedRoles={['MENTOR', 'ADMIN']}>
                <EditQuiz />
              </ProtectedRoute>
            } />
            <Route path="/mentor/analytics" element={
              <ProtectedRoute allowedRoles={['MENTOR', 'ADMIN']}>
                <MentorAnalytics />
              </ProtectedRoute>
            } />
            <Route path="/mentor/announcement" element={
              <ProtectedRoute allowedRoles={['MENTOR', 'ADMIN']}>
                <CreateAnnouncement />
              </ProtectedRoute>
            } />

            <Route path="/admin" element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <AdminDashboard />
              </ProtectedRoute>
            } />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
