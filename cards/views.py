from django.shortcuts import get_object_or_404, render

from .models import Course, Student, Teacher


def dashboard(request):
    recent_students = Student.objects.select_related('course').order_by('-created_at')[:5]
    return render(request, 'index.html', {
        'student_count': Student.objects.count(),
        'teacher_count': Teacher.objects.count(),
        'course_count': Course.objects.count(),
        'recent_students': recent_students,
    })


def student_list(request):
    students = Student.objects.select_related('course').order_by('surname', 'name')
    course_id = request.GET.get('course')
    if course_id:
        students = students.filter(course_id=course_id)

    return render(request, 'students.html', {
        'students': students,
        'courses': Course.objects.order_by('title'),
        'selected_course': course_id or '',
        'student_count': Student.objects.count(),
    })


def student_detail(request, student_id):
    student = get_object_or_404(
        Student.objects.select_related('course'),
        pk=student_id,
    )
    return render(request, 'student_detail.html', {'student': student})


def course_list(request):
    courses = Course.objects.order_by('title')
    return render(request, 'courses.html', {'courses': courses})


def teacher_list(request):
    teachers = Teacher.objects.order_by('surname', 'name')
    return render(request, 'teachers.html', {'teachers': teachers})
