from django.db import models

class College(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.SlugField(max_length=50, unique=True)
    location = models.CharField(max_length=255, blank=True)
    tot_students = models.PositiveIntegerField(default=0)


    def __str__(self):
        return self.name


class Student(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='students')
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    roll_no = models.CharField(max_length=64)


    class Meta:
        unique_together = ('college', 'email')


    def __str__(self):
        return f"{self.full_name} ({self.college.code})"

    @property
    def college_code(self):
        return self.college.code


class Event(models.Model):
    class EventType(models.TextChoices):
        WORKSHOP = 'WORKSHOP', 'Workshop'
        SEMINAR = 'SEMINAR', 'Seminar'
        HACKATHON = 'HACKATHON', 'Hackathon'
        FEST = 'FEST', 'Fest'
        TECHTALK = 'TECHTALK', 'Tech Talk'

    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=16, choices=EventType.choices)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=100)
    registration_count = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['college', 'type']),
            models.Index(fields=['start_at']),
        ]
        unique_together = ('college', 'title', 'start_at')

    def __str__(self):
        return f"{self.title} ({self.college.code})"

class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='registrations')
    college_registered_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'student')
        indexes = [models.Index(fields=['event']), models.Index(fields=['student'])]

class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='attendances')
    has_given_feedback = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(auto_now_add=True)
    is_present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'student')
        indexes = [models.Index(fields=['event']), models.Index(fields=['student'])]

class Feedback(models.Model):
    from django.core.validators import MinValueValidator, MaxValueValidator

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='feedbacks')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'student')
        indexes = [models.Index(fields=['event'])]
