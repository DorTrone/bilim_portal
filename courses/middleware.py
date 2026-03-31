"""
Security middleware for rate limiting and brute-force protection.
"""
import time
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.cache import cache


class BruteForceProtectionMiddleware:
    """
    Simple brute-force protection for login attempts.
    Blocks IP after 5 failed attempts within 15 minutes.
    """
    
    MAX_ATTEMPTS = 5
    BLOCK_TIMEOUT = 900  # 15 minutes
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only check POST requests to login
        if request.method == 'POST' and 'login' in request.path:
            ip = self.get_client_ip(request)
            cache_key = f'login_failed:{ip}'
            
            failed_attempts = cache.get(cache_key, 0)
            
            if failed_attempts >= self.MAX_ATTEMPTS:
                return render_blocked_response(request)
        
        response = self.get_response(request)
        
        # Track failed login attempts
        if request.method == 'POST' and 'login' in request.path:
            if response.status_code == 200 and 'login' in request.path:
                # Check if it's a failed login (form errors)
                if hasattr(request, 'post_login_failed'):
                    ip = self.get_client_ip(request)
                    cache_key = f'login_failed:{ip}'
                    failed_attempts = cache.get(cache_key, 0)
                    cache.set(cache_key, failed_attempts + 1, self.BLOCK_TIMEOUT)
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


def render_blocked_response(request):
    from django.http import HttpResponseForbidden
    from django.template import Template, Context
    
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Too Many Requests</title></head>
    <body style="font-family: sans-serif; text-align: center; padding: 50px;">
        <h1>🚫 Too Many Login Attempts</h1>
        <p>You have made too many failed login attempts.</p>
        <p>Please try again in 15 minutes.</p>
        <a href="/auth/login/">Back to Login</a>
    </body>
    </html>
    """
    return HttpResponseForbidden(html, content_type='text/html')


class SecurityHeadersMiddleware:
    """
    Add security headers to all responses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Remove server identification
        response.server = 'SciencePortal'
        
        return response
