from django.urls import path

from .views import event_popularity, student_participation, top_students

urlpatterns = [
    path('event-popularity/', event_popularity, name='event-popularity'),
    path('student-participation/<int:student_id>/', student_participation, name='student-participation'),
    path('top-students/', top_students, name='top-students'),
]
