from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def relative_time(dt):
    """Return a human-readable relative time string."""
    if not dt:
        return ''
    now = timezone.now()
    diff = now - dt
    total_seconds = diff.total_seconds()
    if total_seconds < 60:
        return 'just now'
    elif total_seconds < 3600:
        minutes = int(total_seconds / 60)
        return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
    elif total_seconds < 86400:
        hours = int(total_seconds / 3600)
        return f'{hours} hour{"s" if hours != 1 else ""} ago'
    elif total_seconds < 604800:
        days = int(total_seconds / 86400)
        return f'{days} day{"s" if days != 1 else ""} ago'
    else:
        return dt.strftime('%b %d, %Y')
