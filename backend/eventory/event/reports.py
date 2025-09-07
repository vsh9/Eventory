from django.db.models import Count, Avg, Q

from event.models import Event, Student, Attendance, Feedback, Registration


class ReportsService:
    @staticmethod
    def event_metrics(event_id):
        total_regs = Registration.objects.filter(event_id=event_id).count()
        return ReportsService.event_report(event_id, total_regs)

    @staticmethod
    def event_report(event_id, total_regs):
        total_att = Attendance.objects.filter(event_id=event_id).count()
        avg_fb = Feedback.objects.filter(event_id=event_id).aggregate(avg=Avg('rating'))['avg']
        attendance_pct = (total_att / total_regs * 100.0) if total_regs else 0.0
        return {
            'event_id': event_id,
            'total_registrations': total_regs,
            'attendance_count': total_att,
            'attendance_percentage': round(attendance_pct, 2),
            'average_feedback': round(avg_fb or 0.0, 2),
        }

    @staticmethod
    def event_popularity(college_id=None, event_type=None):
        qs = Event.objects.all()
        if college_id:
            qs = qs.filter(college_id=college_id)
        if event_type:
            qs = qs.filter(type=event_type)
        qs = qs.annotate(reg_count=Count('registrations')).order_by('-reg_count', '-start_at')
        return [
            {
                'event_id': e.id,
                'title': e.title,
                'college_id': e.college_id,
                'type': e.type,
                'registrations': e.reg_count,
            } for e in qs
        ]

    @staticmethod
    def student_participation(student_id: int):
        att_count = Attendance.objects.filter(student_id=student_id).count()
        reg_count = Registration.objects.filter(student_id=student_id).count()
        return {
            'student_id': student_id,
            'registrations': reg_count,
            'attended': att_count,
        }

    @staticmethod
    def top_students(limit=3, college_id=None):
        qs = Student.objects.all()
        if college_id:
            qs = qs.filter(college_id=college_id)
        qs = qs.annotate(attended=Count('attendances')).order_by('-attended', 'full_name')[:limit]
        return [
            {
                'student_id': s.id,
                'full_name': s.full_name,
                'college_id': s.college_id,
                'events_attended': s.attended,
            } for s in qs
        ]
