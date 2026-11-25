from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from .models import AccountPhoto, Attendance, Course, ExamResult, Student, StudentGroup, Teacher


class EducationDashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='teacher')

    def setUp(self):
        self.client.force_login(self.user)
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

    def test_attendance_can_be_saved_for_a_student(self):
        attendance_response = self.client.get(
            reverse('attendance'),
            {'course': self.course.pk, 'date': '2026-11-19'},
        )
        self.assertContains(attendance_response, 'Davomat')

        save_response = self.client.post(
            reverse('save_attendance'),
            {
                'course': self.course.pk,
                'date': '2026-11-19',
                'status_{}'.format(self.student.pk): Attendance.STATUS_ABSENT,
            },
        )
        self.assertEqual(save_response.status_code, 302)
        record = Attendance.objects.get(
            student=self.student,
            course=self.course,
            date='2026-11-19',
        )
        self.assertEqual(record.status, Attendance.STATUS_ABSENT)

    def test_dashboard_summarizes_current_month_attendance(self):
        Attendance.objects.create(
            student=self.student, course=self.course, date=timezone.localdate(),
            status=Attendance.STATUS_LATE,
        )
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.context['attendance_total'], 1)
        self.assertEqual(response.context['present_pct'], 100)
        self.assertEqual(response.context['absent_pct'], 0)

    def test_group_attendance_accepts_students_without_courses_and_isolates_scope(self):
        group = StudentGroup.objects.create(name='A1')
        student = Student.objects.create(name='Vali', surname='Karimov', age=17, group=group)
        attendance_date = '2026-11-19'
        params = {'scope': f'group:{group.pk}', 'date': attendance_date}
        response = self.client.get(reverse('attendance'), params)
        self.assertContains(response, 'Vali Karimov')
        self.assertNotContains(response, 'Ali Zokirov')
        self.assertContains(response, '>Keldi<')
        self.assertContains(response, '>Kelmadi<')
        self.assertNotContains(response, '>Kech qoldi<')
        self.client.post(reverse('save_attendance'), {**params, f'status_{student.pk}': Attendance.STATUS_LATE})
        self.assertFalse(Attendance.objects.exists())
        for status in (Attendance.STATUS_ABSENT, Attendance.STATUS_PRESENT):
            response = self.client.post(reverse('save_attendance'), {
                **params, f'status_{student.pk}': status,
                f'status_{self.student.pk}': Attendance.STATUS_PRESENT,
            }, follow=True)
            self.assertEqual(response.context['students'][0].attendance_status, status)
            record = Attendance.objects.get()
            self.assertEqual(record.student, student)
            self.assertEqual(record.group, group)
            self.assertIsNone(record.course)

    def test_exam_results_can_be_searched_by_name_and_student_id(self):
        result = ExamResult.objects.create(
            student=self.student, name='Yakuniy test', group='A1',
            subject='Ingliz tili', grade='A+', date=timezone.localdate(),
        )
        for query in ['Ali Zokirov', f'#{self.student.pk}']:
            with self.subTest(query=query):
                response = self.client.get(reverse('exam_list'), {'exam': query})
                self.assertEqual(list(response.context['exam_page']), [result])
                self.assertContains(response, 'Yakuniy test')
        response = self.client.get(reverse('dashboard'), {'exam': 'Matematika'})
        self.assertEqual(list(response.context['exam_page']), [])


class CrmAuthenticationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(username='teacher', password='test-password-837')

    def test_anonymous_requests_require_login(self):
        for route, args in [
            ('dashboard', []), ('student_list', []), ('student_detail', [1]),
            ('teacher_list', []), ('course_list', []), ('exam_list', []),
            ('attendance', []), ('save_attendance', []),
            ('group_list', []), ('group_detail', [1]), ('group_student_add', [1]),
        ]:
            with self.subTest(route=route):
                path = reverse(route, args=args)
                request = self.client.post if route == 'save_attendance' else self.client.get
                self.assertRedirects(request(path), f"{reverse('login')}?next={path}")

    def test_login_returns_to_requested_page_and_logout_ends_session(self):
        exams = reverse('exam_list')
        login = reverse('login')
        response = self.client.post(login, {'username': 'teacher', 'password': 'wrong'})
        self.assertContains(response, 'Login yoki parol')
        response = self.client.post(login, {
            'username': 'teacher', 'password': 'test-password-837', 'next': exams,
        })
        self.assertRedirects(response, exams)
        logout = reverse('logout')
        self.assertEqual(self.client.get(logout).status_code, 405)
        self.assertRedirects(self.client.post(logout), login)
        self.assertRedirects(self.client.get(exams), f'{login}?next={exams}')

    def test_password_change_checks_current_password_and_keeps_session(self):
        user = get_user_model().objects.get(username='teacher')
        self.client.force_login(user)
        path = reverse('password_change')
        fields = {'new_password1': 'updated-test-password-743', 'new_password2': 'updated-test-password-743'}
        self.assertContains(self.client.get(path), 'Joriy parol')
        self.assertEqual(self.client.post(path, {**fields, 'old_password': 'wrong'}).status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password('test-password-837'))
        response = self.client.post(path, {**fields, 'old_password': 'test-password-837'})
        self.assertRedirects(response, reverse('password_change_done'))
        user.refresh_from_db()
        self.assertTrue(user.check_password(fields['new_password1']))
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)

    def test_profile_updates_name_and_valid_photo_for_current_user(self):
        path = reverse('account_profile')
        photo_url = reverse('account_photo')
        self.assertRedirects(self.client.get(path), f"{reverse('login')}?next={path}")
        user = get_user_model().objects.get(username='teacher')
        self.client.force_login(user)
        invalid = SimpleUploadedFile('fake.png', b'<svg/>', content_type='image/png')
        fields = {'first_name': 'Ali', 'last_name': 'Karimov'}
        response = self.client.post(path, {**fields, 'photo': invalid})
        self.assertIn('photo', response.context['form'].errors)
        self.assertFalse(AccountPhoto.objects.exists())
        user.refresh_from_db()
        self.assertEqual(user.first_name, '')

        image = BytesIO()
        Image.new('RGB', (640, 320)).save(image, format='PNG')
        upload = SimpleUploadedFile('avatar.png', image.getvalue(), content_type='image/png')
        self.assertRedirects(self.client.post(path, {**fields, 'photo': upload}), path)
        self.assertContains(self.client.get(reverse('dashboard')), 'Ali Karimov')
        response = self.client.get(photo_url)
        self.assertEqual(response['Content-Type'], 'image/jpeg')
        with Image.open(BytesIO(response.content)) as stored:
            self.assertEqual(stored.size, (512, 256))
        self.assertRedirects(self.client.post(path, {**fields, 'first_name': 'Vali'}), path)
        self.assertEqual(self.client.get(photo_url).content, response.content)

        user.set_password('profile-test-password')
        user.save(update_fields=['password'])
        self.client.logout()
        self.assertRedirects(self.client.post(reverse('login'), {
            'username': user.username, 'password': 'profile-test-password',
        }), reverse('dashboard'))
        user.refresh_from_db()
        self.assertIsNotNone(user.last_login)
        profile = self.client.get(path)
        self.assertContains(profile, 'Vali Karimov')
        self.assertContains(profile, timezone.localtime(user.last_login).strftime('%d.%m.%Y, %H:%M'))
        self.assertEqual(self.client.get(photo_url).content, response.content)

        other_user = get_user_model().objects.create_user(username='another')
        self.client.force_login(other_user)
        self.assertEqual(self.client.get(photo_url).status_code, 404)


class RecordManagementTests(TestCase):
    def test_record_writes_require_permissions(self):
        self.client.force_login(get_user_model().objects.create_user(username='viewer'))
        for prefix in ('student', 'teacher'):
            self.assertEqual(self.client.post(reverse(f'{prefix}_add'), {'name': 'Ali'}).status_code, 403)

    def test_create_edit_and_delete_use_crm_pages(self):
        user = get_user_model().objects.create_superuser(username='manager', password='test-746-password')
        self.client.force_login(user)
        group = StudentGroup.objects.create(name='Matematika A1')
        for prefix, model, extra_fields in [
            ('student', Student, {'age': 17, 'group': group.pk}),
            ('teacher', Teacher, {'specialty': 'Matematika'}),
        ]:
            with self.subTest(prefix=prefix):
                edit_fields = {'name': 'Ali', 'surname': 'Karimov', 'phone': '+998901112233', **extra_fields}
                list_url = reverse(f'{prefix}_list')
                add_url = reverse(f'{prefix}_add')
                self.assertContains(self.client.get(list_url), add_url)
                self.assertRedirects(self.client.post(add_url, edit_fields), list_url)
                record = model.objects.get()
                edit_url = reverse(f'{prefix}_edit', args=[record.pk])
                self.assertContains(self.client.get(edit_url), 'Ali')
                edit_fields['name'] = 'Vali'
                self.assertRedirects(self.client.post(edit_url, edit_fields), list_url)
                record.refresh_from_db()
                self.assertEqual(record.name, 'Vali')
                delete_url = reverse(f'{prefix}_delete', args=[record.pk])
                self.assertContains(self.client.get(delete_url), 'Vali')
                self.assertTrue(model.objects.filter(pk=record.pk).exists())
                self.assertRedirects(self.client.post(delete_url), list_url)
                self.assertFalse(model.objects.filter(pk=record.pk).exists())

    def test_group_add_assigns_student_and_updates_group_counts(self):
        user = get_user_model().objects.create_superuser(username='manager', password='test-746-password')
        self.client.force_login(user)
        self.assertRedirects(self.client.post(reverse('group_add'), {'name': 'Matematika A1'}), reverse('group_list'))
        group = StudentGroup.objects.get(name='Matematika A1')
        other_group = StudentGroup.objects.create(name='Matematika A2')
        fields = {'name': 'Ali', 'surname': 'Karimov', 'phone': '123', 'age': 17}
        response = self.client.post(reverse('student_add'), fields)
        self.assertIn('group', response.context['form'].errors)
        self.assertFalse(Student.objects.exists())
        add_url = reverse('group_student_add', args=[group.pk])
        response = self.client.get(add_url)
        self.assertTrue(response.context['form'].fields['group'].disabled)
        self.assertEqual(response.context['form'].initial['group'], group.pk)
        detail_url = reverse('group_detail', args=[group.pk])
        self.assertRedirects(self.client.post(add_url, {**fields, 'group': other_group.pk}), detail_url)
        self.assertEqual(Student.objects.get().group, group)
        self.assertContains(self.client.get(detail_url), 'Ali Karimov')
        response = self.client.get(reverse('group_list'))
        self.assertContains(response, '1 nafar o‘quvchi')
        self.assertContains(response, '0 nafar o‘quvchi')
        self.assertContains(self.client.get(detail_url), '1 nafar o‘quvchi')
        self.assertEqual([(item.name, item.student_count) for item in response.context['groups']], [
            ('Matematika A1', 1), ('Matematika A2', 0),
        ])
