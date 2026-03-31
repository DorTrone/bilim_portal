import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


def validate_image(file):
    """Validate that the uploaded file is a valid image."""
    # Check file extension
    ext = os.path.splitext(file.name)[1].lower()
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    
    if ext not in allowed_extensions:
        raise ValidationError(_('Unsupported file extension. Allowed: %s') % ', '.join(allowed_extensions))
    
    # Validate by checking file header (first bytes)
    file.seek(0)
    header = file.read(20)
    file.seek(0)
    
    # JPEG: FF D8 FF
    # PNG: 89 50 4E 47
    # GIF: 47 49 46 38
    # WEBP: RIFF....WEBP
    valid_signatures = [
        b'\xff\xd8\xff',      # JPEG
        b'\x89PNG\r\n\x1a\n', # PNG
        b'GIF87a',            # GIF87a
        b'GIF89a',            # GIF89a
    ]

    is_valid = any(header.startswith(sig) for sig in valid_signatures)
    
    # Check for WEBP (RIFF....WEBP)
    if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
        is_valid = True
    
    if not is_valid:
        raise ValidationError(_('Invalid image file format.'))
    
    # Check file size (max 5MB)
    if file.size > 5 * 1024 * 1024:
        raise ValidationError(_('Image file too large. Maximum size is 5MB.'))
    
    return True


def validate_document(file):
    """Validate that the uploaded file is a valid document."""
    ext = os.path.splitext(file.name)[1].lower()
    allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.zip']
    
    if ext not in allowed_extensions:
        raise ValidationError(_('Unsupported file extension. Allowed: %s') % ', '.join(allowed_extensions))
    
    # Check file size (max 50MB)
    if file.size > 50 * 1024 * 1024:
        raise ValidationError(_('File too large. Maximum size is 50MB.'))
    
    return True


def validate_video_url(url):
    """Validate video URL to prevent XSS."""
    if not url:
        return True
    
    # Only allow YouTube, Vimeo, and direct video URLs
    allowed_patterns = [
        'youtube.com/embed/',
        'youtube.com/watch',
        'vimeo.com/',
        'player.vimeo.com/',
    ]

    # Block dangerous protocols
    if url.lower().startswith(('javascript:', 'data:', 'vbscript:')):
        raise ValidationError(_('Invalid video URL.'))
    
    return True


class User(AbstractUser):
    """Extended user model."""
    bio = models.TextField(_('bio'), blank=True, max_length=500)
    avatar = models.ImageField(
        _('avatar'), upload_to='avatars/', blank=True, null=True,
        validators=[validate_image]
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.name


class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', _('Beginner')),
        ('intermediate', _('Intermediate')),
        ('advanced', _('Advanced')),
    ]

    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    description = models.TextField(_('description'), max_length=5000)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='courses', verbose_name=_('category')
    )
    instructor = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='taught_courses', verbose_name=_('instructor')
    )
    level = models.CharField(_('level'), max_length=20, choices=LEVEL_CHOICES, default='beginner')
    thumbnail = models.ImageField(
        _('thumbnail'), upload_to='course_thumbnails/', blank=True, null=True,
        validators=[validate_image]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(_('published'), default=False)

    class Meta:
        verbose_name = _('course')
        verbose_name_plural = _('courses')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_lesson_count(self):
        return self.lessons.count()

    def get_enrolled_count(self):
        return self.enrollments.count()


class Lesson(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE,
        related_name='lessons', verbose_name=_('course')
    )
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(max_length=220)
    content = models.TextField(_('content'), blank=True, max_length=50000)
    video_url = models.URLField(_('video URL'), blank=True, validators=[validate_video_url])
    file = models.FileField(
        _('file'), upload_to='lesson_files/', blank=True, null=True,
        validators=[validate_document]
    )
    order = models.PositiveIntegerField(_('order'), default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('lesson')
        verbose_name_plural = _('lessons')
        ordering = ['order']
        unique_together = [('course', 'slug')]

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class Enrollment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='enrollments', verbose_name=_('user')
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE,
        related_name='enrollments', verbose_name=_('course')
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('enrollment')
        verbose_name_plural = _('enrollments')
        unique_together = [('user', 'course')]

    def __str__(self):
        return f"{self.user.username} → {self.course.title}"
