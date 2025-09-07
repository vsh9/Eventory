
from django.utils import timezone
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
        elif self.action == 'attendance':
            return AttendanceSerializer
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
        students = request.data.get('students')

        if students and isinstance(students, list):
            response_data = []
            for student_data in students:
                student_id = student_data.get('student_id')
                is_present = student_data.get('is_present', False)
                if not Registration.objects.filter(event=event, student_id=student_id).exists():
                    response_data.append({'student_id': student_id, 'status': 'not registered'})
                    continue
                try:
                    student = Student.objects.get(id=student_id)
                    attendance, created = Attendance.objects.get_or_create(
                        event=event,
                        student=student,
                        defaults={'college': student.college, 'checked_in_at': timezone.now(), 'is_present': is_present}
                    )
                    if not created:
                        attendance.is_present = is_present
                        attendance.checked_in_at = timezone.now()
                        attendance.save()
                    response_data.append({'student_id': student_id, 'status': 'marked', 'is_present': is_present})
                except Exception as e:
                    response_data.append({'student_id': student_id, 'status': 'error', 'error': str(e)})

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # Process single attendance record for browsable API form
            student_id = request.data.get('student')
            is_present = request.data.get('is_present', False)
            has_given_feedback = request.data.get('has_given_feedback', False)

            # Convert string booleans to actual booleans (shorter)
            is_present = is_present if isinstance(is_present, bool) else str(is_present).lower() in ['true', '1', 'yes', 'on']
            has_given_feedback = has_given_feedback if isinstance(has_given_feedback, bool) else str(has_given_feedback).lower() in ['true', '1', 'yes', 'on']

            if not student_id:
                return Response({'detail': 'Student ID is required.'}, status=400)
            if not Registration.objects.filter(event=event, student_id=student_id).exists():
                return Response({'detail': 'Student not registered for this event.'}, status=400)
            try:
                student = Student.objects.get(id=student_id)
                attendance, created = Attendance.objects.get_or_create(
                    event=event,
                    student=student,
                    defaults={'college': student.college, 'checked_in_at': timezone.now(), 'is_present': is_present, 'has_given_feedback': has_given_feedback}
                )
                if not created:
                    attendance.is_present = is_present
                    attendance.has_given_feedback = has_given_feedback
                    attendance.checked_in_at = timezone.now()
                    attendance.save()
                serializer = AttendanceSerializer(attendance)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'detail': str(e)}, status=400)

    @action(detail=True, methods=['get'], url_path='registered_students')
    def registered_students(self, request, pk=None):
        event = self.get_object()
        registrations = Registration.objects.filter(event=event).select_related('student')
        students_data = [{'student_id': reg.student.id, 'full_name': reg.student.full_name, 'email': reg.student.email} for reg in registrations]
        return Response(students_data, status=status.HTTP_200_OK)

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
