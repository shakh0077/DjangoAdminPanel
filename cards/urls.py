from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('courses/', views.course_list, name='course_list'),
    path('teachers/', views.teacher_list, name='teacher_list'),
]