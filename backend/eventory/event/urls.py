from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ( 
                    CollegeViewSet, StudentViewSet, EventViewSet,
                    event_metrics, event_popularity, student_participation, top_students)


router = DefaultRouter()
router.register(r'colleges', CollegeViewSet, basename='college')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'events', EventViewSet, basename='event')


urlpatterns = [
path('', include(router.urls)),
# Reports
path('reports/event-metrics/<int:event_id>/', event_metrics, name='event-metrics'),
path('reports/event-popularity/', event_popularity, name='event-popularity'),
path('reports/student-participation/<int:student_id>/', student_participation, name='student-participation'),
path('reports/top-students/', top_students, name='top-students'),
]