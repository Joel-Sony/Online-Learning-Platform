from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class UserRegistrationTests(APITestCase):
    def test_register_student(self):
        data = {'username': 'student1', 'email': 'student1@test.com', 'password': 'pass1234', 'role': 'STUDENT'}
        response = self.client.post('/api/users/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='student1')
        self.assertEqual(user.role, 'STUDENT')
        self.assertFalse(user.is_mentor_approved)

    def test_register_mentor(self):
        data = {'username': 'mentor1', 'email': 'mentor1@test.com', 'password': 'pass1234', 'role': 'MENTOR'}
        response = self.client.post('/api/users/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='mentor1')
        self.assertEqual(user.role, 'MENTOR')
        self.assertFalse(user.is_mentor_approved)

    def test_register_duplicate_username(self):
        User.objects.create_user(username='dup', password='pass1234')
        data = {'username': 'dup', 'password': 'pass1234', 'role': 'STUDENT'}
        response = self.client.post('/api/users/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123', role='STUDENT')

    def test_login_success(self):
        response = self.client.post('/api/users/login/', {'username': 'testuser', 'password': 'testpass123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post('/api/users/login/', {'username': 'testuser', 'password': 'wrongpass'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserDetailTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123', role='STUDENT')

    def test_get_me_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['role'], 'STUDENT')

    def test_get_me_unauthenticated(self):
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_me(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch('/api/users/me/', {'bio': 'Hello world'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, 'Hello world')

    def test_cannot_change_role_through_me(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch('/api/users/me/', {'role': 'MENTOR'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'STUDENT')  # role is read_only


class RoleBasedAccessTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT')
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR')
        self.admin = User.objects.create_user(username='admin', password='pass1234', role='ADMIN', is_staff=True)

    def test_student_role_assignment(self):
        self.assertEqual(self.student.role, 'STUDENT')

    def test_mentor_role_assignment(self):
        self.assertEqual(self.mentor.role, 'MENTOR')
        self.assertFalse(self.mentor.is_mentor_approved)

    def test_admin_role_assignment(self):
        self.assertEqual(self.admin.role, 'ADMIN')

    def test_default_role_is_student(self):
        user = User.objects.create_user(username='default', password='pass1234')
        self.assertEqual(user.role, 'STUDENT')


class MentorApprovalTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass1234', role='ADMIN', is_staff=True)
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR', is_mentor_approved=False)

    def test_admin_can_view_pending_mentors(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/admin/mentors/pending/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_non_admin_cannot_view_pending_mentors(self):
        user = User.objects.create_user(username='regular', password='pass1234', role='STUDENT')
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/admin/mentors/pending/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_approve_mentor(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/admin/mentors/{self.mentor.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mentor.refresh_from_db()
        self.assertTrue(self.mentor.is_mentor_approved)

    def test_admin_can_reject_mentor(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/admin/mentors/{self.mentor.id}/reject/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mentor.refresh_from_db()
        self.assertFalse(self.mentor.is_mentor_approved)


class AdminUserManagementTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass1234', role='ADMIN', is_staff=True)
        self.user = User.objects.create_user(username='testuser', password='pass1234', role='STUDENT')

    def test_admin_can_list_users(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_admin_can_ban_user(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/admin/users/{self.user.id}/ban/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_admin_can_unban_user(self):
        self.user.is_active = False
        self.user.save()
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/admin/users/{self.user.id}/ban/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
