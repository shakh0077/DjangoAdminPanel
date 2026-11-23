from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import CrmPasswordChangeForm, StudentForm, StudentGroupForm, TeacherForm
from .models import Student, StudentGroup, Teacher
from .records import GroupStudentCreate, RecordCreate, RecordDelete, RecordUpdate

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('account/profile/', views.account_profile, name='account_profile'),
    path('account/photo/', views.account_photo, name='account_photo'),
    path('account/password/', auth_views.PasswordChangeView.as_view(
        template_name='password_change.html',
        form_class=CrmPasswordChangeForm,
        success_url=reverse_lazy('password_change_done'),
    ), name='password_change'),
    path('account/password/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='password_change_done.html',
    ), name='password_change_done'),
    path('', views.dashboard, name='dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/add/', RecordCreate.as_view(
        model=StudentGroup, form_class=StudentGroupForm, section='group_list', heading='Guruh qo‘shish',
    ), name='group_add'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:pk>/edit/', RecordUpdate.as_view(
        model=StudentGroup, form_class=StudentGroupForm, section='group_list', heading='Guruh nomini tahrirlash',
    ), name='group_edit'),
    path('groups/<int:group_id>/students/add/', GroupStudentCreate.as_view(
        model=Student, form_class=StudentForm, heading='Guruhga o‘quvchi qo‘shish',
    ), name='group_student_add'),
    path('courses/', views.course_list, name='course_list'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('exams/', views.exam_list, name='exam_list'),
    path('attendance/', views.attendance, name='attendance'),
    path('attendance/save/', views.save_attendance, name='save_attendance'),
]

for prefix, model, form, label in (
    ('student', Student, StudentForm, 'O‘quvchi'),
    ('teacher', Teacher, TeacherForm, 'O‘qituvchi'),
):
    options = {'model': model, 'section': f'{prefix}_list'}
    urlpatterns += [
        path(f'{prefix}s/add/', RecordCreate.as_view(
            **options, form_class=form, heading=f'{label} qo‘shish',
        ), name=f'{prefix}_add'),
        path(f'{prefix}s/<int:pk>/edit/', RecordUpdate.as_view(
            **options, form_class=form, heading=f'{label} ma’lumotlarini tahrirlash',
        ), name=f'{prefix}_edit'),
        path(f'{prefix}s/<int:pk>/delete/', RecordDelete.as_view(
            **options, heading=f'{label}ni o‘chirish',
        ), name=f'{prefix}_delete'),
    ]
