from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from courses.models import Course, Module, Lesson, Quiz, QuizQuestion, QuizChoice, QuizAttempt
from enrollments.models import Enrollment

User = get_user_model()

class QuizPipelineTestCase(APITestCase):
    def setUp(self):
        # Create users
        self.mentor = User.objects.create_user(username='mentor_bob', password='password123', role='MENTOR')
        self.student = User.objects.create_user(username='student_alice', password='password123', role='STUDENT')
        
        # Create Course, Module, Lessons
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            category='Programming',
            level='BEGINNER',
            language='English',
            price=0.00,
            mentor=self.mentor,
            is_published=True
        )
        self.module = Module.objects.create(course=self.course, title='Module 1', order=1)
        self.lesson1 = Lesson.objects.create(module=self.module, title='Lesson 1', lesson_type='VIDEO', order=1)
        
        # Create Quiz
        self.quiz = Quiz.objects.create(module=self.module, title='Quiz 1', passing_score=60)
        
        # Create Quiz Questions
        self.q1 = QuizQuestion.objects.create(quiz=self.quiz, text='What is 2+2?', order=1)
        self.q2 = QuizQuestion.objects.create(quiz=self.quiz, text='What is Python?', order=2)
        
        # Create Choices
        self.q1_c1 = QuizChoice.objects.create(question=self.q1, text='3', is_correct=False)
        self.q1_c2 = QuizChoice.objects.create(question=self.q1, text='4', is_correct=True)
        
        self.q2_c1 = QuizChoice.objects.create(question=self.q2, text='A snake', is_correct=False)
        self.q2_c2 = QuizChoice.objects.create(question=self.q2, text='A programming language', is_correct=True)

    def test_single_correct_choice_enforcement(self):
        # Originally, q1_c2 (4) is correct
        self.assertTrue(self.q1_c2.is_correct)
        self.assertFalse(self.q1_c1.is_correct)
        
        # Change q1_c1 (3) to correct
        self.q1_c1.is_correct = True
        self.q1_c1.save()
        
        # Reload choices from DB
        self.q1_c1.refresh_from_db()
        self.q1_c2.refresh_from_db()
        
        # Now q1_c1 is correct, q1_c2 is automatically set to False
        self.assertTrue(self.q1_c1.is_correct)
        self.assertFalse(self.q1_c2.is_correct)

    def test_submit_quiz_attempt_success(self):
        # Enroll student first
        Enrollment.objects.create(student=self.student, course=self.course, status='ACTIVE')
        
        # Authenticate client
        self.client.force_authenticate(user=self.student)
        
        # Submit correct answers
        payload = {
            'answers': {
                str(self.q1.id): self.q1_c2.id,
                str(self.q2.id): self.q2_c2.id
            }
        }
        response = self.client.post(f'/api/quizzes/{self.quiz.id}/submit/', payload, format='json')
        self.assertEqual(response.status_code, 201) # 201 CREATED
        
        data = response.json()
        self.assertEqual(data['score'], 100.0)
        self.assertTrue(data['passed'])
        self.assertEqual(data['correct_answers'], 2)
        self.assertEqual(data['total_questions'], 2)
        
        # Check detailed review results
        q_results = data['question_results']
        self.assertEqual(len(q_results), 2)
        self.assertTrue(q_results[0]['is_correct'])
        self.assertEqual(q_results[0]['chosen_choice_text'], '4')
        self.assertEqual(q_results[0]['correct_choice_text'], '4')

    def test_submit_quiz_attempt_partial_fail(self):
        Enrollment.objects.create(student=self.student, course=self.course, status='ACTIVE')
        self.client.force_authenticate(user=self.student)
        
        # Submit one correct and one incorrect
        payload = {
            'answers': {
                str(self.q1.id): self.q1_c1.id, # Wrong (3)
                str(self.q2.id): self.q2_c2.id  # Correct (A programming language)
            }
        }
        response = self.client.post(f'/api/quizzes/{self.quiz.id}/submit/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        
        data = response.json()
        self.assertEqual(data['score'], 50.0)
        self.assertFalse(data['passed']) # 50% is below 60% passing score
        
        q_results = data['question_results']
        self.assertFalse(q_results[0]['is_correct'])
        self.assertEqual(q_results[0]['chosen_choice_text'], '3')
        self.assertEqual(q_results[0]['correct_choice_text'], '4')
        self.assertTrue(q_results[1]['is_correct'])

    def test_submit_quiz_attempt_empty_answers(self):
        Enrollment.objects.create(student=self.student, course=self.course, status='ACTIVE')
        self.client.force_authenticate(user=self.student)
        
        # Empty answers submission
        payload = {
            'answers': {}
        }
        response = self.client.post(f'/api/quizzes/{self.quiz.id}/submit/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        
        data = response.json()
        self.assertEqual(data['score'], 0.0)
        self.assertFalse(data['passed'])
        self.assertEqual(data['correct_answers'], 0)
