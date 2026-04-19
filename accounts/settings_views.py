from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .forms import ProfileForm, CustomPasswordChangeForm, ProfilePreferencesForm


@login_required
def settings(request):
    """Settings page - handles profile, preferences, security, and account sections."""
    profile_form = ProfileForm(instance=request.user)
    password_form = CustomPasswordChangeForm(request.user)
    preferences_form = ProfilePreferencesForm(instance=request.user.profile)

    if request.method == 'POST':
        if 'profile_submit' in request.POST:
            profile_form = ProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully.')
        elif 'password_submit' in request.POST:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password updated successfully.')
            else:
                messages.error(request, 'Please correct the errors below.')
        elif 'preferences_submit' in request.POST:
            preferences_form = ProfilePreferencesForm(request.POST, instance=request.user.profile)
            if preferences_form.is_valid():
                preferences_form.save()
                messages.success(request, 'Preferences saved successfully.')
            else:
                messages.error(request, 'Please correct the errors below.')
        return redirect('settings')

    return render(request, 'settings/settings.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'preferences_form': preferences_form,
    })


@login_required
def settings_delete_account(request):
    """Delete user account."""
    if request.method == 'POST':
        username = request.user.username
        request.user.delete()
        logout(request)
        messages.success(request, f'Account for {username} has been deleted.')
        return redirect('login')

    return redirect('settings')
