from rest_framework import serializers
from .models import College, Student, Event, Registration, Attendance, Feedback


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = ['id', 'name', 'code','location','tot_students']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'college', 'full_name', 'email', 'roll_no', 'college_code']


class EventSerializer(serializers.ModelSerializer):
    registrations_count = serializers.SerializerMethodField()
    attendance_count = serializers.SerializerMethodField()
    avg_feedback = serializers.SerializerMethodField()

    def get_registrations_count(self, obj):
        return obj.registrations.count()

    def get_attendance_count(self, obj):
        return obj.attendances.count()

    def get_avg_feedback(self, obj):
        feedbacks = obj.feedbacks.all()
        if feedbacks:
            return sum(f.rating for f in feedbacks) / len(feedbacks)
        return 0.0

    class Meta:
        model = Event
        fields = [
            'id', 'college', 'title', 'description', 'type', 'start_at', 'end_at', 'capacity',
            'registrations_count', 'attendance_count', 'avg_feedback'
        ]


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ['id', 'event', 'student', 'college_registered_count', 'created_at']


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'event', 'student', 'college', 'has_given_feedback', 'checked_in_at']


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'event', 'student', 'rating', 'comment', 'created_at']