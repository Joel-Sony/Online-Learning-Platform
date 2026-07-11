from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from courses.models import Course, Module, Lesson
from enrollments.models import Enrollment
from progress.models import LessonProgress, Certificate

User = get_user_model()


class ProgressTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT')
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR')
        self.admin = User.objects.create_user(username='admin', password='pass1234', role='ADMIN', is_staff=True)
        self.course = Course.objects.create(
            title='Test Course', description='Desc', category='Programming', level='BEGINNER',
            language='English', price=0, mentor=self.mentor, is_published=True
        )
        self.module = Module.objects.create(course=self.course, title='Module 1', order=1)
        self.lesson = Lesson.objects.create(module=self.module, title='Lesson 1', lesson_type='VIDEO', order=1)

    def test_mark_lesson_complete_enrolled(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/progress/mark_complete/', {'lesson_id': self.lesson.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(LessonProgress.objects.filter(student=self.student, lesson=self.lesson, completed=True).exists())

    def test_mark_lesson_complete_not_enrolled(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/progress/mark_complete/', {'lesson_id': self.lesson.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_lesson_complete_unauthenticated(self):
        response = self.client.post('/api/progress/mark_complete/', {'lesson_id': self.lesson.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mark_lesson_complete_twice_idempotent(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.student)
        self.client.post('/api/progress/mark_complete/', {'lesson_id': self.lesson.id}, format='json')
        response = self.client.post('/api/progress/mark_complete/', {'lesson_id': self.lesson.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(LessonProgress.objects.filter(student=self.student, lesson=self.lesson).count(), 1)

    def test_student_sees_own_progress(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        LessonProgress.objects.create(student=self.student, course=self.course, lesson=self.lesson, completed=True)
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/progress/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_mentor_sees_student_progress(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        LessonProgress.objects.create(student=self.student, course=self.course, lesson=self.lesson, completed=True)
        self.client.force_authenticate(user=self.mentor)
        response = self.client.get('/api/progress/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_sees_all_progress(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        LessonProgress.objects.create(student=self.student, course=self.course, lesson=self.lesson, completed=True)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/progress/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_course_progress_endpoint(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        LessonProgress.objects.create(student=self.student, course=self.course, lesson=self.lesson, completed=True)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/progress/course_progress/?course_id={self.course.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_lessons'], 1)
        self.assertEqual(response.data['completed_lessons'], 1)
        self.assertEqual(response.data['progress_percentage'], 100.0)

    def test_course_progress_percentage(self):
        lesson2 = Lesson.objects.create(module=self.module, title='Lesson 2', lesson_type='PDF', order=2)
        Enrollment.objects.create(student=self.student, course=self.course)
        LessonProgress.objects.create(student=self.student, course=self.course, lesson=self.lesson, completed=True)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/progress/course_progress/?course_id={self.course.id}')
        self.assertEqual(response.data['total_lessons'], 2)
        self.assertEqual(response.data['completed_lessons'], 1)
        self.assertEqual(response.data['progress_percentage'], 50.0)


class CertificateTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT')
        self.course = Course.objects.create(
            title='Test Course', description='Desc', category='Programming', level='BEGINNER',
            language='English', price=0,
            mentor=User.objects.create_user(username='mentor', password='pass1234', role='MENTOR'),
            is_published=True
        )

    def test_certificate_created_after_all_lessons_completed(self):
        module = Module.objects.create(course=self.course, title='Module 1', order=1)
        lesson = Lesson.objects.create(module=module, title='Lesson 1', lesson_type='VIDEO', order=1)
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.student)
        self.client.post('/api/progress/mark_complete/', {'lesson_id': lesson.id}, format='json')
        self.assertEqual(Certificate.objects.filter(student=self.student, course=self.course).count(), 1)

    def test_student_sees_own_certificates(self):
        cert = Certificate.objects.create(
            student=self.student, course=self.course, certificate_id='CERT-TEST1234'
        )
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/certificates/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['certificate_id'], 'CERT-TEST1234')

    def test_student_cannot_see_others_certificates(self):
        other = User.objects.create_user(username='other', password='pass1234', role='STUDENT')
        Certificate.objects.create(student=other, course=self.course, certificate_id='CERT-OTHER')
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/certificates/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_certificate_download_authenticated(self):
        cert = Certificate.objects.create(
            student=self.student, course=self.course, certificate_id='CERT-TEST1234'
        )
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/certificates/{cert.id}/download/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('text/html', response['Content-Type'])

    def test_certificate_download_unauthenticated(self):
        cert = Certificate.objects.create(
            student=self.student, course=self.course, certificate_id='CERT-TEST1234'
        )
        response = self.client.get(f'/api/certificates/{cert.id}/download/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MentorAnalyticsTests(APITestCase):
    def setUp(self):
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR', is_mentor_approved=True)
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT')
        self.course = Course.objects.create(
            title='Test Course', description='Desc', category='Programming', level='BEGINNER',
            language='English', price=0, mentor=self.mentor, is_published=True
        )
        Enrollment.objects.create(student=self.student, course=self.course)

    def test_mentor_can_view_analytics(self):
        self.client.force_authenticate(user=self.mentor)
        response = self.client.get('/api/mentor-analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['course_title'], 'Test Course')
        self.assertEqual(response.data[0]['total_enrolled'], 1)

    def test_student_cannot_view_analytics(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/mentor-analytics/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_view_analytics(self):
        response = self.client.get('/api/mentor-analytics/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
