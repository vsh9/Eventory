from django import forms
from django.contrib import admin
from .models import College, Student, Event, Registration, Attendance, Feedback


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'location', 'tot_students')
    search_fields = ('name', 'code')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'roll_no', 'college', 'college_code')
    list_filter = ('college',)
    search_fields = ('full_name', 'roll_no')

class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'college', 'type', 'start_at', 'capacity')
    list_filter = ('college', 'type')
    search_fields = ('title',)
    inlines = [RegistrationInline]


admin.site.register(Registration)
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'student', 'college', 'has_given_feedback', 'checked_in_at')
    list_filter = ('college', 'has_given_feedback')
    search_fields = ('student__full_name', 'event__title')
class FeedbackAdminForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = '__all__'

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating

class FeedbackAdmin(admin.ModelAdmin):
    form = FeedbackAdminForm
    list_display = ('id', 'event', 'student', 'rating', 'comment', 'created_at')

admin.site.register(Feedback, FeedbackAdmin)
