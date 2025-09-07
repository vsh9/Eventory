from datetime import timezone
from django.db import IntegrityError
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from event.serializer import (
    CollegeSerializer, StudentSerializer, EventSerializer,
    AttendanceSerializer, FeedbackSerializer, RegistrationSerializer,
    StudentRegistrationSerializer
)
from event.models import College, Student, Event, Registration, Attendance, Feedback
from event.reports import ReportsService
from rest_framework.decorators import api_view


class CollegeViewSet(viewsets.ModelViewSet):
    queryset = College.objects.all()
    serializer_class = CollegeSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_serializer_class(self):
        # Use StudentRegistrationSerializer only for the "register" action
        if self.action == 'register':
            return StudentRegistrationSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post'], url_path='register')
    def register(self, request, pk=None):
        event = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'event': event})
        if serializer.is_valid():
            registration = serializer.save()
            return Response(RegistrationSerializer(registration).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='attendance')
    def attendance(self, request, pk=None):
        event = self.get_object()
        student_id = request.data.get('student')
        # enforce that only registered students can attend
        if not Registration.objects.filter(event=event, student_id=student_id).exists():
            return Response({'detail': 'Student is not registered for this event.'}, status=400)
        try:
            student = Student.objects.get(id=student_id)
            att = Attendance.objects.create(event=event, student=student, college=student.college, checked_in_at=timezone.now())
            return Response(AttendanceSerializer(att).data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'detail': 'Attendance already marked for this student.'}, status=400)

    @action(detail=True, methods=['post'], url_path='feedback')
    def feedback(self, request, pk=None):
        event = self.get_object()
        data = {**request.data, 'event': event.id}
        ser = FeedbackSerializer(data=data)
        if ser.is_valid():
            try:
                feedback = ser.save()
                # Update Attendance has_given_feedback field
                Attendance.objects.filter(event=event, student_id=feedback.student.id).update(has_given_feedback=True)
                return Response(ser.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'detail': 'Feedback already submitted by this student.'}, status=400)
        return Response(ser.errors, status=400)


# ---- Report Endpoints ----
@api_view(['GET'])
def event_metrics(request, event_id: int):
    return Response(ReportsService.event_metrics(event_id))


@api_view(['GET'])
def event_popularity(request):
    college_id = request.query_params.get('college')
    event_type = request.query_params.get('type')
    data = ReportsService.event_popularity(college_id, event_type)
    return Response(data)


@api_view(['GET'])
def student_participation(request, student_id: int):
    return Response(ReportsService.student_participation(student_id))


@api_view(['GET'])
def top_students(request):
    limit = int(request.query_params.get('limit', 3))
    college_id = request.query_params.get('college')
    return Response(ReportsService.top_students(limit=limit, college_id=college_id))
