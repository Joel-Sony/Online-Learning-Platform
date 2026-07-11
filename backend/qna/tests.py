from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from courses.models import Course, Module
from enrollments.models import Enrollment
from qna.models import Question, Reply

User = get_user_model()


class QnABaseTestCase(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student', password='pass1234', role='STUDENT')
        self.mentor = User.objects.create_user(username='mentor', password='pass1234', role='MENTOR')
        self.admin = User.objects.create_user(username='admin', password='pass1234', role='ADMIN', is_staff=True)
        self.course = Course.objects.create(
            title='Test Course', description='Desc', category='Programming', level='BEGINNER',
            language='English', price=0, mentor=self.mentor, is_published=True
        )
        self.question_data = {'title': 'How to code?', 'body': 'I need help with Python.'}


class QuestionTests(QnABaseTestCase):
    def setUp(self):
        super().setUp()
        Enrollment.objects.create(student=self.student, course=self.course)

    def test_enrolled_student_can_create_question(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(f'/api/courses/{self.course.id}/qna/questions/', self.question_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 1)

    def test_mentor_can_create_question(self):
        self.client.force_authenticate(user=self.mentor)
        response = self.client.post(f'/api/courses/{self.course.id}/qna/questions/', self.question_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unenrolled_student_cannot_create_question(self):
        other_student = User.objects.create_user(username='other', password='pass1234', role='STUDENT')
        self.client.force_authenticate(user=other_student)
        response = self.client.post(f'/api/courses/{self.course.id}/qna/questions/', self.question_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_question(self):
        response = self.client.post(f'/api/courses/{self.course.id}/qna/questions/', self.question_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_questions_for_course(self):
        Question.objects.create(course=self.course, author=self.student, title='Q1', body='Body1')
        Question.objects.create(course=self.course, author=self.student, title='Q2', body='Body2')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/courses/{self.course.id}/qna/questions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_question_not_in_other_courses(self):
        other_course = Course.objects.create(
            title='Other', description='Desc', category='Design', level='INTERMEDIATE',
            language='English', price=0, mentor=self.mentor, is_published=True
        )
        Question.objects.create(course=self.course, author=self.student, title='Q1', body='Body1')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/courses/{other_course.id}/qna/questions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_author_can_update_own_question(self):
        q = Question.objects.create(course=self.course, author=self.student, title='Q1', body='Body1')
        self.client.force_authenticate(user=self.student)
        response = self.client.patch(f'/api/courses/{self.course.id}/qna/questions/{q.id}/', {'title': 'Updated'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        q.refresh_from_db()
        self.assertEqual(q.title, 'Updated')

    def test_other_student_cannot_update_question(self):
        q = Question.objects.create(course=self.course, author=self.student, title='Q1', body='Body1')
        other = User.objects.create_user(username='other', password='pass1234', role='STUDENT')
        Enrollment.objects.create(student=other, course=self.course)
        self.client.force_authenticate(user=other)
        response = self.client.patch(f'/api/courses/{self.course.id}/qna/questions/{q.id}/', {'title': 'Hacked'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_delete_own_question(self):
        q = Question.objects.create(course=self.course, author=self.student, title='Q1', body='Body1')
        self.client.force_authenticate(user=self.student)
        response = self.client.delete(f'/api/courses/{self.course.id}/qna/questions/{q.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_mentor_can_delete_question(self):
        q = Question.objects.create(course=self.course, author=self.student, title='Q1', body='Body1')
        self.client.force_authenticate(user=self.mentor)
        response = self.client.delete(f'/api/courses/{self.course.id}/qna/questions/{q.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_delete_question(self):
        q = Question.objects.create(course=self.course, author=self.student, title='Q1', body='Body1')
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/courses/{self.course.id}/qna/questions/{q.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class PinQuestionTests(QnABaseTestCase):
    def setUp(self):
        super().setUp()
        Enrollment.objects.create(student=self.student, course=self.course)
        self.question = Question.objects.create(course=self.course, author=self.student, title='Q1', body='Body1')

    def test_mentor_can_pin_question(self):
        self.client.force_authenticate(user=self.mentor)
        response = self.client.post(f'/api/courses/{self.course.id}/qna/questions/{self.question.id}/pin/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_pinned'])

    def test_admin_can_pin_question(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/courses/{self.course.id}/qna/questions/{self.question.id}/pin/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_pinned'])

    def test_student_cannot_pin_question(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(f'/api/courses/{self.course.id}/qna/questions/{self.question.id}/pin/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pin_toggle(self):
        self.client.force_authenticate(user=self.mentor)
        self.client.post(f'/api/courses/{self.course.id}/qna/questions/{self.question.id}/pin/')
        self.question.refresh_from_db()
        self.assertTrue(self.question.is_pinned)
        response = self.client.post(f'/api/courses/{self.course.id}/qna/questions/{self.question.id}/pin/')
        self.assertFalse(response.data['is_pinned'])

    def test_pinned_questions_appear_first(self):
        q2 = Question.objects.create(course=self.course, author=self.student, title='Q2', body='Body2')
        q2.is_pinned = True
        q2.save()
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/courses/{self.course.id}/qna/questions/')
        self.assertEqual(response.data[0]['id'], q2.id)


class ReplyTests(QnABaseTestCase):
    def setUp(self):
        super().setUp()
        Enrollment.objects.create(student=self.student, course=self.course)
        self.question = Question.objects.create(course=self.course, author=self.student, title='Q1', body='Body1')

    def test_enrolled_student_can_create_reply(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            f'/api/courses/{self.course.id}/qna/questions/{self.question.id}/replies/',
            {'body': 'Here is an answer'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reply.objects.count(), 1)

    def test_mentor_reply_marked_as_mentor_response(self):
        self.client.force_authenticate(user=self.mentor)
        response = self.client.post(
            f'/api/courses/{self.course.id}/qna/questions/{self.question.id}/replies/',
            {'body': 'Mentor answer'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_mentor_response'])

    def test_student_reply_not_mentor_response(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            f'/api/courses/{self.course.id}/qna/questions/{self.question.id}/replies/',
            {'body': 'Student answer'}, format='json'
        )
        self.assertFalse(response.data['is_mentor_response'])

    def test_list_replies_for_question(self):
        Reply.objects.create(question=self.question, author=self.student, body='Reply 1')
        Reply.objects.create(question=self.question, author=self.student, body='Reply 2')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/courses/{self.course.id}/qna/questions/{self.question.id}/replies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_reply_with_parent(self):
        parent = Reply.objects.create(question=self.question, author=self.student, body='Parent')
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            f'/api/courses/{self.course.id}/qna/questions/{self.question.id}/replies/',
            {'body': 'Child reply', 'parent': parent.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['parent'], parent.id)

    def test_create_reply_with_invalid_parent(self):
        other_q = Question.objects.create(course=self.course, author=self.student, title='Q2', body='Body2')
        parent = Reply.objects.create(question=other_q, author=self.student, body='Parent')
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            f'/api/courses/{self.course.id}/qna/questions/{self.question.id}/replies/',
            {'body': 'Child', 'parent': parent.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nested_threading_not_allowed(self):
        parent = Reply.objects.create(question=self.question, author=self.student, body='Parent')
        child = Reply.objects.create(question=self.question, author=self.student, body='Child', parent=parent)
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            f'/api/courses/{self.course.id}/qna/questions/{self.question.id}/replies/',
            {'body': 'Grandchild', 'parent': child.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_author_can_delete_own_reply(self):
        reply = Reply.objects.create(question=self.question, author=self.student, body='Reply')
        self.client.force_authenticate(user=self.student)
        response = self.client.delete(
            f'/api/courses/{self.course.id}/qna/questions/{self.question.id}/replies/{reply.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_mentor_can_delete_reply(self):
        reply = Reply.objects.create(question=self.question, author=self.student, body='Reply')
        self.client.force_authenticate(user=self.mentor)
        response = self.client.delete(
            f'/api/courses/{self.course.id}/qna/questions/{self.question.id}/replies/{reply.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_student_cannot_delete_reply(self):
        reply = Reply.objects.create(question=self.question, author=self.student, body='Reply')
        other = User.objects.create_user(username='other', password='pass1234', role='STUDENT')
        Enrollment.objects.create(student=other, course=self.course)
        self.client.force_authenticate(user=other)
        response = self.client.delete(
            f'/api/courses/{self.course.id}/qna/questions/{self.question.id}/replies/{reply.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class QnAFlaggingTests(QnABaseTestCase):
    def setUp(self):
        super().setUp()
        Enrollment.objects.create(student=self.student, course=self.course)
        self.question = Question.objects.create(course=self.course, author=self.student, title='Q1', body='Body1', is_flagged=True)
        self.reply = Reply.objects.create(question=self.question, author=self.student, body='Bad reply', is_flagged=True)

    def test_admin_can_view_flagged_qna(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/admin/qna/flagged/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('questions', response.data)
        self.assertIn('replies', response.data)
        self.assertEqual(len(response.data['questions']), 1)
        self.assertEqual(len(response.data['replies']), 1)

    def test_admin_can_delete_flagged_question(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/admin/qna/{self.question.id}/delete_question/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Question.objects.count(), 0)

    def test_admin_can_delete_flagged_reply(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/admin/qna/{self.reply.id}/delete_reply/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Reply.objects.count(), 0)

    def test_non_admin_cannot_view_flagged_qna(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/admin/qna/flagged/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
