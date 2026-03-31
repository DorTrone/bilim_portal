from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .models import Course, Lesson, Enrollment, Category
from .forms import RegisterForm


# ── Home ──────────────────────────────────────────────────────────────────────

def home(request):
    courses = Course.objects.filter(is_published=True).select_related('category', 'instructor')[:6]
    return render(request, 'courses/home.html', {'courses': courses})


# ── Auth ──────────────────────────────────────────────────────────────────────

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Welcome! Your account was created.'))
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


# ── Profile ───────────────────────────────────────────────────────────────────

@login_required
def profile(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    return render(request, 'courses/profile.html', {'enrollments': enrollments})


# ── Courses ───────────────────────────────────────────────────────────────────

def course_list(request):
    qs = Course.objects.filter(is_published=True).select_related('category', 'instructor')

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

    # Filter by category
    category_slug = request.GET.get('category', '')
    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    # Filter by level
    level = request.GET.get('level', '')
    if level:
        qs = qs.filter(level=level)

    # Sort
    sort = request.GET.get('sort', '-created_at')
    allowed_sorts = ['created_at', '-created_at', 'title', '-title']
    if sort in allowed_sorts:
        qs = qs.order_by(sort)

    categories = Category.objects.all()
    return render(request, 'courses/course_list.html', {
        'courses': qs,
        'categories': categories,
        'query': q,
        'selected_category': category_slug,
        'selected_level': level,
        'selected_sort': sort,
    })


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    lessons = course.lessons.all()
    is_enrolled = (
        request.user.is_authenticated and
        Enrollment.objects.filter(user=request.user, course=course).exists()
    )
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
    })


@login_required
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    _obj, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    if created:
        messages.success(request, _('You enrolled in "%(title)s".') % {'title': course.title})
    else:
        messages.info(request, _('You are already enrolled.'))
    return redirect('course_detail', slug=slug)


# ── Lessons ───────────────────────────────────────────────────────────────────

@login_required
def lesson_detail(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)

    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, _('Please enroll in the course first.'))
        return redirect('course_detail', slug=course_slug)

    lessons = course.lessons.all()
    return render(request, 'courses/lesson_detail.html', {
        'course': course,
        'lesson': lesson,
        'lessons': lessons,
    })
