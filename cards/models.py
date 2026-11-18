from django.db import models

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

    def __str__(self):
        return f'{self.name} {self.surname}'
