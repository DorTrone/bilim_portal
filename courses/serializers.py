from rest_framework import serializers
from .models import Course, Lesson, Category, Enrollment, User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'slug', 'content', 'video_url', 'file', 'order']


class CourseSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    instructor = serializers.StringRelatedField()
    lesson_count = serializers.SerializerMethodField()
    enrolled_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'category',
            'instructor', 'level', 'thumbnail', 'created_at',
            'lesson_count', 'enrolled_count',
        ]

    def get_lesson_count(self, obj):
        return obj.get_lesson_count()

    def get_enrolled_count(self, obj):
        return obj.get_enrolled_count()


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.filter(is_published=True),
        write_only=True, source='course'
    )

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'course_id', 'enrolled_at']
        read_only_fields = ['enrolled_at']
