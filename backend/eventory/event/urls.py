from django.urls import path, include
from rest_framework.routers import DefaultRouter
from event.views import (
    CollegeViewSet, StudentViewSet, EventViewSet, FeedbackViewSet,
    RegisterUserView, LoginUserView, LogoutUserView
)

router = DefaultRouter()
router.register(r'colleges', CollegeViewSet)
router.register(r'students', StudentViewSet)
router.register(r'events', EventViewSet)
router.register(r'feedbacks', FeedbackViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterUserView.as_view(), name='register'),
    path('auth/login/', LoginUserView.as_view(), name='login'),
    path('auth/logout/', LogoutUserView.as_view(), name='logout'),
]
