from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CourseViewSet, LessonViewSet, EnrollmentViewSet, CategoryViewSet, current_user

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('courses', CourseViewSet)
router.register('enrollments', EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
    path('me/', current_user, name='api_me'),
    path('auth/', include('rest_framework.urls')),
    path('courses/<slug:course_slug>/lessons/', LessonViewSet.as_view({'get': 'list'}), name='api_lessons'),
    path('courses/<slug:course_slug>/lessons/<int:pk>/', LessonViewSet.as_view({'get': 'retrieve'}), name='api_lesson_detail'),
]
