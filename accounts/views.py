from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404
from .forms import SignupForm, LoginForm
from .models import UserProfile, Portfolio


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Placement Copilot.')
            return redirect('welcome')
    else:
        form = SignupForm()
    return render(request, 'account/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Ensure profile exists for users created before signal was added
                UserProfile.objects.get_or_create(user=user)
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def portfolio_page(request):
    """Portfolio editor page (owner only)."""
    portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
    return render(request, 'accounts/portfolio.html', {'portfolio': portfolio})


@login_required
def portfolio_update(request):
    """Save portfolio settings (title, bio, links, theme, publish toggle)."""
    if request.method == 'POST':
        portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
        portfolio.title = request.POST.get('title', portfolio.title)[:200]
        portfolio.headline = request.POST.get('headline', portfolio.headline)[:200]
        portfolio.bio = request.POST.get('bio', portfolio.bio)[:1000]
        portfolio.website_url = request.POST.get('website_url', '')[:200]
        portfolio.github_url = request.POST.get('github_url', '')[:200]
        portfolio.linkedin_url = request.POST.get('linkedin_url', '')[:200]
        portfolio.theme = request.POST.get('theme', portfolio.theme)
        portfolio.is_published = request.POST.get('is_published') == 'on'
        portfolio.save()
        messages.success(request, 'Portfolio saved!')
    return redirect('portfolio_page')


def portfolio_public(request, username):
    """Public portfolio page — visible to anyone."""
    user = get_object_or_404(User, username=username)
    try:
        portfolio = user.portfolio
    except Portfolio.DoesNotExist:
        raise Http404("Portfolio not found.")
    if not portfolio.is_published:
        raise Http404("Portfolio not found.")
    resumes = user.resumes.filter(status='complete').order_by('-updated_at')
    return render(request, 'accounts/portfolio_public.html', {
        'portfolio': portfolio,
        'resumes': resumes,
    })