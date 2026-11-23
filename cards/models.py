from django.conf import settings
from django.db import models


class AccountPhoto(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='account_photo',
    )
    image = models.BinaryField()

class Cards(models.Model):
    img = models.TextField(max_length=1000)
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    tavsif = models.TextField(max_length=200)

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.IntegerField()
    duration = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    specialty = models.CharField(max_length=150)
    phone = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.name} {self.surname}'


class StudentGroup(models.Model):
    name = models.CharField('Guruh nomi', max_length=100, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    age = models.IntegerField()
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(
        StudentGroup, on_delete=models.PROTECT, null=True, blank=True,
        related_name='students',
    )

    def __str__(self):
        return f'{self.name} {self.surname}'


class Attendance(models.Model):
    STATUS_PRESENT = 'present'
    STATUS_ABSENT = 'absent'
    STATUS_LATE = 'late'
    STATUS_EXCUSED = 'excused'
    STATUS_CHOICES = (
        (STATUS_PRESENT, 'Keldi'),
        (STATUS_ABSENT, 'Kelmadi'),
        (STATUS_LATE, 'Kech qoldi'),
        (STATUS_EXCUSED, 'Sababli'),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='attendance_records',
    )
    group = models.ForeignKey(
        StudentGroup, on_delete=models.PROTECT, null=True, blank=True,
        related_name='attendance_records',
    )
    date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PRESENT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('student', 'course', 'date'),
                name='unique_student_course_attendance',
            ),
            models.UniqueConstraint(
                fields=('student', 'group', 'date'),
                name='unique_student_group_attendance',
            ),
            models.CheckConstraint(
                condition=(models.Q(course__isnull=False, group__isnull=True)
                           | models.Q(course__isnull=True, group__isnull=False)),
                name='attendance_has_one_scope',
            ),
        ]
        ordering = ('date', 'student__surname', 'student__name')

    def __str__(self):
        return f'{self.student} - {self.date} - {self.get_status_display()}'


class ExamResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_results')
    name = models.CharField('Imtihon nomi', max_length=100)
    group = models.CharField('Guruh', max_length=100)
    subject = models.CharField('Fan', max_length=100)
    grade = models.CharField('Baho', max_length=16)
    date = models.DateField('Sana')

    class Meta:
        ordering = ('-date', '-pk')

    def __str__(self):
        return f'{self.name} / {self.student}'
