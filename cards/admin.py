from django.contrib import admin

from .forms import StudentForm
from .models import Attendance, Cards, Course, ExamResult, Student, StudentGroup, Teacher


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentForm
    list_display = ('name', 'surname', 'phone', 'age', 'course', 'group', 'created_at')
    list_filter = ('course', 'group')
    search_fields = ('name', 'surname', 'phone')
    ordering = ('surname', 'name')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'specialty', 'phone')
    search_fields = ('name', 'surname', 'specialty', 'phone')
    ordering = ('surname', 'name')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'duration')
    search_fields = ('title',)
    ordering = ('title',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'group', 'date', 'status', 'updated_at')
    list_filter = ('course', 'group', 'date', 'status')
    search_fields = ('student__name', 'student__surname')
    ordering = ('-date', 'student__surname', 'student__name')


admin.site.register(Cards)
admin.site.register(StudentGroup)


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('name', 'student', 'group', 'subject', 'grade', 'date')
    list_filter = ('date', 'subject')
    search_fields = ('name', 'student__name', 'student__surname', 'subject')
