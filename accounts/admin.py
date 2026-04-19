"""Accounts admin — registers UserProfile to the shared placement admin site."""
from django.contrib import admin
from placement_copilot.admin import placement_admin_site
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription_tier', 'onboarding_completed', 'default_template', 'default_paper_size', 'email_opt_out']
    list_filter = ['subscription_tier', 'onboarding_completed', 'default_template', 'email_opt_out']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']


placement_admin_site.register(UserProfile, UserProfileAdmin)
