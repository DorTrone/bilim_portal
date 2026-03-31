"""
Management command to seed demo data.
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Category, Course, Lesson

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed demo data for development'

    def handle(self, *args, **kwargs):
        # Admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin / admin123'))

        # Demo instructor
        instructor, _ = User.objects.get_or_create(
            username='instructor',
            defaults={'email': 'instructor@example.com', 'is_staff': True}
        )
        instructor.set_password('instructor123')
        instructor.save()

        # Categories
        physics, _ = Category.objects.get_or_create(name='Physics', defaults={'slug': 'physics'})
        chemistry, _ = Category.objects.get_or_create(name='Chemistry', defaults={'slug': 'chemistry'})
        biology, _ = Category.objects.get_or_create(name='Biology', defaults={'slug': 'biology'})
        self.stdout.write(self.style.SUCCESS('Categories created'))

        # Courses
        courses_data = [
            {
                'title': 'Introduction to Physics',
                'slug': 'intro-physics',
                'description': 'Learn the fundamentals of classical mechanics, thermodynamics, and electromagnetism.',
                'category': physics,
                'level': 'beginner',
                'lessons': [
                    ('What is Physics?', 'intro-lesson', 'Physics is the natural science that studies matter, its fundamental constituents, its motion and behavior through space and time.'),
                    ('Newton\'s Laws of Motion', 'newtons-laws', 'Newton formulated three laws that describe the relationship between the motion of an object and the forces acting on it.'),
                    ('Energy and Work', 'energy-work', 'Energy is the ability to do work. Work is done when a force causes displacement.'),
                ],
            },
            {
                'title': 'Organic Chemistry Basics',
                'slug': 'organic-chemistry',
                'description': 'Explore carbon-based compounds, reactions, and fundamental principles of organic chemistry.',
                'category': chemistry,
                'level': 'intermediate',
                'lessons': [
                    ('Introduction to Organic Chemistry', 'intro-organic', 'Organic chemistry studies compounds containing carbon.'),
                    ('Functional Groups', 'functional-groups', 'Functional groups are specific groups of atoms within molecules that are responsible for the characteristic chemical reactions.'),
                ],
            },
            {
                'title': 'Cell Biology',
                'slug': 'cell-biology',
                'description': 'Understand the structure and function of cells — the building blocks of all living organisms.',
                'category': biology,
                'level': 'beginner',
                'lessons': [
                    ('The Cell Theory', 'cell-theory', 'The cell theory states that all living organisms are composed of cells.'),
                    ('Cell Structure', 'cell-structure', 'Cells contain organelles such as the nucleus, mitochondria, and ribosomes.'),
                    ('Cell Division', 'cell-division', 'Cells reproduce through mitosis and meiosis.'),
                ],
            },
        ]

        for cd in courses_data:
            lessons_data = cd.pop('lessons')
            course, created = Course.objects.get_or_create(
                slug=cd['slug'],
                defaults={**cd, 'instructor': instructor, 'is_published': True}
            )
            if created:
                for i, (title, slug, content) in enumerate(lessons_data):
                    Lesson.objects.get_or_create(
                        course=course, slug=slug,
                        defaults={'title': title, 'content': content, 'order': i + 1}
                    )
                self.stdout.write(self.style.SUCCESS(f'Created course: {course.title}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Demo data ready!'))
        self.stdout.write('   Login: admin / admin123')
        self.stdout.write('   Instructor: instructor / instructor123')
