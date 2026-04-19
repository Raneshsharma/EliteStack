"""
Shared admin site for Placement Copilot. Imported by placement_copilot/admin.py
before app-level admin modules, and referenced in placement_copilot/urls.py.
"""
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta


class PlacementAdminSite(admin.AdminSite):
    site_header = "Placement Copilot Admin"
    site_title = "Placement Copilot Admin"
    index_title = "Welcome to Placement Copilot Administration"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['platform_stats'] = _get_platform_stats()
        return super().index(request, extra_context)


def _get_platform_stats():
    from resumes.models import Resume
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    return {
        'total_users': User.objects.count(),
        'total_resumes': Resume.objects.count(),
        'users_this_week': User.objects.filter(date_joined__gte=week_ago).count(),
        'resumes_this_week': Resume.objects.filter(created_at__gte=week_ago).count(),
    }


# Singleton — all apps register to this site
placement_admin_site = PlacementAdminSite(name='admin')


def export_users_csv(modeladmin, request, queryset):
    """Export selected users to CSV."""
    import csv
    from django.http import HttpResponse
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Date Joined', 'Last Login', 'Is Staff', 'Is Active'])
    for user in queryset:
        writer.writerow([
            user.username, user.email, user.first_name, user.last_name,
            user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            (user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else ''),
            user.is_staff, user.is_active,
        ])
    return response


export_users_csv.short_description = 'Export selected users to CSV'


class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'date_joined', 'is_staff', 'subscription_tier_badge', 'status_badge']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    actions = [export_users_csv]

    def subscription_tier_badge(self, obj):
        try:
            tier = obj.profile.subscription_tier
            color = {'free': 'gray', 'pro': 'blue', 'premium': 'green'}.get(tier, 'gray')
            return format_html('<span style="color:{}">{}</span>', color, tier.title())
        except Exception:
            return '-'
    subscription_tier_badge.short_description = 'Tier'

    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color:green">Active</span>')
        return format_html('<span style="color:red">Inactive</span>')
    status_badge.short_description = 'Status'


placement_admin_site.register(User, CustomUserAdmin)
