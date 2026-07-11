from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from courses.models import Course
from notifications.models import Notification, Announcement
from enrollments.models import Enrollment

User = get_user_model()


class NotificationTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT')
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR')
        self.course = Course.objects.create(
            title='Test Course', description='Desc', category='Programming', level='BEGINNER',
            language='English', price=0, mentor=self.mentor, is_published=True
        )

    def test_create_notification(self):
        notification = Notification.objects.create(
            recipient=self.student, type='ENROLLMENT', message='Welcome!'
        )
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(notification.recipient, self.student)
        self.assertFalse(notification.is_read)

    def test_notification_default_unread(self):
        notification = Notification.objects.create(
            recipient=self.student, type='ENROLLMENT', message='Welcome!'
        )
        self.assertFalse(notification.is_read)

    def test_student_sees_own_notifications(self):
        Notification.objects.create(recipient=self.student, type='ENROLLMENT', message='Welcome!')
        other = User.objects.create_user(username='other', password='pass1234', role='STUDENT')
        Notification.objects.create(recipient=other, type='ENROLLMENT', message='Other notif')
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_mark_notification_as_read(self):
        notification = Notification.objects.create(
            recipient=self.student, type='ENROLLMENT', message='Welcome!'
        )
        self.client.force_authenticate(user=self.student)
        response = self.client.post(f'/api/notifications/{notification.id}/read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_mark_all_notifications_as_read(self):
        Notification.objects.create(recipient=self.student, type='ENROLLMENT', message='Notif 1')
        Notification.objects.create(recipient=self.student, type='NEW_LESSON', message='Notif 2')
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/notifications/read-all/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unread = Notification.objects.filter(recipient=self.student, is_read=False).count()
        self.assertEqual(unread, 0)

    def test_unauthenticated_cannot_view_notifications(self):
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_notification_read_only(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/notifications/', {
            'recipient': self.student.id, 'type': 'ENROLLMENT', 'message': 'Test'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_notification_ordering(self):
        Notification.objects.create(recipient=self.student, type='ENROLLMENT', message='Old')
        import time
        time.sleep(0.01)
        Notification.objects.create(recipient=self.student, type='NEW_LESSON', message='New')
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.data[0]['message'], 'New')


class AnnouncementTests(APITestCase):
    def setUp(self):
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR', is_mentor_approved=True)
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT')
        self.course = Course.objects.create(
            title='Test Course', description='Desc', category='Programming', level='BEGINNER',
            language='English', price=0, mentor=self.mentor, is_published=True
        )
        Enrollment.objects.create(student=self.student, course=self.course)

    def test_mentor_can_create_announcement(self):
        self.client.force_authenticate(user=self.mentor)
        response = self.client.post('/api/announcements/', {
            'course': self.course.id, 'title': 'Important', 'content': 'Please read'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Announcement.objects.count(), 1)

    def test_announcement_creates_notifications_for_enrolled(self):
        self.client.force_authenticate(user=self.mentor)
        self.client.post('/api/announcements/', {
            'course': self.course.id, 'title': 'Important', 'content': 'Please read'
        }, format='json')
        notifications = Notification.objects.filter(recipient=self.student)
        self.assertEqual(notifications.count(), 1)
        self.assertEqual(notifications.first().type, 'ANNOUNCEMENT')

    def test_list_announcements(self):
        Announcement.objects.create(course=self.course, mentor=self.mentor, title='A1', content='C1')
        Announcement.objects.create(course=self.course, mentor=self.mentor, title='A2', content='C2')
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/announcements/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_announcement_mentor_set_automatically(self):
        self.client.force_authenticate(user=self.mentor)
        response = self.client.post('/api/announcements/', {
            'course': self.course.id, 'title': 'Important', 'content': 'Read'
        }, format='json')
        self.assertEqual(response.data['mentor'], self.mentor.id)

    def test_unauthenticated_cannot_create_announcement(self):
        response = self.client.post('/api/announcements/', {
            'course': self.course.id, 'title': 'Test', 'content': 'Test'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
