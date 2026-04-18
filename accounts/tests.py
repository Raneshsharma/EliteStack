from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class SignupTests(TestCase):
    """Tests for user signup functionality"""

    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')

    def test_signup_page_loads(self):
        """Test signup page renders correctly"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200, "Signup page should return 200 OK")
        self.assertTemplateUsed(response, 'account/signup.html')
        self.assertContains(response, 'Sign Up')
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Email')
        self.assertIn('form', response.context, "Response should contain a form")

    def test_signup_page_has_signup_form(self):
        """Test that signup page contains a SignupForm"""
        response = self.client.get(self.signup_url)
        form = response.context['form']
        self.assertEqual(form.__class__.__name__, 'SignupForm',
                         "Form should be a SignupForm instance")

    def test_user_can_signup(self):
        """Test user can successfully sign up with valid data"""
        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
        })

        # Should redirect after successful signup
        self.assertEqual(response.status_code, 302, "Should redirect after successful signup")

        # User should be created in database
        self.assertTrue(User.objects.filter(username='newuser').exists(),
                       "User should be created in database")

        # User should have correct email
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com',
                        "User email should be saved correctly")

        # User should be logged in
        self.assertTrue(self.client.session.get('_auth_user_id'),
                       "User should be logged in after signup")

    def test_user_can_signup_and_redirect_to_dashboard(self):
        """Test that signup redirects to dashboard"""
        response = self.client.post(self.signup_url, {
            'username': 'dashboarduser',
            'email': 'dashboard@example.com',
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
        })

        self.assertEqual(response.status_code, 302, "Should redirect after signup")
        self.assertIn('/dashboard/', response.url, "Should redirect to dashboard")

    def test_signup_duplicate_username(self):
        """Test signup fails with duplicate username"""
        User.objects.create_user('existinguser', 'test@example.com', 'pass123')
        response = self.client.post(self.signup_url, {
            'username': 'existinguser',
            'email': 'another@example.com',
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
        })

        self.assertEqual(response.status_code, 200, "Should show form with errors")
        self.assertFalse(User.objects.filter(email='another@example.com').exists(),
                        "User with duplicate username should not be created")

    def test_signup_password_mismatch(self):
        """Test signup fails when passwords don't match"""
        response = self.client.post(self.signup_url, {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'SecurePassword123!',
            'password2': 'DifferentPassword456!',
        })

        self.assertEqual(response.status_code, 200, "Should show form with errors")
        self.assertFalse(User.objects.filter(username='testuser').exists(),
                        "User should not be created when passwords don't match")

    def test_signup_missing_required_fields(self):
        """Test signup fails when required fields are missing"""
        response = self.client.post(self.signup_url, {
            'username': '',
            'email': '',
            'password1': '',
            'password2': '',
        })

        self.assertEqual(response.status_code, 200, "Should show form with errors")
        self.assertFalse(User.objects.filter(username='').exists(),
                        "User should not be created with empty username")

    def test_signup_redirect_authenticated(self):
        """Test authenticated user is redirected from signup"""
        user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 302, "Should redirect to dashboard")
        self.assertIn('/dashboard/', response.url, "Authenticated user should be redirected")

    def test_signup_post_authenticated_redirects(self):
        """Test POST from authenticated user also redirects"""
        User.objects.create_user('authuser', 'auth@example.com', 'testpass123')
        self.client.login(username='authuser', password='testpass123')

        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
        })

        self.assertEqual(response.status_code, 302, "POST from authenticated user should redirect")

    def test_signup_creates_user_with_all_fields(self):
        """Test that signup creates user with all required fields"""
        self.client.post(self.signup_url, {
            'username': 'completeuser',
            'email': 'complete@example.com',
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
        })

        user = User.objects.get(username='completeuser')
        self.assertEqual(user.username, 'completeuser')
        self.assertEqual(user.email, 'complete@example.com')
        self.assertTrue(user.check_password('SecurePassword123!'),
                       "Password should be set correctly")
        self.assertTrue(user.is_active, "New user should be active")


class LoginTests(TestCase):
    """Tests for user login functionality"""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            'testuser',
            'test@example.com',
            'testpass123'
        )

    def test_login_page_loads(self):
        """Test login page renders correctly"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200, "Login page should return 200 OK")
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Sign In')
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Password')
        self.assertIn('form', response.context, "Response should contain a form")

    def test_login_page_has_login_form(self):
        """Test that login page contains a LoginForm"""
        response = self.client.get(self.login_url)
        form = response.context['form']
        self.assertEqual(form.__class__.__name__, 'LoginForm',
                         "Form should be a LoginForm instance")

    def test_user_can_login(self):
        """Test valid credentials login successfully"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123',
        })

        self.assertEqual(response.status_code, 302, "Should redirect after successful login")
        self.assertIn('/dashboard/', response.url, "Should redirect to dashboard")

        # Verify user is authenticated
        self.assertTrue(self.client.session.get('_auth_user_id'),
                       "User should be logged in after valid login")
        self.assertEqual(int(self.client.session.get('_auth_user_id')), self.user.id,
                        "Logged in user should match created user")

    def test_invalid_credentials_fail(self):
        """Test invalid credentials are rejected"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword',
        })

        self.assertEqual(response.status_code, 200, "Should stay on login page with error")
        self.assertFalse(self.client.session.get('_auth_user_id'),
                        "User should not be logged in with wrong password")
        self.assertContains(response, 'Please enter a correct username and password',
                          msg_prefix="Should show error message for invalid credentials")

    def test_login_nonexistent_user(self):
        """Test login fails with nonexistent user"""
        response = self.client.post(self.login_url, {
            'username': 'nonexistent',
            'password': 'anypassword',
        })

        self.assertEqual(response.status_code, 200, "Should show error")
        self.assertContains(response, 'Please enter a correct username and password')
        self.assertFalse(self.client.session.get('_auth_user_id'),
                        "User should not be logged in with non-existent username")

    def test_login_with_empty_credentials(self):
        """Test login fails with empty credentials"""
        response = self.client.post(self.login_url, {
            'username': '',
            'password': '',
        })

        self.assertEqual(response.status_code, 200, "Should show form with errors")
        self.assertFalse(self.client.session.get('_auth_user_id'),
                        "User should not be logged in with empty credentials")

    def test_login_case_sensitive_username(self):
        """Test that username login is case-sensitive"""
        response = self.client.post(self.login_url, {
            'username': 'TESTUSER',
            'password': 'testpass123',
        })

        self.assertEqual(response.status_code, 200, "Should fail for case mismatch")
        self.assertFalse(self.client.session.get('_auth_user_id'),
                        "Username should be case-sensitive")

    def test_login_redirect_authenticated(self):
        """Test authenticated user is redirected from login"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302, "Should redirect to dashboard")
        self.assertIn('/dashboard/', response.url, "Authenticated user should be redirected")

    def test_login_preserves_user_session(self):
        """Test that login properly sets up user session"""
        session = self.client.session
        self.assertIsNone(session.get('_auth_user_id'), "Should start unauthenticated")

        self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123',
        })

        session = self.client.session
        self.assertEqual(int(session['_auth_user_id']), self.user.id,
                        "Session should contain correct user ID")


class LogoutTests(TestCase):
    """Tests for user logout functionality"""

    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('logout')
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            'testuser',
            'test@example.com',
            'testpass123'
        )

    def test_user_can_logout(self):
        """Test logout clears session"""
        # Login first
        self.client.login(username='testuser', password='testpass123')

        # Verify user is logged in
        self.assertTrue(self.client.session.get('_auth_user_id'),
                       "User should be logged in before logout")

        # Logout
        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, 302, "Should redirect after logout")
        self.assertIn('/accounts/login/', response.url, "Should redirect to login")

        # Session should be cleared
        self.assertFalse(self.client.session.get('_auth_user_id'),
                        "Session should be cleared after logout")

    def test_logout_post_request_required(self):
        """Test that logout works with POST request (standard Django behavior)"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))

    def test_logout_unauthenticated_user(self):
        """Test logout works for unauthenticated user (no-op)"""
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302,
                        "Logout should handle unauthenticated users gracefully")

    def test_logout_clears_authentication(self):
        """Test that user cannot access protected pages after logout"""
        # Login
        self.client.login(username='testuser', password='testpass123')

        # Logout
        self.client.post(self.logout_url)

        # Try to access protected page
        response = self.client.get(reverse('resume_list'))

        self.assertEqual(response.status_code, 302, "Should redirect to login")
        self.assertTrue(response.url.startswith(reverse('login')),
                       "Should redirect to login page")

    def test_logout_then_login_again(self):
        """Test that user can login again after logging out"""
        # Login
        self.client.login(username='testuser', password='testpass123')
        self.client.post(self.logout_url)

        # Login again
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'),
                       "User should be able to login again after logout")


class AuthenticationRedirectTests(TestCase):
    """Tests for authentication-related redirects"""

    def test_protected_page_redirects_to_login(self):
        """Test accessing protected page without auth redirects to login"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302, "Should redirect to login")
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_resume_list_requires_auth(self):
        """Test resume list page requires authentication"""
        response = self.client.get(reverse('resume_list'))
        self.assertEqual(response.status_code, 302, "Should redirect unauthenticated users")

    def test_resume_create_requires_auth(self):
        """Test resume create page requires authentication"""
        response = self.client.get(reverse('resume_create'))
        self.assertEqual(response.status_code, 302, "Should redirect unauthenticated users")

    def test_protected_page_preserves_next_parameter(self):
        """Test that next parameter is preserved for redirect after login"""
        response = self.client.get(reverse('resume_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('next=', response.url,
                     "Redirect should include next parameter")

    def test_authenticated_user_can_access_protected_pages(self):
        """Test that authenticated user can access protected pages"""
        user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.client.login(username='testuser', password='testpass123')

        # Should be able to access dashboard
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302, "Dashboard should be accessible")

        # Should be able to access resume list
        response = self.client.get(reverse('resume_list'))
        self.assertEqual(response.status_code, 200, "Resume list should be accessible")


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
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        confirm_url = reverse('password_reset_confirm', kwargs={
            'uidb64': uid,
            'token': token
        })
        response = self.client.get(confirm_url, follow=True)
        # Should render the confirm page with valid token
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
