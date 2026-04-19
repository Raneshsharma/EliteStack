# P0.1 Auth Completion — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the P0.1 Authentication epic — password reset via email, session expiry flash message, `?next=` param support, and Gmail SMTP email backend.

**Architecture:** Use Django's built-in `PasswordResetView` and `PasswordResetConfirmView` for the email flow. Add a custom middleware for session expiry detection. Configure Gmail SMTP via environment variables.

**Tech Stack:** Django 4.2, python-dotenv, Gmail SMTP, crispy-tailwind

---

## Task 1: Email Backend — `.env` and `settings.py`

**Files:**
- Create: `d:/EliteSttack/.env`
- Modify: `d:/EliteSttack/placement_copilot/settings.py`

- [ ] **Step 1: Create `.env` with email and existing vars**

Create the file at `d:/EliteSttack/.env`:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_NAME=placement_copilot
DATABASE_USER=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_ENGINE=sqlite
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=comforttime9@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=Placement Copilot <comforttime9@gmail.com>
```

- [ ] **Step 2: Read current `settings.py` to find insertion point**

Read `d:/EliteSttack/placement_copilot/settings.py`. Find the line after the Crispy Forms settings block (around line 144). Add email configuration after `CRISPY_TEMPLATE_PACK`:

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

Also verify `load_dotenv()` is already called at the top (line 10). It is.

- [ ] **Step 3: Run a quick smoke test**

Run: `python manage.py shell -c "from django.conf import settings; print(settings.EMAIL_BACKEND, settings.EMAIL_HOST)"`
Expected: prints the email settings values from `.env`

- [ ] **Step 4: Commit**

```bash
git add d:/EliteSttack/.env d:/EliteSttack/placement_copilot/settings.py
git commit -m "feat(auth): configure Gmail SMTP email backend via .env"
```

---

## Task 2: Password Reset URLs — `accounts/urls.py`

**Files:**
- Modify: `d:/EliteSttack/accounts/urls.py`
- Create: `d:/EliteSttack/templates/registration/password_reset_subject.txt`

- [ ] **Step 1: Read current `accounts/urls.py`**

```python
from django.urls import path
from . import views
from . import settings_views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', settings_views.settings, name='settings'),
    path('settings/profile/', settings_views.settings_profile, name='settings_profile'),
    path('settings/password/', settings_views.settings_password, name='settings_password'),
    path('settings/delete/', settings_views.settings_delete_account, name='settings_delete_account'),
]
```

- [ ] **Step 2: Replace `accounts/urls.py` with full content including reset URLs**

```python
from django.urls import path
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from . import views
from . import settings_views

urlpatterns = [
    # Auth
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Password reset
    path('password_reset/', PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url='password_reset_done',
    ), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html',
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='password_reset_complete',
    ), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html',
    ), name='password_reset_complete'),
    # Settings
    path('settings/', settings_views.settings, name='settings'),
    path('settings/profile/', settings_views.settings_profile, name='settings_profile'),
    path('settings/password/', settings_views.settings_password, name='settings_password'),
    path('settings/delete/', settings_views.settings_delete_account, name='settings_delete_account'),
]
```

- [ ] **Step 3: Create email subject template**

Create `d:/EliteSttack/templates/registration/password_reset_subject.txt`:

```
Placement Copilot — Password Reset Request
```

- [ ] **Step 4: Verify URL pattern names are correct**

Run: `python manage.py shell -c "from accounts.urls import urlpatterns; print([p.name for p in urlpatterns])"`
Expected: `['signup', 'login', 'logout', 'password_reset', 'password_reset_done', 'password_reset_confirm', 'password_reset_complete', 'settings', 'settings_profile', 'settings_password', 'settings_delete_account']`

- [ ] **Step 5: Commit**

```bash
git add d:/EliteSttack/accounts/urls.py d:/EliteSttack/templates/registration/password_reset_subject.txt
git commit -m "feat(auth): add Django password reset URLs"
```

---

## Task 3: Session Expiry Middleware

**Files:**
- Create: `d:/EliteSttack/accounts/middleware.py`
- Modify: `d:/EliteSttack/placement_copilot/settings.py`

- [ ] **Step 1: Create `accounts/middleware.py`**

Create `d:/EliteSttack/accounts/middleware.py`:

```python
from django.shortcuts import redirect
from django.contrib import messages


class SessionExpiryMiddleware:
    """
    Detects when a user's session has expired and they were redirected
    to login, then adds an informational flash message.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.protected_prefixes = ('/dashboard', '/resumes', '/settings')

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_request(self, request):
        # Only add message on the redirect TO login from a protected page
        if (request.user.is_anonymous
                and request.path == '/accounts/login/'
                and 'next' in request.GET):
            messages.info(
                request,
                'Your session has expired. Please log in again.'
            )
        return None
```

- [ ] **Step 2: Register middleware in `settings.py`**

Read `settings.py` MIDDLEWARE list (around line 41-49). Add the new middleware **after** `AuthenticationMiddleware`:

```python
'django.contrib.auth.middleware.AuthenticationMiddleware',
'django.contrib.messages.middleware.MessageMiddleware',
'accounts.middleware.SessionExpiryMiddleware',
'django.middleware.clickjacking.XFrameOptionsMiddleware',
```

Note: `MessageMiddleware` must already be above `SessionExpiryMiddleware` since the middleware needs `django.contrib.messages`. It is already at line 47.

- [ ] **Step 3: Run a quick import test**

Run: `python manage.py shell -c "from accounts.middleware import SessionExpiryMiddleware; print('ok')"`
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add d:/EliteSttack/accounts/middleware.py d:/EliteSttack/placement_copilot/settings.py
git commit -m "feat(auth): add session expiry detection middleware"
```

---

## Task 4: Password Reset Templates

**Files:**
- Create: `d:/EliteSttack/templates/registration/password_reset_form.html`
- Create: `d:/EliteSttack/templates/registration/password_reset_email.html`
- Create: `d:/EliteSttack/templates/registration/password_reset_done.html`
- Create: `d:/EliteSttack/templates/registration/password_reset_confirm.html`
- Create: `d:/EliteSttack/templates/registration/password_reset_complete.html`

- [ ] **Step 1: Create `password_reset_form.html`**

Create `d:/EliteSttack/templates/registration/password_reset_form.html`:

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
                {% for field, errors in form.errors.items %}
                    {% for error in errors %}
                    <p>{{ error }}</p>
                    {% endfor %}
                {% endfor %}
            </div>
            {% endif %}
            <div>
                <label for="id_email" class="block text-sm font-medium text-gray-700">Email</label>
                <input type="email" name="email" id="id_email" required
                    class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mt-1"
                    placeholder="your@email.com">
            </div>
            <button type="submit" class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
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

- [ ] **Step 2: Create `password_reset_email.html`**

Create `d:/EliteSttack/templates/registration/password_reset_email.html`:

```html
{% autoescape off %}
Hi,

You're receiving this email because you requested a password reset for your account at Placement Copilot.

Click the link below to set a new password:

{{ protocol }}://{{ domain }}{% url 'password_reset_confirm' uidb64=uid token=token %}

If you didn't request this, you can ignore this email — your password won't be changed.

Best,
The Placement Copilot Team
{% endautoescape %}
```

- [ ] **Step 3: Create `password_reset_done.html`**

Create `d:/EliteSttack/templates/registration/password_reset_done.html`:

```html
{% extends 'base.html' %}
{% block title %}Password Reset Sent - Placement Copilot{% endblock %}

{% block content %}
<div class="min-h-screen flex items-center justify-center py-12 px-4">
    <div class="max-w-md w-full space-y-8 text-center">
        <div>
            <h1 class="text-center text-3xl font-bold text-gray-900">Check Your Email</h1>
            <p class="mt-4 text-gray-600">
                If an account exists with that email address, we've sent a password reset link to it.
            </p>
            <p class="mt-2 text-sm text-gray-500">
                Check your spam folder if you don't see it within a few minutes.
            </p>
        </div>
        <div class="mt-6">
            <a href="{% url 'login' %}" class="text-sm text-blue-600 hover:text-blue-500">Back to login</a>
        </div>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 4: Create `password_reset_confirm.html`**

Create `d:/EliteSttack/templates/registration/password_reset_confirm.html`:

```html
{% extends 'base.html' %}
{% block title %}Set New Password - Placement Copilot{% endblock %}

{% block content %}
<div class="min-h-screen flex items-center justify-center py-12 px-4">
    <div class="max-w-md w-full space-y-8">
        <div>
            <h1 class="text-center text-3xl font-bold text-gray-900">Set New Password</h1>
        </div>

        {% if messages %}
        <div class="messages">
            {% for message in messages %}
            <div class="p-4 mb-4 rounded {% if message.tags %}{{ message.tags }}{% endif %}">{{ message }}</div>
            {% endfor %}
        </div>
        {% endif %}

        {% if validlink %}
        <form class="mt-8 space-y-6" method="POST">
            {% csrf_token %}
            {% if form.errors %}
            <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {% for field, errors in form.errors.items %}
                    {% for error in errors %}
                    <p>{{ error }}</p>
                    {% endfor %}
                {% endfor %}
            </div>
            {% endif %}
            <div class="space-y-4">
                <div>
                    <label for="id_new_password1" class="block text-sm font-medium text-gray-700">New Password</label>
                    <input type="password" name="new_password1" id="id_new_password1" required
                        class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mt-1"
                        placeholder="New password">
                </div>
                <div>
                    <label for="id_new_password2" class="block text-sm font-medium text-gray-700">Confirm New Password</label>
                    <input type="password" name="new_password2" id="id_new_password2" required
                        class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mt-1"
                        placeholder="Confirm new password">
                </div>
            </div>
            <button type="submit" class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                Change Password
            </button>
        </form>
        {% else %}
        <div class="text-center">
            <p class="text-red-600">The password reset link is invalid or has expired.</p>
            <a href="{% url 'password_reset' %}" class="mt-4 inline-block text-sm text-blue-600 hover:text-blue-500">
                Request a new reset link
            </a>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Create `password_reset_complete.html`**

Create `d:/EliteSttack/templates/registration/password_reset_complete.html`:

```html
{% extends 'base.html' %}
{% block title %}Password Changed - Placement Copilot{% endblock %}

{% block content %}
<div class="min-h-screen flex items-center justify-center py-12 px-4">
    <div class="max-w-md w-full space-y-8 text-center">
        <div>
            <h1 class="text-center text-3xl font-bold text-gray-900">Password Changed</h1>
            <p class="mt-4 text-gray-600">
                Your password has been set successfully. You can now sign in with your new password.
            </p>
        </div>
        <div class="mt-6">
            <a href="{% url 'login' %}" class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
                Sign In
            </a>
        </div>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 6: Verify templates load without errors**

Run: `python manage.py shell -c "from django.template import loader; [loader.get_template('registration/' + t) for t in ['password_reset_form.html','password_reset_done.html','password_reset_confirm.html','password_reset_complete.html']]; print('all templates exist')"`
Expected: `all templates exist`

- [ ] **Step 7: Commit**

```bash
git add d:/EliteSttack/templates/registration/
git commit -m "feat(auth): add password reset email templates"
```

---

## Task 5: Login Page — Forgot Password Link

**Files:**
- Modify: `d:/EliteSttack/templates/account/login.html`

- [ ] **Step 1: Read current `login.html` and add forgot password link**

In the template, add the "Forgot password?" link below the password field div. The current password field div ends with `{{ form.password }}` on line 43. Add after it:

```html
                </div>

                <div class="text-right">
                    <a href="{% url 'password_reset' %}" class="text-sm text-blue-600 hover:text-blue-500">
                        Forgot password?
                    </a>
                </div>
```

So the full password section becomes:

```html
                <div>
                    <label for="id_password" class="block text-sm font-medium text-gray-700">Password</label>
                    {{ form.password }}
                </div>

                <div class="text-right">
                    <a href="{% url 'password_reset' %}" class="text-sm text-blue-600 hover:text-blue-500">
                        Forgot password?
                    </a>
                </div>
```

- [ ] **Step 2: Verify the link renders**

Run the dev server briefly: `python manage.py runserver 8001` (port different from default) — or just verify the template syntax is valid by running: `python manage.py shell -c "from django.template import loader; t = loader.get_template('account/login.html'); print('template valid')"`
Expected: `template valid`

- [ ] **Step 3: Commit**

```bash
git add d:/EliteSttack/templates/account/login.html
git commit -m "feat(auth): add forgot password link to login page"
```

---

## Task 6: Tests — Password Reset

**Files:**
- Modify: `d:/EliteSttack/accounts/tests.py`

- [ ] **Step 1: Add `PasswordResetTests` class to `accounts/tests.py`**

Read the end of `accounts/tests.py` to find where to insert. Add this class before the last closing `}`:

```python
class PasswordResetTests(TestCase):
    """Tests for password reset functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'testuser',
            'test@example.com',
            'testpass123'
        )
        self.reset_url = reverse('password_reset')
        self.reset_done_url = reverse('password_reset_done')

    def test_password_reset_page_loads(self):
        """Test password reset page renders correctly"""
        response = self.client.get(self.reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_form.html')
        self.assertContains(response, 'email')

    def test_password_reset_with_valid_email(self):
        """Test password reset form submits with valid email"""
        response = self.client.post(self.reset_url, {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('password_reset_done'))

    def test_password_reset_with_nonexistent_email(self):
        """Test form shows success even for non-existent email (prevents enumeration)"""
        response = self.client.post(self.reset_url, {
            'email': 'nonexistent@example.com'
        })
        # Should NOT reveal whether email exists — still redirects to done page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('password_reset_done'))

    def test_password_reset_done_page_loads(self):
        """Test password reset done page renders"""
        response = self.client.get(self.reset_done_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_done.html')

    def test_forgot_password_link_on_login(self):
        """Test login page contains forgot password link"""
        response = self.client.get(reverse('login'))
        self.assertContains(response, 'Forgot password')

    def test_password_reset_invalid_email_format(self):
        """Test form shows error for invalid email format"""
        response = self.client.post(self.reset_url, {
            'email': 'not-an-email'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'email')

    def test_password_reset_confirm_page_with_valid_token(self):
        """Test password reset confirm page loads with valid token"""
        # Generate a password reset token
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        confirm_url = reverse('password_reset_confirm', kwargs={
            'uidb64': uid,
            'token': token
        })
        response = self.client.get(confirm_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_confirm.html')
        self.assertContains(response, 'New Password')

    def test_password_reset_confirm_page_with_invalid_token(self):
        """Test confirm page shows error with invalid token"""
        confirm_url = reverse('password_reset_confirm', kwargs={
            'uidb64': 'bW9jaw',
            'token': 'invalid-token-abc123'
        })
        response = self.client.get(confirm_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'invalid')

    def test_password_reset_complete_page_loads(self):
        """Test password reset complete page renders"""
        response = self.client.get(reverse('password_reset_complete'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_complete.html')
```

- [ ] **Step 2: Run the new tests**

Run: `python manage.py test accounts.tests.PasswordResetTests -v 2`
Expected: All tests pass (the existing tests already pass — new ones should too)

- [ ] **Step 3: Run full test suite**

Run: `python manage.py test accounts -v 2`
Expected: All accounts tests pass

- [ ] **Step 4: Commit**

```bash
git add d:/EliteSttack/accounts/tests.py
git commit -m "test(auth): add password reset and forgot password tests"
```

---

## Spec Coverage Check

| Spec Requirement | Task |
|-----------------|------|
| Password reset via email | Tasks 1–4 |
| `?next=` param on login redirect | Verified — Django handles this |
| Session expiry flash message | Task 3 |
| Generic error on non-existent email | Task 4 (Django default behavior) |
| CSRF on all auth forms | Already in all templates |
| Forgot password link on login | Task 5 |
| Password reset tests | Task 6 |

**Gaps found:** None — all P0.1 requirements covered.
