from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import IntegrityError
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from event.serializer import (
    CollegeSerializer, StudentSerializer, EventSerializer,
    AttendanceSerializer, FeedbackSerializer, RegistrationSerializer,
    StudentRegistrationSerializer, UserRegistrationSerializer
)
from event.models import College, Student, Event, Registration, Attendance, Feedback
from event.permissions import IsAdminOrReadOnly, IsAdmin, IsStudent, IsAuthenticated



class CollegeViewSet(viewsets.ModelViewSet):
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    @action(detail=True, methods=['get'], url_path='registered_events')
    def registered_events(self, request, pk=None):
        student = self.get_object()
        registrations = Registration.objects.filter(student=student).select_related('event')
        events_data = []
        for reg in registrations:
            event = reg.event
            events_data.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'type': event.type,
                'start_at': event.start_at,
                'end_at': event.end_at,
                'college': event.college.name,
                'has_given_feedback': Attendance.objects.filter(event=event, student=student, has_given_feedback=True).exists()
            })
        return Response(events_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='registered')
    def registered(self, request):
        students = Student.objects.filter(registrations__isnull=False).distinct().select_related('college')
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_permissions(self):
        """Override to set different permissions for different actions"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only Admins can create, update, or delete events
            self.permission_classes = [IsAuthenticated, IsAdmin]
        elif self.action in ['register', 'attendance', 'feedback']:
            # Students can register, check-in, and provide feedback
            self.permission_classes = [IsAuthenticated, IsStudent]
        else:
            # Read operations (list, retrieve) are allowed for all authenticated users
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        # Use StudentRegistrationSerializer only for the "register" action
        if self.action == 'register':
            return StudentRegistrationSerializer
        elif self.action == 'attendance':
            return AttendanceSerializer
        elif self.action == 'feedback':
            return FeedbackSerializer
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
    def attendance(self, request, pk=None):  # sourcery skip: low-code-quality
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
            is_present = is_present if isinstance(is_present, bool) else str(is_present).lower() in {'true', '1', 'yes', 'on'}
            has_given_feedback = has_given_feedback if isinstance(has_given_feedback, bool) else str(has_given_feedback).lower() in {'true', '1', 'yes', 'on'}

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

    @action(detail=True, methods=['get'], url_path='attendance')
    def attendance_list(self, request, pk=None):
        event = self.get_object()
        attendances = Attendance.objects.filter(event=event).select_related('student', 'college')
        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='feedback')
    def feedback(self, request, pk=None):
        event = self.get_object()
        data = request.data.copy()
        data['event'] = event.id
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


class FeedbackViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Feedback.objects.select_related('event', 'student')
        event_id = self.request.query_params.get('event')
        student_id = self.request.query_params.get('student')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        return queryset


# User Registration and Authentication Views

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = UserRegistrationSerializer()
        return Response(serializer.data)

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect('/api/auth/login/')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Return empty serializer fields for browsable API form
        return Response({"username": "", "password": ""})

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/api/')
        else:
            return Response(
                {"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(
            {"detail": "Logout successful."}, status=status.HTTP_200_OK
        )
