from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from courses.models import Course, Module, Lesson, Quiz, QuizQuestion, QuizChoice, QuizAttempt
from enrollments.models import Enrollment

User = get_user_model()


class QuizPipelineTestCase(APITestCase):
    def setUp(self):
        self.mentor = User.objects.create_user(username='mentor_bob', password='password123', role='MENTOR')
        self.student = User.objects.create_user(username='student_alice', password='password123', role='STUDENT')

        self.course = Course.objects.create(
            title='Test Course', description='Test Description', category='Programming',
            level='BEGINNER', language='English', price=0.00, mentor=self.mentor, is_published=True
        )
        self.module = Module.objects.create(course=self.course, title='Module 1', order=1)
        self.lesson1 = Lesson.objects.create(module=self.module, title='Lesson 1', lesson_type='VIDEO', order=1)

        self.quiz = Quiz.objects.create(module=self.module, title='Quiz 1', passing_score=60)

        self.q1 = QuizQuestion.objects.create(quiz=self.quiz, text='What is 2+2?', order=1)
        self.q2 = QuizQuestion.objects.create(quiz=self.quiz, text='What is Python?', order=2)

        self.q1_c1 = QuizChoice.objects.create(question=self.q1, text='3', is_correct=False)
        self.q1_c2 = QuizChoice.objects.create(question=self.q1, text='4', is_correct=True)

        self.q2_c1 = QuizChoice.objects.create(question=self.q2, text='A snake', is_correct=False)
        self.q2_c2 = QuizChoice.objects.create(question=self.q2, text='A programming language', is_correct=True)

    def test_single_correct_choice_enforcement(self):
        self.assertTrue(self.q1_c2.is_correct)
        self.assertFalse(self.q1_c1.is_correct)

        self.q1_c1.is_correct = True
        self.q1_c1.save()

        self.q1_c1.refresh_from_db()
        self.q1_c2.refresh_from_db()

        self.assertTrue(self.q1_c1.is_correct)
        self.assertFalse(self.q1_c2.is_correct)

    def test_submit_quiz_attempt_success(self):
        Enrollment.objects.create(student=self.student, course=self.course, status='ACTIVE')
        self.client.force_authenticate(user=self.student)

        payload = {
            'answers': {
                str(self.q1.id): self.q1_c2.id,
                str(self.q2.id): self.q2_c2.id
            }
        }
        response = self.client.post(f'/api/quizzes/{self.quiz.id}/submit/', payload, format='json')
        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertEqual(data['score'], 100.0)
        self.assertTrue(data['passed'])
        self.assertEqual(data['correct_answers'], 2)
        self.assertEqual(data['total_questions'], 2)

        q_results = data['question_results']
        self.assertEqual(len(q_results), 2)
        self.assertTrue(q_results[0]['is_correct'])
        self.assertEqual(q_results[0]['chosen_choice_text'], '4')
        self.assertEqual(q_results[0]['correct_choice_text'], '4')

    def test_submit_quiz_attempt_partial_fail(self):
        Enrollment.objects.create(student=self.student, course=self.course, status='ACTIVE')
        self.client.force_authenticate(user=self.student)

        payload = {
            'answers': {
                str(self.q1.id): self.q1_c1.id,
                str(self.q2.id): self.q2_c2.id
            }
        }
        response = self.client.post(f'/api/quizzes/{self.quiz.id}/submit/', payload, format='json')
        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertEqual(data['score'], 50.0)
        self.assertFalse(data['passed'])

        q_results = data['question_results']
        self.assertFalse(q_results[0]['is_correct'])
        self.assertEqual(q_results[0]['chosen_choice_text'], '3')
        self.assertEqual(q_results[0]['correct_choice_text'], '4')
        self.assertTrue(q_results[1]['is_correct'])

    def test_submit_quiz_attempt_empty_answers(self):
        Enrollment.objects.create(student=self.student, course=self.course, status='ACTIVE')
        self.client.force_authenticate(user=self.student)

        payload = {'answers': {}}
        response = self.client.post(f'/api/quizzes/{self.quiz.id}/submit/', payload, format='json')
        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertEqual(data['score'], 0.0)
        self.assertFalse(data['passed'])
        self.assertEqual(data['correct_answers'], 0)

    def test_submit_quiz_without_enrollment(self):
        self.client.force_authenticate(user=self.student)
        payload = {'answers': {str(self.q1.id): self.q1_c2.id}}
        response = self.client.post(f'/api/quizzes/{self.quiz.id}/submit/', payload, format='json')
        # Student's queryset only includes enrolled courses' quizzes, so 404
        self.assertEqual(response.status_code, 404)

    def test_submit_quiz_unauthenticated(self):
        payload = {'answers': {str(self.q1.id): self.q1_c2.id}}
        response = self.client.post(f'/api/quizzes/{self.quiz.id}/submit/', payload, format='json')
        self.assertEqual(response.status_code, 401)

    def test_quiz_attempt_created_in_db(self):
        Enrollment.objects.create(student=self.student, course=self.course, status='ACTIVE')
        self.client.force_authenticate(user=self.student)
        payload = {'answers': {str(self.q1.id): self.q1_c2.id, str(self.q2.id): self.q2_c2.id}}
        self.client.post(f'/api/quizzes/{self.quiz.id}/submit/', payload, format='json')
        self.assertEqual(QuizAttempt.objects.count(), 1)
        attempt = QuizAttempt.objects.first()
        self.assertEqual(attempt.student, self.student)
        self.assertEqual(attempt.quiz, self.quiz)


class CourseCRUDTests(APITestCase):
    def setUp(self):
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR', is_mentor_approved=True)
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT')
        self.admin = User.objects.create_user(username='admin', password='pass1234', role='ADMIN', is_staff=True)
        self.course_data = {
            'title': 'New Course',
            'description': 'A great course',
            'category': 'Programming',
            'level': 'BEGINNER',
            'language': 'English',
            'price': 49.99,
            'is_free': False,
        }

    def test_mentor_can_create_course(self):
        self.client.force_authenticate(user=self.mentor)
        response = self.client.post('/api/courses/', self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['mentor'], self.mentor.id)

    def test_student_cannot_create_course(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/courses/', self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anyone_can_view_published_courses(self):
        Course.objects.create(mentor=self.mentor, is_published=True, **self.course_data)
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_unpublished_course_hidden_from_students(self):
        course = Course.objects.create(mentor=self.mentor, is_published=False, **self.course_data)
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_mentor_sees_own_unpublished_courses(self):
        course = Course.objects.create(mentor=self.mentor, is_published=False, **self.course_data)
        self.client.force_authenticate(user=self.mentor)
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_admin_sees_all_courses(self):
        Course.objects.create(mentor=self.mentor, is_published=False, **self.course_data)
        Course.objects.create(mentor=self.mentor, is_published=True, title='Published Course', description='Desc',
                              category='Design', level='INTERMEDIATE', language='English', price=0)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_mentor_can_update_own_course(self):
        course = Course.objects.create(mentor=self.mentor, is_published=True, **self.course_data)
        self.client.force_authenticate(user=self.mentor)
        response = self.client.patch(f'/api/courses/{course.id}/', {'title': 'Updated Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course.refresh_from_db()
        self.assertEqual(course.title, 'Updated Title')

    def test_mentor_cannot_update_other_mentor_course(self):
        other_mentor = User.objects.create_user(username='other_mentor', password='pass1234', role='MENTOR')
        course = Course.objects.create(mentor=other_mentor, **self.course_data)
        self.client.force_authenticate(user=self.mentor)
        response = self.client.patch(f'/api/courses/{course.id}/', {'title': 'Hacked'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mentor_can_delete_own_course(self):
        course = Course.objects.create(mentor=self.mentor, **self.course_data)
        self.client.force_authenticate(user=self.mentor)
        response = self.client.delete(f'/api/courses/{course.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_anonymous_list_courses(self):
        Course.objects.create(mentor=self.mentor, is_published=True, **self.course_data)
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_anonymous_cannot_create_course(self):
        response = self.client.post('/api/courses/', self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CourseFilterTests(APITestCase):
    def setUp(self):
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR')
        for i, (cat, level, price, free) in enumerate([
            ('Programming', 'BEGINNER', 0, True),
            ('Design', 'INTERMEDIATE', 49.99, False),
            ('Programming', 'ADVANCED', 99.99, False),
        ]):
            Course.objects.create(
                title=f'Course {i}', description='Desc', category=cat, level=level,
                language='English', price=price, mentor=self.mentor, is_published=True,
                is_free=free
            )

    def test_filter_by_category(self):
        response = self.client.get('/api/courses/?category=Programming')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filter_by_level(self):
        response = self.client.get('/api/courses/?level=BEGINNER')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_price_range(self):
        response = self.client.get('/api/courses/?price_min=10&price_max=100')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filter_by_free(self):
        response = self.client.get('/api/courses/?is_free=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_search_by_title(self):
        response = self.client.get('/api/courses/?search=Course')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_autocomplete(self):
        response = self.client.get('/api/courses/autocomplete/?q=Cou')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_autocomplete_short_query_returns_empty(self):
        response = self.client.get('/api/courses/autocomplete/?q=C')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class CourseApprovalTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass1234', role='ADMIN', is_staff=True)
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR')
        self.course = Course.objects.create(
            title='Pending Course', description='Desc', category='Programming', level='BEGINNER',
            language='English', price=0, mentor=self.mentor, status='PENDING'
        )

    def test_admin_can_approve_course(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/admin/courses/{self.course.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.status, 'PUBLISHED')
        self.assertTrue(self.course.is_published)

    def test_admin_can_reject_course(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/admin/courses/{self.course.id}/reject/', {'reason': 'Not good enough'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.status, 'REJECTED')
        self.assertFalse(self.course.is_published)

    def test_non_admin_cannot_approve_course(self):
        self.client.force_authenticate(user=self.mentor)
        response = self.client.post(f'/api/admin/courses/{self.course.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_pending_courses(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/admin/courses/pending/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class AdminReportsTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass1234', role='ADMIN', is_staff=True)
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR')
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT')
        self.course = Course.objects.create(
            title='Test Course', description='Desc', category='Programming', level='BEGINNER',
            language='English', price=0, mentor=self.mentor, is_published=True
        )

    def test_admin_can_view_reports(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/admin/reports/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('stats', response.data)
        self.assertIn('top_courses', response.data)
        self.assertIn('top_mentors', response.data)
        self.assertEqual(response.data['stats']['total_users'], 3)
        self.assertEqual(response.data['stats']['total_courses'], 1)

    def test_non_admin_cannot_view_reports(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/admin/reports/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ModuleLessonTests(APITestCase):
    def setUp(self):
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR', is_mentor_approved=True)
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT')
        self.course = Course.objects.create(
            title='Test Course', description='Desc', category='Programming', level='BEGINNER',
            language='English', price=0, mentor=self.mentor, is_published=True
        )

    def test_mentor_can_create_module(self):
        self.client.force_authenticate(user=self.mentor)
        response = self.client.post('/api/modules/', {'course': self.course.id, 'title': 'Module 1', 'order': 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_student_cannot_create_module(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/modules/', {'course': self.course.id, 'title': 'Module 1', 'order': 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mentor_can_create_lesson(self):
        module = Module.objects.create(course=self.course, title='Module 1', order=1)
        self.client.force_authenticate(user=self.mentor)
        response = self.client.post('/api/lessons/', {
            'module': module.id, 'title': 'Lesson 1', 'lesson_type': 'VIDEO', 'video_url': 'http://example.com/video', 'order': 1
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_filter_modules_by_course(self):
        Module.objects.create(course=self.course, title='Module 1', order=1)
        self.client.force_authenticate(user=self.mentor)
        response = self.client.get(f'/api/modules/?course_id={self.course.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class MentorSearchTests(APITestCase):
    def setUp(self):
        self.mentor = User.objects.create_user(username='mentor_john', password='pass1234', role='MENTOR', bio='Expert coder')
        self.student = User.objects.create_user(username='student_jane', password='pass1234', role='STUDENT')

    def test_mentor_search_finds_mentors(self):
        response = self.client.get('/api/mentors/search/?search=john')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_mentor_search_does_not_include_students(self):
        response = self.client.get('/api/mentors/search/?search=jane')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class QuizViewPermissionsTests(APITestCase):
    def setUp(self):
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR')
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT')
        self.course = Course.objects.create(
            title='Test Course', description='Desc', category='Programming', level='BEGINNER',
            language='English', price=0, mentor=self.mentor, is_published=True
        )
        self.module = Module.objects.create(course=self.course, title='Module 1', order=1)
        self.quiz = Quiz.objects.create(module=self.module, title='Quiz 1')

    def test_student_cannot_create_quiz(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/quizzes/', {'module': self.module.id, 'title': 'New Quiz'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mentor_can_create_quiz(self):
        self.client.force_authenticate(user=self.mentor)
        response = self.client.post('/api/quizzes/', {'module': self.module.id, 'title': 'New Quiz'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_student_sees_hides_correct_answers(self):
        Enrollment.objects.create(student=self.student, course=self.course, status='ACTIVE')
        q = QuizQuestion.objects.create(quiz=self.quiz, text='Q1', order=1)
        QuizChoice.objects.create(question=q, text='Correct', is_correct=True)
        QuizChoice.objects.create(question=q, text='Wrong', is_correct=False)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/quizzes/{self.quiz.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        question_data = response.data['questions'][0]
        for choice in question_data['choices']:
            self.assertNotIn('is_correct', choice)

    def test_mentor_sees_correct_answers(self):
        q = QuizQuestion.objects.create(quiz=self.quiz, text='Q1', order=1)
        QuizChoice.objects.create(question=q, text='Correct', is_correct=True)
        self.client.force_authenticate(user=self.mentor)
        response = self.client.get(f'/api/quizzes/{self.quiz.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        question_data = response.data['questions'][0]
        for choice in question_data['choices']:
            self.assertIn('is_correct', choice)


class QuizAttemptViewPermissionsTests(APITestCase):
    def setUp(self):
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR')
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT')
        self.admin = User.objects.create_user(username='admin', password='pass1234', role='ADMIN', is_staff=True)
        self.course = Course.objects.create(
            title='Test Course', description='Desc', category='Programming', level='BEGINNER',
            language='English', price=0, mentor=self.mentor, is_published=True
        )
        self.module = Module.objects.create(course=self.course, title='Module 1', order=1)
        self.quiz = Quiz.objects.create(module=self.module, title='Quiz 1')
        self.attempt = QuizAttempt.objects.create(student=self.student, quiz=self.quiz, score=80.0, passed=True)

    def test_student_sees_own_attempts(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/quiz-attempts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_student_cannot_see_other_student_attempts(self):
        other = User.objects.create_user(username='other', password='pass1234', role='STUDENT')
        self.client.force_authenticate(user=other)
        response = self.client.get('/api/quiz-attempts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_mentor_sees_students_attempts_on_own_courses(self):
        self.client.force_authenticate(user=self.mentor)
        response = self.client.get('/api/quiz-attempts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_sees_all_attempts(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/quiz-attempts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
