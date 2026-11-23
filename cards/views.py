from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .forms import AccountProfileForm
from .models import AccountPhoto, Attendance, Course, ExamResult, Student, StudentGroup, Teacher


@login_required
def account_profile(request):
    if request.method == 'POST':
        form = AccountProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.save(update_fields=('first_name', 'last_name'))
                if form.cleaned_data['photo']:
                    AccountPhoto.objects.update_or_create(
                        user=user, defaults={'image': form.cleaned_data['photo']},
                    )
            messages.success(request, 'Profil saqlandi.')
            return redirect('account_profile')
    else:
        form = AccountProfileForm(instance=request.user)
    return render(request, 'account_profile.html', {'form': form})


@never_cache
@login_required
def account_photo(request):
    photo = get_object_or_404(AccountPhoto, user=request.user)
    return HttpResponse(bytes(photo.image), content_type='image/jpeg')


def exam_results(request):
    query = request.GET.get('exam', '').strip()
    results = ExamResult.objects.select_related('student')
    for term in query.split():
        match = (Q(name__icontains=term) | Q(subject__icontains=term)
                 | Q(group__icontains=term) | Q(student__name__icontains=term)
                 | Q(student__surname__icontains=term))
        student_id = term.removeprefix('#')
        if student_id.isascii() and student_id.isdecimal() and len(student_id) <= 18:
            match |= Q(student_id=int(student_id))
        results = results.filter(match)
    return {
        'exam_query': query,
        'exam_page': Paginator(results, 8).get_page(request.GET.get('page')),
    }


@login_required
def dashboard(request):
    featured_student = Student.objects.select_related('course').order_by('-created_at', '-pk').first()
    today = timezone.localdate()
    records = Attendance.objects.filter(date__gte=today.replace(day=1), date__lte=today)
    counts = records.aggregate(
        total=Count('pk'),
        present=Count('pk', filter=Q(status__in=[
            Attendance.STATUS_PRESENT, Attendance.STATUS_LATE,
        ])),
        absent=Count('pk', filter=Q(status=Attendance.STATUS_ABSENT)),
    )
    total = counts['total']
    present = round(counts['present'] * 100 / total) if total else 0
    absent_end = round((counts['present'] + counts['absent']) * 100 / total) if total else 0
    return render(request, 'index.html', {
        **exam_results(request),
        'student_count': Student.objects.count(),
        'teacher_count': Teacher.objects.count(),
        'course_count': Course.objects.count(),
        'featured_student': featured_student,
        'attendance_total': total,
        'present_pct': present,
        'absent_pct': absent_end - present,
        'excused_pct': 100 - absent_end if total else 0,
        'absent_end': absent_end,
    })


@login_required
def exam_list(request):
    return render(request, 'exams.html', exam_results(request))


@login_required
def group_list(request):
    return render(request, 'groups.html', {
        'groups': StudentGroup.objects.annotate(student_count=Count('students')),
        'ungrouped_count': Student.objects.filter(group__isnull=True).count(),
    })


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(StudentGroup, pk=group_id)
    students = group.students.select_related('course', 'group').order_by('surname', 'name', 'pk')
    return render(request, 'group_detail.html', {'group': group, 'students': students})


@login_required
def student_list(request):
    students = Student.objects.select_related('course', 'group').order_by('surname', 'name')
    course_id = request.GET.get('course')
    if course_id and course_id.isascii() and course_id.isdecimal() and len(course_id) <= 18:
        students = students.filter(course_id=course_id)
    group_id = request.GET.get('group', '')
    if group_id == 'none':
        students = students.filter(group__isnull=True)
    elif group_id.isascii() and group_id.isdecimal() and len(group_id) <= 18:
        students = students.filter(group_id=group_id)
    query = request.GET.get('q', '').strip()
    for term in query.split():
        students = students.filter(Q(name__icontains=term) | Q(surname__icontains=term)
                                   | Q(phone__icontains=term))

    return render(request, 'students.html', {
        'students': students,
        'courses': Course.objects.order_by('title'),
        'selected_course': course_id or '',
        'student_count': Student.objects.count(),
        'student_query': query,
        'groups': StudentGroup.objects.all(),
        'selected_group': group_id,
    })


@login_required
def student_detail(request, student_id):
    student = get_object_or_404(
        Student.objects.select_related('course', 'group'),
        pk=student_id,
    )
    return render(request, 'student_detail.html', {'student': student})


@login_required
def course_list(request):
    courses = Course.objects.order_by('title')
    return render(request, 'courses.html', {'courses': courses})


@login_required
def teacher_list(request):
    teachers = Teacher.objects.order_by('surname', 'name')
    return render(request, 'teachers.html', {'teachers': teachers})


def attendance_scope(params):
    scope = params.get('scope', '')
    if scope:
        kind, _, target_id = scope.partition(':')
    elif params.get('group'):
        kind, target_id = 'group', params['group']
    else:
        kind, target_id = 'course', params.get('course', '')

    if not target_id:
        return kind, None
    if kind not in ('course', 'group') or not (
        target_id.isascii() and target_id.isdecimal() and len(target_id) <= 18
    ):
        raise Http404
    model = StudentGroup if kind == 'group' else Course
    return kind, get_object_or_404(model, pk=target_id)


def selected_attendance_date(value):
    try:
        return date.fromisoformat(value) if value else timezone.localdate()
    except ValueError:
        return timezone.localdate()


def attendance_status_choices(kind):
    if kind == 'group':
        return Attendance.STATUS_CHOICES[:2]
    return Attendance.STATUS_CHOICES


@login_required
def attendance(request):
    kind, target = attendance_scope(request.GET)
    attendance_date = selected_attendance_date(request.GET.get('date'))
    students = Student.objects.none()

    if target:
        students = Student.objects.filter(**{kind: target}).order_by('surname', 'name')
        attendance_records = dict(Attendance.objects.filter(
            date=attendance_date, **{kind: target},
        ).values_list('student_id', 'status'))
        for student in students:
            student.attendance_status = attendance_records.get(student.pk, Attendance.STATUS_PRESENT)

    return render(request, 'attendance.html', {
        'courses': Course.objects.order_by('title'),
        'groups': StudentGroup.objects.all(),
        'kind': kind,
        'target': target,
        'selected_date': attendance_date,
        'students': students,
        'status_choices': attendance_status_choices(kind),
    })


@login_required
@require_POST
@transaction.atomic
def save_attendance(request):
    kind, target = attendance_scope(request.POST)
    if target is None:
        raise Http404
    attendance_date = selected_attendance_date(request.POST.get('date'))
    target_filter = {kind: target}
    valid_statuses = dict(attendance_status_choices(kind))
    for student in Student.objects.filter(**target_filter):
        status = request.POST.get(f'status_{student.pk}')
        if status in valid_statuses:
            Attendance.objects.update_or_create(
                student=student, date=attendance_date, **target_filter,
                defaults={'status': status},
            )

    return redirect(
        f"{reverse('attendance')}?{kind}={target.pk}&date={attendance_date.isoformat()}"
    )
