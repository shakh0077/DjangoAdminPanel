from django.contrib import admin

from .models import Cards, Course, Student, Teacher


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'phone', 'age', 'course', 'created_at')
    list_filter = ('course',)
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


admin.site.register(Cards)
