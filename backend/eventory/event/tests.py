from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import College, Student, Event, Registration

class EventRegistrationTests(APITestCase):
    def setUp(self):
        self.college = College.objects.create(name="Test College", code="TC01")
        self.student = Student.objects.create(college=self.college, full_name="John Doe", email="john@example.com", roll_no="123")
        self.event = Event.objects.create(
            college=self.college,
            title="Test Event",
            description="Test Description",
            type="WORKSHOP",
            start_at="2024-12-01T10:00:00Z",
            end_at="2024-12-01T12:00:00Z",
            capacity=100
        )

    def test_register_student_to_event(self):
        url = reverse('event-register', args=[self.event.id])
        data = {'student': self.student.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Registration.objects.count(), 1)
        registration = Registration.objects.get()
        self.assertEqual(registration.student, self.student)
        self.assertEqual(registration.event, self.event)

    def test_register_same_student_twice(self):
        url = reverse('event-register', args=[self.event.id])
        data = {'student': self.student.id}
        response1 = self.client.post(url, data, format='json')
        response2 = self.client.post(url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response2.data)
