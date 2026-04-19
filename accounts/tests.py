from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class PortfolioAPITests(TestCase):
    """Tests for Portfolio feature."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_portfolio_page_loads(self):
        """Portfolio page renders for authenticated user."""
        response = self.client.get(reverse('portfolio_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Portfolio Builder')

    def test_portfolio_page_requires_auth(self):
        """Unauthenticated GET redirects to login."""
        self.client.logout()
        response = self.client.get(reverse('portfolio_page'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_portfolio_save_creates_portfolio(self):
        """POST to portfolio_update creates Portfolio if none exists."""
        from accounts.models import Portfolio
        self.assertFalse(Portfolio.objects.filter(user=self.user).exists())
        response = self.client.post(reverse('portfolio_update'), {
            'title': 'My Portfolio',
            'headline': 'SWE',
            'bio': 'Hello world',
            'theme': 'professional',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Portfolio.objects.filter(user=self.user).exists())
        portfolio = Portfolio.objects.get(user=self.user)
        self.assertEqual(portfolio.title, 'My Portfolio')
        self.assertEqual(portfolio.theme, 'professional')
        self.assertFalse(portfolio.is_published)

    def test_portfolio_publish_toggle(self):
        """is_published checkbox saves correctly."""
        response = self.client.post(reverse('portfolio_update'), {
            'title': 'Test',
            'is_published': 'on',
        })
        self.assertEqual(response.status_code, 302)
        from accounts.models import Portfolio
        portfolio = Portfolio.objects.get(user=self.user)
        self.assertTrue(portfolio.is_published)

    def test_portfolio_public_hidden_when_unpublished(self):
        """GET /u/<username>/ returns 404 when not published."""
        from accounts.models import Portfolio
        Portfolio.objects.create(user=self.user, title='Test', is_published=False)
        response = self.client.get(reverse('portfolio_public', args=[self.user.username]))
        self.assertEqual(response.status_code, 404)

    def test_portfolio_public_visible_when_published(self):
        """GET /u/<username>/ renders when published."""
        from accounts.models import Portfolio
        Portfolio.objects.create(user=self.user, title='Test', is_published=True)
        response = self.client.get(reverse('portfolio_public', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test')
        self.assertContains(response, 'My Resumes')

    def test_portfolio_public_nonexistent_user_404(self):
        """GET /u/<nonexistent>/ returns 404."""
        response = self.client.get(reverse('portfolio_public', args=['doesnotexist']))
        self.assertEqual(response.status_code, 404)

    def test_portfolio_public_shows_complete_resumes(self):
        """Public page shows only complete resumes."""
        from resumes.models import Resume
        from accounts.models import Portfolio
        Portfolio.objects.create(user=self.user, is_published=True)
        Resume.objects.create(user=self.user, title='Complete Resume', status='complete')
        Resume.objects.create(user=self.user, title='Draft Resume', status='draft')
        response = self.client.get(reverse('portfolio_public', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete Resume')
        self.assertNotContains(response, 'Draft Resume')
