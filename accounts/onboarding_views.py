from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
def onboarding_skip(request):
    """Mark onboarding as complete and redirect to dashboard."""
    request.user.profile.onboarding_completed = True
    request.user.profile.save(update_fields=['onboarding_completed'])
    return redirect('dashboard')


@login_required
def onboarding_complete(request):
    """Mark onboarding as complete (called after first resume is created)."""
    request.user.profile.onboarding_completed = True
    request.user.profile.save(update_fields=['onboarding_completed'])
    return redirect('dashboard')
