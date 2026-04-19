from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extension of Django User for onboarding and preferences."""
    TEMPLATE_CHOICES = [
        ('classic', 'Classic'),
        ('modern', 'Modern'),
        ('minimal', 'Minimal'),
    ]
    PAPER_SIZE_CHOICES = [
        ('letter', 'US Letter'),
        ('a4', 'A4'),
    ]

    TIER_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('premium', 'Premium'),
    ]
    subscription_tier = models.CharField(
        max_length=20,
        choices=TIER_CHOICES,
        default='free'
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    onboarding_completed = models.BooleanField(default=False)
    default_template = models.CharField(
        max_length=20,
        choices=TEMPLATE_CHOICES,
        default='classic'
    )
    default_paper_size = models.CharField(
        max_length=10,
        choices=PAPER_SIZE_CHOICES,
        default='letter'
    )
    email_opt_out = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile for {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile whenever a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile whenever User is saved, if it exists."""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Portfolio(models.Model):
    """A public portfolio page for a user."""
    THEME_CHOICES = [
        ('minimal', 'Minimal'),
        ('professional', 'Professional'),
        ('creative', 'Creative'),
    ]
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='portfolio'
    )
    title = models.CharField(max_length=200, default='My Portfolio')
    headline = models.CharField(max_length=200, blank=True)
    bio = models.TextField(max_length=1000, blank=True)
    website_url = models.URLField(max_length=200, blank=True)
    github_url = models.URLField(max_length=200, blank=True)
    linkedin_url = models.URLField(max_length=200, blank=True)
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='professional')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def public_url(self):
        return f"/u/{self.user.username}/"
