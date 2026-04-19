# Placement Copilot - Landing Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a warm, encouraging landing page with playful animations that transforms resume-building from a dreaded task into an exciting journey.

**Architecture:** Django template-based landing page using Tailwind CSS for styling, custom CSS for animations, and vanilla JavaScript for scroll-triggered interactions. Single page with 7 sections flowing in a journey metaphor.

**Tech Stack:** Django 4.2, Tailwind CSS (CDN), Custom CSS animations, Vanilla JS (Intersection Observer)

---

## File Structure

```
d:/EliteSttack/
├── templates/
│   ├── landing.html          # Landing page template (NEW)
│   └── base.html             # Updated with landing nav link
├── static/
│   ├── css/
│   │   ├── landing.css        # Landing page styles (NEW)
│   │   └── animations.css     # Animation keyframes (NEW)
│   └── js/
│       └── landing.js         # Scroll animations, interactions (NEW)
├── resumes/
│   └── views.py               # Add landing_page view
└── placement_copilot/
    └── urls.py                # Add landing page URL
```

---

## Task 1: Landing Page Template Structure

**Files:**
- Create: `templates/landing.html`
- Modify: `templates/base.html`

- [ ] **Step 1: Create landing.html with all 7 sections**

```html
{% extends 'base.html' %}
{% load static %}

{% block title %}Placement Copilot - Build a Resume That Stands Out{% endblock %}

{% block content %}
<!-- Section 1: Navigation -->
<nav id="navbar" class="fixed top-0 left-0 right-0 z-50 transition-all duration-300">
    <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <a href="/" class="text-2xl font-bold text-white">Placement Copilot</a>
        <div class="hidden md:flex items-center gap-8">
            <a href="#features" class="text-white/80 hover:text-white transition-colors">Features</a>
            <a href="#journey" class="text-white/80 hover:text-white transition-colors">How It Works</a>
            <a href="#testimonials" class="text-white/80 hover:text-white transition-colors">Testimonials</a>
        </div>
        <a href="{% url 'signup' %}" class="px-6 py-2 border-2 border-white text-white rounded-full hover:bg-white hover:text-purple-600 transition-all">
            Get Started
        </a>
    </div>
</nav>

<!-- Section 2: Hero -->
<section class="min-h-screen flex items-center justify-center relative overflow-hidden bg-gradient-to-br from-purple-600 to-purple-800">
    <!-- Floating Shapes Background -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="floating-shape shape-1"></div>
        <div class="floating-shape shape-2"></div>
        <div class="floating-shape shape-3"></div>
        <div class="floating-shape shape-4"></div>
    </div>
    
    <div class="relative z-10 text-center px-6 max-w-4xl mx-auto">
        <h1 class="text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6 fade-in-up">
            Build a Resume That Stands Out
        </h1>
        <p class="text-xl md:text-2xl text-white/80 mb-10 fade-in-up delay-200">
            Create a professional resume that tells your story — even if you have no experience yet.
        </p>
        <div class="fade-in-up delay-400">
            <a href="{% url 'signup' %}" class="cta-button inline-block px-10 py-4 bg-coral text-white text-lg font-semibold rounded-full shadow-lg hover:scale-105 transition-transform">
                Build a Resume That Stands Out
            </a>
        </div>
        <p class="mt-8 text-white/60">
            <a href="#journey" class="hover:text-white transition-colors">
                See how it works ↓
            </a>
        </p>
    </div>
</section>

<!-- Section 3: Journey Steps -->
<section id="journey" class="py-24 bg-gradient-to-b from-purple-50 to-white">
    <div class="max-w-7xl mx-auto px-6">
        <h2 class="text-4xl font-bold text-center text-gray-800 mb-16">Your Journey to a Great Resume</h2>
        
        <div class="relative">
            <!-- SVG Path connecting steps -->
            <svg class="hidden lg:block absolute top-1/2 left-0 w-full h-4 -translate-y-1/2" preserveAspectRatio="none">
                <path d="M0,50 Q250,0 500,50 T1000,50 T1500,50 T2000,50" stroke="url(#pathGradient)" stroke-width="4" fill="none" stroke-dasharray="10,10" class="animate-dash"/>
                <defs>
                    <linearGradient id="pathGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" style="stop-color:#8B6BA9"/>
                        <stop offset="100%" style="stop-color:#FF7F6B"/>
                    </linearGradient>
                </defs>
            </svg>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 relative">
                <!-- Step 1 -->
                <div class="journey-card" data-step="1">
                    <div class="bg-white rounded-3xl p-8 shadow-lg hover:shadow-xl transition-shadow">
                        <div class="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mb-6 mx-auto">
                            <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                            </svg>
                        </div>
                        <h3 class="text-xl font-bold text-gray-800 text-center mb-3">Tell Your Story</h3>
                        <p class="text-gray-600 text-center">Add your info and personal details</p>
                    </div>
                </div>
                
                <!-- Step 2 -->
                <div class="journey-card" data-step="2">
                    <div class="bg-white rounded-3xl p-8 shadow-lg hover:shadow-xl transition-shadow">
                        <div class="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mb-6 mx-auto">
                            <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                            </svg>
                        </div>
                        <h3 class="text-xl font-bold text-gray-800 text-center mb-3">Show Your Skills</h3>
                        <p class="text-gray-600 text-center">Add education, projects, experience</p>
                    </div>
                </div>
                
                <!-- Step 3 -->
                <div class="journey-card" data-step="3">
                    <div class="bg-white rounded-3xl p-8 shadow-lg hover:shadow-xl transition-shadow">
                        <div class="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mb-6 mx-auto">
                            <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/>
                            </svg>
                        </div>
                        <h3 class="text-xl font-bold text-gray-800 text-center mb-3">Preview & Polish</h3>
                        <p class="text-gray-600 text-center">See your resume come to life</p>
                    </div>
                </div>
                
                <!-- Step 4 -->
                <div class="journey-card" data-step="4">
                    <div class="bg-white rounded-3xl p-8 shadow-lg hover:shadow-xl transition-shadow">
                        <div class="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mb-6 mx-auto">
                            <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                            </svg>
                        </div>
                        <h3 class="text-xl font-bold text-gray-800 text-center mb-3">Download & Go</h3>
                        <p class="text-gray-600 text-center">Get a resume ready for applications</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- Section 4: Testimonials -->
<section id="testimonials" class="py-24 bg-white">
    <div class="max-w-7xl mx-auto px-6">
        <h2 class="text-4xl font-bold text-center text-gray-800 mb-16">Students Love It</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <!-- Testimonial 1 -->
            <div class="testimonial-card" data-index="1">
                <div class="bg-cream rounded-3xl p-8 relative">
                    <div class="absolute -top-4 left-8 w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center">
                        <span class="text-2xl">👩</span>
                    </div>
                    <p class="text-gray-700 text-lg mt-8 mb-6">"I had zero experience and was terrified to start. This made it so easy!"</p>
                    <p class="font-semibold text-purple-600">Priya S.</p>
                    <p class="text-gray-500 text-sm">Recent Graduate</p>
                </div>
            </div>
            
            <!-- Testimonial 2 -->
            <div class="testimonial-card" data-index="2">
                <div class="bg-cream rounded-3xl p-8 relative">
                    <div class="absolute -top-4 left-8 w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center">
                        <span class="text-2xl">👨</span>
                    </div>
                    <p class="text-gray-700 text-lg mt-8 mb-6">"Built my first resume in 15 minutes. Actually felt proud of it!"</p>
                    <p class="font-semibold text-purple-600">Rahul M.</p>
                    <p class="text-gray-500 text-sm">Final Year Student</p>
                </div>
            </div>
            
            <!-- Testimonial 3 -->
            <div class="testimonial-card" data-index="3">
                <div class="bg-cream rounded-3xl p-8 relative">
                    <div class="absolute -top-4 left-8 w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center">
                        <span class="text-2xl">👩</span>
                    </div>
                    <p class="text-gray-700 text-lg mt-8 mb-6">"Finally a resume builder that doesn't make you feel inadequate."</p>
                    <p class="font-semibold text-purple-600">Sneha K.</p>
                    <p class="text-gray-500 text-sm">First-Time Job Seeker</p>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- Section 5: Why Choose Us -->
<section id="features" class="py-24 bg-gradient-to-b from-white to-purple-50">
    <div class="max-w-7xl mx-auto px-6">
        <h2 class="text-4xl font-bold text-center text-gray-800 mb-16">Why Choose Us</h2>
        
        <div class="flex flex-wrap justify-center gap-8">
            <!-- Feature 1 -->
            <div class="feature-badge" data-feature="1">
                <div class="bg-soft-lavender rounded-full px-8 py-6 flex items-center gap-4 hover:bg-coral group transition-colors">
                    <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center">
                        <span class="text-2xl">💚</span>
                    </div>
                    <div>
                        <h3 class="font-bold text-gray-800 group-hover:text-white transition-colors">No Experience Needed</h3>
                        <p class="text-gray-600 group-hover:text-white/80 text-sm transition-colors">We've been there. Start from zero.</p>
                    </div>
                </div>
            </div>
            
            <!-- Feature 2 -->
            <div class="feature-badge" data-feature="2">
                <div class="bg-soft-lavender rounded-full px-8 py-6 flex items-center gap-4 hover:bg-coral group transition-colors">
                    <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center">
                        <span class="text-2xl">⚡</span>
                    </div>
                    <div>
                        <h3 class="font-bold text-gray-800 group-hover:text-white transition-colors">Quick & Easy</h3>
                        <p class="text-gray-600 group-hover:text-white/80 text-sm transition-colors">15 minutes to a professional resume.</p>
                    </div>
                </div>
            </div>
            
            <!-- Feature 3 -->
            <div class="feature-badge" data-feature="3">
                <div class="bg-soft-lavender rounded-full px-8 py-6 flex items-center gap-4 hover:bg-coral group transition-colors">
                    <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center">
                        <span class="text-2xl">🎁</span>
                    </div>
                    <div>
                        <h3 class="font-bold text-gray-800 group-hover:text-white transition-colors">Always Free</h3>
                        <p class="text-gray-600 group-hover:text-white/80 text-sm transition-colors">No hidden costs, ever.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- Section 6: Final CTA -->
<section class="py-24 bg-gradient-to-br from-purple-600 to-purple-800 relative overflow-hidden">
    <!-- Particle Background -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    
    <div class="relative z-10 max-w-3xl mx-auto text-center px-6">
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-6">Ready to Build Your Story?</h2>
        <p class="text-xl text-white/80 mb-10">Join thousands of students who created their resume with Placement Copilot.</p>
        <a href="{% url 'signup' %}" class="inline-block px-12 py-5 bg-coral text-white text-xl font-bold rounded-full shadow-lg hover:scale-105 transition-transform">
            Build a Resume That Stands Out
        </a>
    </div>
</section>

<!-- Section 7: Footer -->
<footer class="bg-gray-900 text-white py-12">
    <div class="max-w-7xl mx-auto px-6">
        <div class="flex flex-col md:flex-row justify-between items-center gap-6">
            <div class="text-center md:text-left">
                <p class="text-2xl font-bold mb-2">Placement Copilot</p>
                <p class="text-gray-400">Made with ❤️ for job seekers.</p>
            </div>
            <div class="flex gap-6 text-gray-400">
                <a href="#" class="hover:text-white transition-colors">Privacy</a>
                <a href="#" class="hover:text-white transition-colors">Terms</a>
                <a href="#" class="hover:text-white transition-colors">Contact</a>
            </div>
        </div>
        <div class="border-t border-gray-800 mt-8 pt-8 text-center text-gray-500">
            © 2026 Placement Copilot. All rights reserved.
        </div>
    </div>
</footer>
{% endblock %}
```

- [ ] **Step 2: Update base.html to include landing page link**

Modify the nav section in base.html to add a link to the landing page:
```html
<a href="{% url 'landing_page' %}" class="...">Home</a>
```

- [ ] **Step 3: Verify template structure**

Run: `python manage.py check`
Expected: No errors

---

## Task 2: Landing Page Styles (CSS)

**Files:**
- Create: `static/css/landing.css`
- Create: `static/css/animations.css`
- Modify: `templates/base.html` (add CSS links)

- [ ] **Step 1: Create landing.css with custom styles**

```css
/* Color Variables */
:root {
    --primary-bg: #8B6BA9;
    --secondary-bg: #E8E0F0;
    --surface: #FDFBF9;
    --cta: #6B4C9A;
    --accent: #FF7F6B;
    --text-primary: #2D2D3A;
    --text-secondary: #6B6B7B;
    --success: #4ECDC4;
}

/* Custom Colors */
.bg-primary { background-color: var(--primary-bg); }
.bg-secondary { background-color: var(--secondary-bg); }
.bg-surface { background-color: var(--surface); }
.bg-cta { background-color: var(--cta); }
.bg-coral { background-color: var(--accent); }
.text-coral { color: var(--accent); }
.bg-soft-lavender { background-color: var(--secondary-bg); }
.bg-cream { background-color: var(--surface); }

/* Navigation */
#navbar {
    transition: background-color 0.3s ease;
}
#navbar.scrolled {
    background-color: var(--surface);
    box-shadow: 0 2px 20px rgba(0,0,0,0.1);
}
#navbar.scrolled a {
    color: var(--text-primary) !important;
}

/* Hero Section */
.hero-gradient {
    background: linear-gradient(135deg, #8B6BA9 0%, #6B4C9A 100%);
}

/* Journey Cards */
.journey-card {
    opacity: 0;
    transform: translateY(30px);
    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.journey-card.visible {
    opacity: 1;
    transform: translateY(0);
}

/* Testimonial Cards */
.testimonial-card {
    opacity: 0;
    transform: scale(0.95);
    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.testimonial-card.visible {
    opacity: 1;
    transform: scale(1);
}

/* Feature Badges */
.feature-badge {
    opacity: 0;
    transform: rotate(-5deg);
    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.feature-badge.visible {
    opacity: 1;
    transform: rotate(0deg);
}
```

- [ ] **Step 2: Create animations.css with keyframes**

```css
/* Floating Shapes Animation */
@keyframes float {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50% { transform: translateY(-20px) rotate(5deg); }
}

.floating-shape {
    position: absolute;
    border-radius: 50%;
    opacity: 0.1;
    animation: float 6s ease-in-out infinite;
}

.shape-1 {
    width: 300px;
    height: 300px;
    background: white;
    top: 10%;
    left: 5%;
    animation-delay: 0s;
}

.shape-2 {
    width: 200px;
    height: 200px;
    background: white;
    top: 60%;
    right: 10%;
    animation-delay: 1s;
}

.shape-3 {
    width: 150px;
    height: 150px;
    background: white;
    bottom: 20%;
    left: 15%;
    animation-delay: 2s;
}

.shape-4 {
    width: 100px;
    height: 100px;
    background: var(--accent);
    top: 30%;
    right: 30%;
    animation-delay: 3s;
}

/* CTA Button Breathing Animation */
@keyframes breathe {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}

.cta-button {
    animation: breathe 2s ease-in-out infinite;
}

/* Fade In Up Animation */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in-up {
    animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.delay-200 { animation-delay: 0.2s; opacity: 0; }
.delay-400 { animation-delay: 0.4s; opacity: 0; }

/* Particle Animation */
@keyframes particleFloat {
    0%, 100% {
        transform: translateY(0) translateX(0);
        opacity: 0.3;
    }
    50% {
        transform: translateY(-100px) translateX(20px);
        opacity: 0.6;
    }
}

.particle {
    position: absolute;
    width: 10px;
    height: 10px;
    background: white;
    border-radius: 50%;
    animation: particleFloat 4s ease-in-out infinite;
}

.particle:nth-child(1) { left: 10%; animation-delay: 0s; }
.particle:nth-child(2) { left: 25%; animation-delay: 0.5s; }
.particle:nth-child(3) { left: 40%; animation-delay: 1s; }
.particle:nth-child(4) { left: 55%; animation-delay: 1.5s; }
.particle:nth-child(5) { left: 70%; animation-delay: 2s; }
.particle:nth-child(6) { left: 85%; animation-delay: 2.5s; }
.particle:nth-child(7) { left: 15%; animation-delay: 3s; }
.particle:nth-child(8) { left: 60%; animation-delay: 3.5s; }

/* Wave Animation for Journey Cards */
@keyframes waveFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}

.journey-card:nth-child(1) { animation: waveFloat 3s ease-in-out infinite; }
.journey-card:nth-child(2) { animation: waveFloat 3s ease-in-out infinite 0.5s; }
.journey-card:nth-child(3) { animation: waveFloat 3s ease-in-out infinite 1s; }
.journey-card:nth-child(4) { animation: waveFloat 3s ease-in-out infinite 1.5s; }

/* Testimonial Bob Animation */
@keyframes testimonialBob {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}

.testimonial-card:nth-child(1) { animation: testimonialBob 4s ease-in-out infinite; }
.testimonial-card:nth-child(2) { animation: testimonialBob 4s ease-in-out infinite 0.5s; }
.testimonial-card:nth-child(3) { animation: testimonialBob 4s ease-in-out infinite 1s; }

/* SVG Path Animation */
@keyframes dash {
    to {
        stroke-dashoffset: -100;
    }
}

.animate-dash {
    animation: dash 3s linear infinite;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
    .shape-1, .shape-2, .shape-3, .shape-4 {
        width: 100px;
        height: 100px;
    }
}
```

- [ ] **Step 3: Update base.html to link CSS files**

Add to base.html head:
```html
<link rel="stylesheet" href="{% static 'css/landing.css' %}">
<link rel="stylesheet" href="{% static 'css/animations.css' %}">
```

---

## Task 3: Landing Page JavaScript

**Files:**
- Create: `static/js/landing.js`
- Modify: `templates/landing.html` (add script link)

- [ ] **Step 1: Create landing.js with scroll animations**

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // ============================================
    // Navigation Scroll Effect
    // ============================================
    const navbar = document.getElementById('navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // ============================================
    // Scroll-Triggered Animations (Intersection Observer)
    // ============================================
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const animateOnScroll = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    // Observe journey cards
    document.querySelectorAll('.journey-card').forEach(card => {
        animateOnScroll.observe(card);
    });
    
    // Observe testimonial cards
    document.querySelectorAll('.testimonial-card').forEach(card => {
        animateOnScroll.observe(card);
    });
    
    // Observe feature badges
    document.querySelectorAll('.feature-badge').forEach(badge => {
        animateOnScroll.observe(badge);
    });
    
    // ============================================
    // Smooth Scroll for Anchor Links
    // ============================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // ============================================
    // Parallax Effect for Floating Shapes
    // ============================================
    const shapes = document.querySelectorAll('.floating-shape');
    
    window.addEventListener('scroll', function() {
        const scrolled = window.scrollY;
        shapes.forEach((shape, index) => {
            const speed = 0.1 + (index * 0.05);
            shape.style.transform = `translateY(${scrolled * speed}px)`;
        });
    });
    
    console.log('Landing page animations initialized');
});
```

- [ ] **Step 2: Add script to landing.html**

Add before closing `{% endblock %}`:
```html
<script src="{% static 'js/landing.js' %}"></script>
```

- [ ] **Step 3: Verify JavaScript loads**

Check browser console for "Landing page animations initialized"

---

## Task 4: Django View and URL Routing

**Files:**
- Modify: `resumes/views.py`
- Modify: `resumes/urls.py`
- Modify: `placement_copilot/urls.py`

- [ ] **Step 1: Add landing_page view to resumes/views.py**

```python
def landing_page(request):
    """Landing page view - public, no authentication required"""
    return render(request, 'landing.html')
```

- [ ] **Step 2: Update resumes/urls.py to add landing page URL**

```python
from django.urls import path
from . import views

urlpatterns = [
    # ... existing urls ...
    path('', views.landing_page, name='landing_page'),
]
```

- [ ] **Step 3: Update placement_copilot/urls.py to route to landing page**

Modify to serve landing page at root:
```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('resumes.urls')),  # Landing page at root
]
```

- [ ] **Step 4: Verify routing**

Run: `python manage.py check`
Expected: No errors

---

## Task 5: Testing and Verification

**Files:**
- Test: All created files

- [ ] **Step 1: Run Django checks**

Run: `python manage.py check`
Expected: "System check identified no issues (0 silenced)."

- [ ] **Step 2: Start server and verify landing page**

Run: `python manage.py runserver`
Expected: Server starts on http://127.0.0.1:8000/

- [ ] **Step 3: Use Playwright to verify page loads**

```javascript
// Navigate to landing page
await page.goto('http://127.0.0.1:8000/');

// Verify hero section
const headline = await page.textContent('h1');
console.log('Headline:', headline);

// Verify all sections exist
const sections = ['#journey', '#testimonials', '#features'];
for (const section of sections) {
    const exists = await page.$(section);
    console.log(`${section} exists:`, !!exists);
}

// Verify CTA button
const cta = await page.$('a[href*="signup"]');
console.log('CTA button exists:', !!cta);
```

- [ ] **Step 4: Verify animations work (take screenshot)**

```javascript
await page.screenshot({ path: 'landing-page.png' });
```

---

## Task 6: Integration with Existing App

**Files:**
- Modify: `templates/base.html`
- Modify: Navigation consistency

- [ ] **Step 1: Ensure navigation is consistent**

Update base.html nav to show:
- "Home" link for landing page
- "Login" and "Sign Up" buttons
- Logo returns to landing page

- [ ] **Step 2: Verify auth links work**

Click "Get Started" -> should go to signup
Click "Login" -> should go to login page
Click logo -> should go to landing page

---

## Task 7: QA and Final Polish

**Files:**
- Test all responsive breakpoints
- Verify animations are smooth

- [ ] **Step 1: Test responsive design**

Test at:
- Desktop (1920px width)
- Tablet (768px width)
- Mobile (375px width)

- [ ] **Step 2: Verify all CTAs link correctly**

- [ ] **Step 3: Final browser test with Playwright**

```javascript
// Full E2E test
await page.goto('http://127.0.0.1:8000/');
await page.click('a[href*="signup"]');
await page.waitForURL('**/accounts/signup/');
console.log('Navigation works!');
```

---

## Agent Tasks Summary

| Agent | Tasks | Focus |
|-------|-------|-------|
| Frontend Tech Lead | Task 1, 2 | Template structure, CSS styles |
| UI Component Agent | Task 2, 3 | Component specs, animations |
| Animation Specialist | Task 3 | JavaScript scroll animations |
| Backend Tech Lead | Task 4 | Django view, URL routing |
| QA Lead | Task 5, 7 | Testing, cross-browser validation |
| Functional Test Agent | Task 5, 7 | E2E tests, Playwright validation |

---

## Success Criteria

1. ✅ Landing page loads at root URL
2. ✅ All 7 sections render correctly
3. ✅ Navigation works (Home, Get Started)
4. ✅ CTAs link to signup page
5. ✅ Scroll animations trigger on scroll
6. ✅ Hero floating shapes animate
7. ✅ Journey cards reveal with staggered animation
8. ✅ Testimonial cards bob gently
9. ✅ Feature badges rotate on hover
10. ✅ Final CTA has particle animation
11. ✅ Mobile responsive design works
12. ✅ Page loads in under 3 seconds

---

**End of Implementation Plan**