---
name: P0.1 Auth Design
description: Complete Django auth with password reset, session expiry, and email SMTP
type: project
---

# P0.1 Auth Completion — Implementation Design

**Date:** 2026-04-18
**Epic:** P0.1 Authentication
**Stack:** Django 4.2, Tailwind, Gmail SMTP

---

## 1. Email Backend

### What's changing

Gmail SMTP added via `.env` variables. `settings.py` updated to read them.

### `.env` additions

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=comforttime9@gmail.com
EMAIL_HOST_PASSWORD=<16-char-app-password>
DEFAULT_FROM_EMAIL=Placement Copilot <comforttime9@gmail.com>
```

### `settings.py` additions

After existing settings, add:

```python
# Email settings
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Placement Copilot <noreply@placementcopilot.com>')
```

---

## 2. Password Reset URLs

### `accounts/urls.py` additions

```python
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
)

urlpatterns += [
    path('password_reset/', PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url=reverse('password_reset_done'),
    ), name='password_reset'),

    path('password_reset/done/', PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html',
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse('password_reset_complete'),
    ), name='password_reset_confirm'),

    path('reset/done/', PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html',
    ), name='password_reset_complete'),
]
```

---

## 3. Password Reset Templates

### `templates/registration/password_reset_form.html`

"Enter your email" form. Mirrors the signup/login card style. Single email field + submit. Error shown inline.

```html
{% extends 'base.html' %}
{% block title %}Reset Password - Placement Copilot{% endblock %}

{% block content %}
<div class="min-h-screen flex items-center justify-center py-12 px-4">
    <div class="max-w-md w-full space-y-8">
        <div>
            <h1 class="text-center text-3xl font-bold text-gray-900">Reset Password</h1>
            <p class="mt-2 text-center text-sm text-gray-600">
                Enter your email and we'll send you a reset link.
            </p>
        </div>

        {% if messages %}
        <div class="messages">
            {% for message in messages %}
            <div class="p-4 mb-4 rounded {% if message.tags %}{{ message.tags }}{% endif %}">{{ message }}</div>
            {% endfor %}
        </div>
        {% endif %}

        <form class="mt-8 space-y-6" method="POST">
            {% csrf_token %}
            {% if form.errors %}
            <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {% for error in form.errors %}
                <p>{{ error }}</p>
                {% endfor %}
            </div>
            {% endif %}
            <div>
                <label for="id_email" class="block text-sm font-medium text-gray-700">Email</label>
                <input type="email" name="email" id="id_email" required
                    class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="your@email.com">
            </div>
            <button type="submit" class="w-full py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
                Send Reset Link
            </button>
        </form>
        <div class="text-center">
            <a href="{% url 'login' %}" class="text-sm text-blue-600 hover:text-blue-500">Back to login</a>
        </div>
    </div>
</div>
{% endblock %}
```

### `templates/registration/password_reset_done.html`

Simple confirmation page. "Check your email — we've sent a link."

### `templates/registration/password_reset_confirm.html`

New password form. Two fields: new password + confirm. Uses Django's `set_password_form` from the view context.

### `templates/registration/password_reset_complete.html`

Success page with a "Sign in" link to `/accounts/login/`.

### `templates/registration/password_reset_email.html` (optional override)

Use Django's default email body — no custom email template needed for MVP.

---

## 4. Login Page — "Forgot Password?" Link

### `templates/account/login.html` change

Add below the password field, inside the `<div class="space-y-4">` block:

```html
<div class="text-right">
    <a href="{% url 'password_reset' %}" class="text-sm text-blue-600 hover:text-blue-500">
        Forgot password?
    </a>
</div>
```

---

## 5. Session Expiry Flash Message

### `accounts/views.py` — Custom login_required decorator

```python
from django.contrib.auth.decorators import login_required as django_login_required
from django.contrib import messages

def login_required_with_message(view_func):
    """Wrapper that adds session expiry message on redirect."""
    @django_login_required(login_url='/accounts/login/')
    def wrapper(request, *args, **kwargs):
        # Check if this is a redirect from session expiry
        if request.method == 'GET' and not request.session.session_key:
            # Check if coming from a protected page
            pass
        return view_func(request, *args, **kwargs)
    return wrapper
```

**Simpler approach:** Add a message in the `login_required` redirect path. Django's default `redirect()` call doesn't support messages. Instead, override the login_required behavior by adding a check in middleware or using a custom decorator.

**Final approach:** Create a simple middleware that detects the `next` param from session expiry and adds a flash message:

```python
# In accounts/middleware.py
from django.shortcuts import redirect
from django.contrib import messages

class SessionExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If session expired and user hits a protected page
        if request.user.is_anonymous and request.path.startswith('/dashboard') or \
           request.path.startswith('/resumes') or \
           request.path.startswith('/settings'):
            messages.info(request, 'Your session has expired. Please log in again.')
        return self.get_response(request)
```

Add to `MIDDLEWARE` in `settings.py`.

---

## 6. `?next=` Parameter Verification

Django's `LoginView` already reads `request.GET.get('next')` and passes it through. The current login view uses `AuthenticationForm` which includes the `next` field. **No code changes needed** — verify with tests.

---

## 7. Test Updates

Add test for password reset flow in `accounts/tests.py`:

```python
def test_password_reset_page_loads(self):
    response = self.client.get(reverse('password_reset'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'email')

def test_password_reset_nonexistent_email_shows_success(self):
    """Should show success even if email doesn't exist (prevents enumeration)."""
    response = self.client.post(reverse('password_reset'), {
        'email': 'nonexistent@example.com'
    })
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'email')  # stays on form or shows generic success

def test_forgot_password_link_on_login(self):
    response = self.client.get(reverse('login'))
    self.assertContains(response, 'Forgot password')
```

---

## File Summary

| File | Action |
|------|--------|
| `.env` | Create — email SMTP vars |
| `settings.py` | Edit — email backend config |
| `accounts/urls.py` | Edit — add 4 reset URLs |
| `accounts/middleware.py` | Create — session expiry middleware |
| `templates/registration/password_reset_form.html` | Create |
| `templates/registration/password_reset_done.html` | Create |
| `templates/registration/password_reset_confirm.html` | Create |
| `templates/registration/password_reset_complete.html` | Create |
| `templates/account/login.html` | Edit — add forgot password link |
| `accounts/tests.py` | Edit — add password reset tests |
| `placement_copilot/settings.py` | Edit — register middleware |

---

## Dependencies

- Django 4.2 (already installed)
- Gmail App Password (user-provided)
- `python-dotenv` (already installed)
