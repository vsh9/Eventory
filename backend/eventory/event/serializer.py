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
        fields = ['id', 'event', 'student', 'college', 'has_given_feedback', 'checked_in_at', 'is_present']


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'event', 'student', 'rating', 'comment', 'created_at']


class StudentRegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    collegeid = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    studentid = serializers.CharField(max_length=64)
    event_id = serializers.IntegerField()

    def create(self, validated_data):
        from .models import Student, College, Registration
        name = validated_data['name']
        collegeid = validated_data['collegeid']
        email = validated_data['email']
        studentid = validated_data['studentid']
        event_id = validated_data['event_id']

        try:
            college = College.objects.get(code=collegeid)
        except College.DoesNotExist:
            raise serializers.ValidationError({'collegeid': 'Invalid college code.'})

        student, created = Student.objects.get_or_create(
            email=email,
            college=college,
            defaults={'full_name': name, 'roll_no': studentid}
        )

        if not created:
            # Update details if student exists
            student.full_name = name
            student.roll_no = studentid
            student.save()

        event = Event.objects.get(id=event_id)

        # Check if already registered
        if Registration.objects.filter(event=event, student=student).exists():
            raise serializers.ValidationError({'detail': 'Student already registered for this event.'})

        # Check capacity
        if event.registration_count >= event.capacity:
            raise serializers.ValidationError({'detail': 'Event is at full capacity.'})

        registration = Registration.objects.create(event=event, student=student)

        # Update counts
        college_count = Registration.objects.filter(event=event, student__college=college).count()
        registration.college_registered_count = college_count
        registration.save()

        event.registration_count += 1
        event.save()

        return registration
