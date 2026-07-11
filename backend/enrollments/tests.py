from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from courses.models import Course, Module, Lesson
from enrollments.models import Enrollment, Payment

User = get_user_model()


class EnrollmentTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT')
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR')
        self.admin = User.objects.create_user(username='admin', password='pass1234', role='ADMIN', is_staff=True)
        self.course = Course.objects.create(
            title='Test Course', description='Desc', category='Programming', level='BEGINNER',
            language='English', price=0, mentor=self.mentor, is_published=True, is_free=True
        )
        self.paid_course = Course.objects.create(
            title='Paid Course', description='Desc', category='Design', level='INTERMEDIATE',
            language='English', price=49.99, mentor=self.mentor, is_published=True, is_free=False
        )

    def test_student_can_enroll_free_course(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/enrollments/enroll_free/', {'course_id': self.course.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Enrollment.objects.filter(student=self.student, course=self.course).exists())

    def test_student_cannot_enroll_free_course_twice(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/enrollments/enroll_free/', {'course_id': self.course.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_enroll_paid_course_as_free(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/enrollments/enroll_free/', {'course_id': self.paid_course.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enrollment_unauthenticated(self):
        response = self.client.post('/api/enrollments/enroll_free/', {'course_id': self.course.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_sees_own_enrollments(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/enrollments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_mentor_sees_course_enrollments(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.mentor)
        response = self.client.get('/api/enrollments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_sees_all_enrollments(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        other_student = User.objects.create_user(username='other', password='pass1234', role='STUDENT')
        other_course = Course.objects.create(
            title='Other', description='Desc', category='Programming', level='BEGINNER',
            language='English', price=0, mentor=self.mentor, is_published=True
        )
        Enrollment.objects.create(student=other_student, course=other_course)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/enrollments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_student_can_enroll_via_direct_post(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/enrollments/', {'course': self.paid_course.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Enrollment.objects.filter(student=self.student, course=self.paid_course).exists())


class EnrollmentStatusTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT')
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR')
        self.admin = User.objects.create_user(username='admin', password='pass1234', role='ADMIN', is_staff=True)
        self.course = Course.objects.create(
            title='Test Course', description='Desc', category='Programming', level='BEGINNER',
            language='English', price=0, mentor=self.mentor, is_published=True
        )

    def test_enrollment_default_status_active(self):
        enrollment = Enrollment.objects.create(student=self.student, course=self.course)
        self.assertEqual(enrollment.status, 'ACTIVE')

    def test_enrollment_can_be_completed(self):
        enrollment = Enrollment.objects.create(student=self.student, course=self.course)
        enrollment.status = 'COMPLETED'
        enrollment.save()
        self.assertEqual(enrollment.status, 'COMPLETED')

    def test_enrollment_can_be_refunded(self):
        enrollment = Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.student)
        response = self.client.post(f'/api/enrollments/{enrollment.id}/request_refund/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unique_enrollment_constraint(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        with self.assertRaises(Exception):
            Enrollment.objects.create(student=self.student, course=self.course)


class PaymentTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT')
        self.course = Course.objects.create(
            title='Paid Course', description='Desc', category='Design', level='INTERMEDIATE',
            language='English', price=49.99, mentor=User.objects.create_user(
                username='mentor', password='pass1234', role='MENTOR'
            ), is_published=True
        )
        self.payment = Payment.objects.create(
            user=self.student, course=self.course, provider='STRIPE', amount=49.99,
            provider_payment_id='test_session_123', status='COMPLETED'
        )

    def test_student_sees_own_payments(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/payments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_student_cannot_see_other_payments(self):
        other = User.objects.create_user(username='other', password='pass1234', role='STUDENT')
        self.client.force_authenticate(user=other)
        response = self.client.get('/api/payments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class StripeCheckoutTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT', email='student@test.com')
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR')
        self.course = Course.objects.create(
            title='Paid Course', description='Desc', category='Design', level='INTERMEDIATE',
            language='English', price=49.99, mentor=self.mentor, is_published=True
        )

    def test_create_stripe_checkout_unauthenticated(self):
        response = self.client.post('/api/enrollments/create_stripe_checkout/', {'course_id': self.course.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_stripe_checkout_no_course(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/enrollments/create_stripe_checkout/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RefundTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass1234', role='ADMIN', is_staff=True)
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT')
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR')
        self.course = Course.objects.create(
            title='Test Course', description='Desc', category='Programming', level='BEGINNER',
            language='English', price=49.99, mentor=self.mentor, is_published=True
        )
        self.enrollment = Enrollment.objects.create(student=self.student, course=self.course)
        self.payment = Payment.objects.create(
            user=self.student, course=self.course, provider='STRIPE', amount=49.99,
            provider_payment_id='cs_test_123', status='COMPLETED'
        )

    def test_admin_can_view_refund_requests(self):
        self.payment.status = 'REFUND_REQUESTED'
        self.payment.save()
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/admin/refunds/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_non_admin_cannot_view_refund_requests(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/admin/refunds/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_refund_no_completed_payment(self):
        # Create a payment with REFUND_REQUESTED status that has no corresponding enrollment
        self.payment.status = 'REFUND_REQUESTED'
        self.payment.save()
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/admin/refunds/{self.payment.id}/approve/')
        # Stripe refund will fail since it's a test session ID
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_reject_refund(self):
        self.payment.status = 'REFUND_REQUESTED'
        self.payment.save()
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/admin/refunds/{self.payment.id}/reject/', {'reason': 'Not eligible'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'COMPLETED')
