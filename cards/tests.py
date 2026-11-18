from django.test import TestCase
from django.urls import reverse

from .models import Course, Student, Teacher


class EducationDashboardTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title='Ingliz tili',
            description='Boshlangich kurs',
            price=500000,
            duration='3 oy',
        )
        self.student = Student.objects.create(
            name='Ali',
            surname='Zokirov',
            phone='+998901234567',
            age=17,
            course=self.course,
        )
        Teacher.objects.create(
            name='Dilnoza',
            surname='Karimova',
            specialty='Ingliz tili',
            phone='+998909876543',
        )

    def test_dashboard_shows_counts_and_latest_students(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ali Zokirov')
        self.assertContains(response, 'Ingliz tili')
        self.assertEqual(response.context['student_count'], 1)
        self.assertEqual(response.context['teacher_count'], 1)
        self.assertEqual(response.context['course_count'], 1)

    def test_students_are_sorted_and_can_be_filtered_by_course(self):
        Student.objects.create(
            name='Zara',
            surname='Abdullayeva',
            phone='+998911111111',
            age=16,
            course=None,
        )
        response = self.client.get(reverse('student_list'))
        self.assertEqual(
            list(response.context['students'].values_list('surname', flat=True)),
            ['Abdullayeva', 'Zokirov'],
        )

        filtered_response = self.client.get(
            reverse('student_list'),
            {'course': self.course.pk},
        )
        self.assertEqual(list(filtered_response.context['students']), [self.student])

    def test_student_profile_and_missing_student(self):
        response = self.client.get(
            reverse('student_detail', args=[self.student.pk])
        )
        self.assertContains(response, 'Ali')
        self.assertContains(response, '17 yosh')

        missing_response = self.client.get(
            reverse('student_detail', args=[9999])
        )
        self.assertEqual(missing_response.status_code, 404)

    def test_course_and_teacher_pages_render(self):
        self.assertContains(self.client.get(reverse('course_list')), '500000')
        self.assertContains(
            self.client.get(reverse('teacher_list')),
            'Dilnoza Karimova',
        )
