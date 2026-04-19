# P0.2 Resume Builder — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the resume edit page with a two-panel builder featuring live preview, auto-save, progress indicator, collapsible sections, and 3 template styles (classic/modern/minimal).

**Architecture:** REST API (djangorestframework) for auto-save PATCH calls. Preview refresh via dedicated fragment view per template style. Vanilla JS for all client-side behavior (no framework).

**Tech Stack:** Django 4.2, djangorestframework, Tailwind CSS, vanilla JS

---

## File Structure

| File | Action |
|------|--------|
| `requirements.txt` | Edit — add `djangorestframework` |
| `resumes/models.py` | Edit — add 3 fields to Resume + computed_status property |
| `resumes/serializers.py` | Create — ResumeSerializer, ResumeListSerializer |
| `resumes/views.py` | Edit — add ResumeViewSet + resume_preview_fragment |
| `resumes/urls.py` | Edit — add API router + preview-fragment URL |
| `resumes/admin.py` | Edit — register new fields |
| `resumes/tests.py` | Edit — add API and builder tests |
| `templates/resumes/resume_builder.html` | Create (replaces resume_update.html) |
| `templates/resumes/resume_classic.html` | Create (copy of existing preview) |
| `templates/resumes/resume_modern.html` | Create (new style) |
| `templates/resumes/resume_minimal.html` | Create (new style) |

---

## Context

- **Existing model:** `resumes/models.py` has `Resume`, `ResumeEducation`, `ResumeExperience`, `ResumeProject`, `ResumeSkill` — all with `user` FK and standard Django fields.
- **Existing preview template:** `templates/resumes/resume_preview.html` — classic LaTeX-style with serif fonts, blue headers, uppercase name, pipe-separated contact info. Use this as the base for `resume_classic.html`.
- **Existing URL name:** `resume_update` → currently serves a plain edit form. Will be replaced by `resume_builder.html`.
- **Authentication:** All resume views require login (handled by existing URL routing).
- **NOT a git repo** — skip git operations throughout.

---

## Task 1: Install djangorestframework + add model fields

**Files:**
- Modify: `requirements.txt`
- Modify: `resumes/models.py:1-30`
- Create: `resumes/migrations/XXXXXX_add_builder_fields.py` (auto-generated)

- [ ] **Step 1: Add djangorestframework to requirements.txt**

Read `requirements.txt` and add `djangorestframework` on its own line.

- [ ] **Step 2: Add three new fields to Resume model**

Read `resumes/models.py`. On the `Resume` class, add after existing fields:

```python
professional_summary = models.TextField(max_length=500, blank=True)
template_style = models.CharField(max_length=20, default='classic')  # classic | modern | minimal
status = models.CharField(max_length=20, default='draft')  # draft | complete
```

Also add this computed property inside the `Resume` class:

```python
@property
def computed_status(self):
    has_personal = bool(self.full_name and self.email)
    has_entries = self.education.exists() or self.experience.exists()
    return 'complete' if (has_personal and has_entries) else 'draft'
```

- [ ] **Step 3: Generate migration**

Run: `cd d:/EliteSttack && python manage.py makemigrations resumes`

Expected: Migration created with additions for `professional_summary`, `template_style`, `status`.

- [ ] **Step 4: Apply migration**

Run: `python manage.py migrate`

Expected: Applied successfully.

- [ ] **Step 5: Install djangorestframework**

Run: `pip install djangorestframework`

---

## Task 2: REST API — Serializers + ViewSet + preview-fragment endpoint

**Files:**
- Create: `resumes/serializers.py`
- Modify: `resumes/views.py` (add ViewSet + preview-fragment view)
- Modify: `resumes/urls.py` (add router + preview-fragment URL)

- [ ] **Step 1: Create serializers.py**

Create `resumes/serializers.py`:

```python
from rest_framework import serializers
from .models import Resume, ResumeEducation, ResumeExperience, ResumeProject, ResumeSkill


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = [
            'id', 'title', 'full_name', 'email', 'phone', 'location',
            'linkedin', 'github', 'website', 'professional_summary',
            'template_style', 'status',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ResumeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view."""
    class Meta:
        model = Resume
        fields = ['id', 'title', 'status', 'is_primary', 'updated_at']
```

- [ ] **Step 2: Read existing resumes/views.py**

Read `resumes/views.py` to understand current structure.

- [ ] **Step 3: Add ResumeViewSet + preview-fragment view**

Add to `resumes/views.py`:

```python
from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404, render
from .models import Resume
from .serializers import ResumeSerializer


class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


def resume_preview_fragment(request, resume_id):
    """Returns just the resume content HTML for live preview refresh."""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    template_name = f"resumes/resume_{resume.template_style}.html"
    return render(request, template_name, {'resume': resume})
```

- [ ] **Step 4: Read existing resumes/urls.py**

Read `resumes/urls.py` to see existing URL patterns.

- [ ] **Step 5: Update resumes/urls.py**

Add API router and preview-fragment URL:

```python
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/resumes', views.ResumeViewSet, basename='resume-api')

urlpatterns = [
    # ... existing URLs (keep them) ...
    path('resumes/<int:resume_id>/preview-fragment/', views.resume_preview_fragment, name='resume_preview_fragment'),
] + router.urls
```

**IMPORTANT:** The `preview-fragment/` path must come BEFORE any path that might match `<int:resume_id>` with a trailing slash or similar. If existing URLs already handle `resumes/<int:pk>/` patterns, ensure the new URL is added correctly without conflict.

---

## Task 3: Three resume template files (classic, modern, minimal)

**Files:**
- Create: `templates/resumes/resume_classic.html`
- Create: `templates/resumes/resume_modern.html`
- Create: `templates/resumes/resume_minimal.html`

The existing `templates/resumes/resume_preview.html` is the **source of truth** for the classic template. Copy its structure for `resume_classic.html`.

- [ ] **Step 1: Read existing resume_preview.html**

Read `templates/resumes/resume_preview.html` in full — this is the classic template.

- [ ] **Step 2: Create resume_classic.html**

Create `templates/resumes/resume_classic.html` with the exact same structure as `resume_preview.html`. The only difference: no `<style>` block for print (keep it), no actions bar (that lives in the builder). Keep all the resume content HTML — name, contact info, experience, education, projects, skills sections.

Strip the outer container `<div class="max-w-[850px] mx-auto py-6 px-4">` wrapper and actions bar from the classic template — the preview panel will provide the container. Start from the inner `<div class="bg-white p-8 resume-content">` element.

```html
{% extends 'base.html' %}
{% block title %}{{ resume.title }} - Placement Copilot{% endblock %}

{% block content %}
<div class="max-w-[850px] mx-auto py-6 px-4">
    <div class="bg-white p-8 resume-content" style="font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; font-size: 10.5pt; line-height: 1.4; color: #111;">
        <!-- (copy all content sections from resume_preview.html here) -->
    </div>
</div>
<style>
@media print {
    body { background: white !important; }
    nav { display: none !important; }
}
</style>
{% endblock %}
```

Copy all sections from `resume_preview.html`: Header, section divider, Experience, Education, Projects, Skills. Do not copy the Actions Bar or outer container.

- [ ] **Step 3: Create resume_modern.html**

Create `templates/resumes/resume_modern.html` — clean sans-serif design:

```html
{% extends 'base.html' %}
{% block title %}{{ resume.title }} - Placement Copilot{% endblock %}

{% block content %}
<div class="max-w-[850px] mx-auto py-6 px-4">
    <div class="bg-white p-8" style="font-family: 'Inter', 'Segoe UI', sans-serif; font-size: 10.5pt; line-height: 1.5; color: #1a1a2e;">

        <!-- Header -->
        <div class="mb-6">
            <h1 class="text-3xl font-bold mb-2" style="color: #1e3a8a;">{{ resume.full_name|default:resume.title }}</h1>
            <div class="flex flex-wrap gap-x-4 gap-y-1 text-sm" style="color: #64748b;">
                {% if resume.email %}<span>{{ resume.email }}</span>{% endif %}
                {% if resume.phone %}<span>{{ resume.phone }}</span>{% endif %}
                {% if resume.location %}<span>{{ resume.location }}</span>{% endif %}
                {% if resume.linkedin %}<span>{{ resume.linkedin }}</span>{% endif %}
                {% if resume.github %}<span>{{ resume.github }}</span>{% endif %}
                {% if resume.website %}<span>{{ resume.website }}</span>{% endif %}
            </div>
        </div>

        <!-- Summary -->
        {% if resume.professional_summary %}
        <div class="mb-5 p-4 rounded-lg" style="background-color: #f8fafc; border-left: 4px solid #1e3a8a;">
            <p class="text-sm" style="color: #334155;">{{ resume.professional_summary }}</p>
        </div>
        {% endif %}

        <!-- Experience -->
        {% if resume.experience.all %}
        <section class="mb-5">
            <h2 class="text-sm font-bold tracking-widest mb-3" style="color: #1e3a8a; text-transform: uppercase;">Experience</h2>
            {% for exp in resume.experience.all %}
            <div class="mb-3">
                <div class="flex justify-between items-baseline">
                    <h3 class="font-semibold" style="color: #1e3a8a;">{{ exp.job_title }}</h3>
                    <span class="text-xs" style="color: #94a3b8;">
                        {% if exp.start_date %}{{ exp.start_date|date:"M Y" }}{% endif %}
                        {% if exp.start_date and exp.end_date %} – {% endif %}
                        {% if exp.end_date %}{{ exp.end_date|date:"M Y" }}{% elif exp.is_current %} – Present{% endif %}
                    </span>
                </div>
                <p class="text-sm italic" style="color: #475569;">{{ exp.company }}{% if exp.location %}, {{ exp.location }}{% endif %}</p>
                {% if exp.description %}
                <ul class="mt-1 ml-4 text-sm" style="list-style-type: disc; color: #334155;">
                    {% for line in exp.description.splitlines %}{% if line.strip %}
                    <li>{{ line.strip }}</li>{% endif %}{% endfor %}
                </ul>
                {% endif %}
            </div>
            {% endfor %}
        </section>
        {% endif %}

        <!-- Education -->
        {% if resume.education.all %}
        <section class="mb-5">
            <h2 class="text-sm font-bold tracking-widest mb-3" style="color: #1e3a8a; text-transform: uppercase;">Education</h2>
            {% for edu in resume.education.all %}
            <div class="mb-3">
                <div class="flex justify-between items-baseline">
                    <h3 class="font-semibold" style="color: #1e3a8a;">{{ edu.school }}</h3>
                    <span class="text-xs" style="color: #94a3b8;">
                        {% if edu.start_date %}{{ edu.start_date|date:"Y" }}{% endif %}
                        {% if edu.start_date and edu.end_date %} – {% endif %}
                        {% if edu.end_date %}{{ edu.end_date|date:"Y" }}{% endif %}
                    </span>
                </div>
                <p class="text-sm italic" style="color: #475569;">{{ edu.degree }}{% if edu.field_of_study %} in {{ edu.field_of_study }}{% endif %}{% if edu.gpa %} · GPA: {{ edu.gpa }}{% endif %}</p>
                {% if edu.description %}
                <ul class="mt-1 ml-4 text-sm" style="list-style-type: disc; color: #334155;">
                    {% for line in edu.description.splitlines %}{% if line.strip %}
                    <li>{{ line.strip }}</li>{% endif %}{% endfor %}
                </ul>
                {% endif %}
            </div>
            {% endfor %}
        </section>
        {% endif %}

        <!-- Projects -->
        {% if resume.projects.all %}
        <section class="mb-5">
            <h2 class="text-sm font-bold tracking-widest mb-3" style="color: #1e3a8a; text-transform: uppercase;">Projects</h2>
            {% for project in resume.projects.all %}
            <div class="mb-3">
                <div class="flex justify-between items-baseline">
                    <h3 class="font-semibold" style="color: #1e3a8a;">{{ project.name }}</h3>
                    {% if project.start_date or project.end_date %}
                    <span class="text-xs" style="color: #94a3b8;">
                        {% if project.start_date %}{{ project.start_date|date:"M Y" }}{% endif %}
                        {% if project.start_date and project.end_date %} – {% endif %}
                        {% if project.end_date %}{{ project.end_date|date:"M Y" }}{% endif %}
                    </span>
                    {% endif %}
                </div>
                {% if project.role %}<p class="text-sm italic" style="color: #475569;">{{ project.role }}</p>{% endif %}
                {% if project.url %}<p class="text-xs"><a href="{{ project.url }}" class="text-blue-600" target="_blank">{{ project.url }}</a></p>{% endif %}
                {% if project.description %}
                <ul class="mt-1 ml-4 text-sm" style="list-style-type: disc; color: #334155;">
                    {% for line in project.description.splitlines %}{% if line.strip %}
                    <li>{{ line.strip }}</li>{% endif %}{% endfor %}
                </ul>
                {% endif %}
            </div>
            {% endfor %}
        </section>
        {% endif %}

        <!-- Skills -->
        {% if resume.skills.all %}
        <section class="mb-5">
            <h2 class="text-sm font-bold tracking-widest mb-3" style="color: #1e3a8a; text-transform: uppercase;">Skills</h2>
            <div class="flex flex-wrap gap-2">
                {% for skill in resume.skills.all %}
                <span class="px-3 py-1 rounded-full text-sm" style="background-color: #dbeafe; color: #1e3a8a;">{{ skill.name }}</span>
                {% endfor %}
            </div>
        </section>
        {% endif %}

    </div>
</div>
<style>
@media print {
    body { background: white !important; }
    nav { display: none !important; }
}
</style>
{% endblock %}
```

- [ ] **Step 4: Create resume_minimal.html**

Create `templates/resumes/resume_minimal.html` — maximum whitespace, subtle separators:

```html
{% extends 'base.html' %}
{% block title %}{{ resume.title }} - Placement Copilot{% endblock %}

{% block content %}
<div class="max-w-[850px] mx-auto py-6 px-4">
    <div style="font-family: Georgia, 'Times New Roman', serif; font-size: 11pt; line-height: 1.6; color: #2d2d2d;">

        <!-- Header -->
        <div class="mb-6">
            <h1 class="text-2xl font-normal mb-1">{{ resume.full_name|default:resume.title }}</h1>
            <div class="flex flex-wrap gap-x-3 gap-y-1 text-sm" style="color: #888;">
                {% if resume.email %}<span>{{ resume.email }}</span>{% endif %}
                {% if resume.phone %}<span>{{ resume.phone }}</span>{% endif %}
                {% if resume.location %}<span>{{ resume.location }}</span>{% endif %}
                {% if resume.linkedin %}<span>{{ resume.linkedin }}</span>{% endif %}
                {% if resume.github %}<span>{{ resume.github }}</span>{% endif %}
                {% if resume.website %}<span>{{ resume.website }}</span>{% endif %}
            </div>
        </div>

        <!-- Summary -->
        {% if resume.professional_summary %}
        <div class="mb-5">
            <p class="text-sm" style="color: #555;">{{ resume.professional_summary }}</p>
        </div>
        {% endif %}

        <!-- Experience -->
        {% if resume.experience.all %}
        <section class="mb-5">
            <h2 class="text-xs tracking-widest mb-3" style="text-transform: uppercase; color: #999;">Experience</h2>
            {% for exp in resume.experience.all %}
            <div class="mb-3">
                <div class="flex justify-between items-baseline">
                    <h3 class="text-sm font-medium">{{ exp.job_title }}</h3>
                    <span class="text-xs" style="color: #aaa;">
                        {% if exp.start_date %}{{ exp.start_date|date:"M Y" }}{% endif %}
                        {% if exp.start_date and exp.end_date %} – {% endif %}
                        {% if exp.end_date %}{{ exp.end_date|date:"M Y" }}{% elif exp.is_current %} – Present{% endif %}
                    </span>
                </div>
                <p class="text-sm" style="color: #666;">{{ exp.company }}{% if exp.location %}, {{ exp.location }}{% endif %}</p>
                {% if exp.description %}
                <ul class="mt-1 ml-4 text-sm" style="list-style-type: disc; color: #555;">
                    {% for line in exp.description.splitlines %}{% if line.strip %}
                    <li>{{ line.strip }}</li>{% endif %}{% endfor %}
                </ul>
                {% endif %}
            </div>
            {% endfor %}
        </section>
        {% endif %}

        <!-- Education -->
        {% if resume.education.all %}
        <section class="mb-5">
            <h2 class="text-xs tracking-widest mb-3" style="text-transform: uppercase; color: #999;">Education</h2>
            {% for edu in resume.education.all %}
            <div class="mb-3">
                <div class="flex justify-between items-baseline">
                    <h3 class="text-sm font-medium">{{ edu.school }}</h3>
                    <span class="text-xs" style="color: #aaa;">
                        {% if edu.start_date %}{{ edu.start_date|date:"Y" }}{% endif %}
                        {% if edu.start_date and edu.end_date %} – {% endif %}
                        {% if edu.end_date %}{{ edu.end_date|date:"Y" }}{% endif %}
                    </span>
                </div>
                <p class="text-sm" style="color: #666;">{{ edu.degree }}{% if edu.field_of_study %} in {{ edu.field_of_study }}{% endif %}{% if edu.gpa %} · GPA: {{ edu.gpa }}{% endif %}</p>
            </div>
            {% endfor %}
        </section>
        {% endif %}

        <!-- Projects -->
        {% if resume.projects.all %}
        <section class="mb-5">
            <h2 class="text-xs tracking-widest mb-3" style="text-transform: uppercase; color: #999;">Projects</h2>
            {% for project in resume.projects.all %}
            <div class="mb-2">
                <div class="flex justify-between items-baseline">
                    <h3 class="text-sm font-medium">{{ project.name }}</h3>
                    {% if project.start_date or project.end_date %}
                    <span class="text-xs" style="color: #aaa;">
                        {% if project.start_date %}{{ project.start_date|date:"M Y" }}{% endif %}
                        {% if project.start_date and project.end_date %} – {% endif %}
                        {% if project.end_date %}{{ project.end_date|date:"M Y" }}{% endif %}
                    </span>
                    {% endif %}
                </div>
                {% if project.role %}<p class="text-sm" style="color: #666;">{{ project.role }}</p>{% endif %}
                {% if project.description %}
                <ul class="mt-1 ml-4 text-sm" style="list-style-type: disc; color: #555;">
                    {% for line in project.description.splitlines %}{% if line.strip %}
                    <li>{{ line.strip }}</li>{% endif %}{% endfor %}
                </ul>
                {% endif %}
            </div>
            {% endfor %}
        </section>
        {% endif %}

        <!-- Skills -->
        {% if resume.skills.all %}
        <section class="mb-5">
            <h2 class="text-xs tracking-widest mb-3" style="text-transform: uppercase; color: #999;">Skills</h2>
            <p class="text-sm" style="color: #555;">
                {% for skill in resume.skills.all %}{{ skill.name }}{% if not forloop.last %}, {% endif %}{% endfor %}
            </p>
        </section>
        {% endif %}

    </div>
</div>
<style>
@media print {
    body { background: white !important; }
    nav { display: none !important; }
}
</style>
{% endblock %}
```

---

## Task 4: Two-panel builder layout template

**Files:**
- Create: `templates/resumes/resume_builder.html`

This replaces the existing `resume_update.html`. The builder has a top bar (progress + template switcher), left panel (form with collapsible sections), right panel (live preview, sticky).

- [ ] **Step 1: Read existing resume_update.html**

Read `templates/resumes/resume_update.html` to understand current form field structure — you need to extract all field names and structure to build the builder form.

- [ ] **Step 2: Read resumes/forms.py**

Read `resumes/forms.py` to understand how form fields are organized. This determines which fields go in which collapsible section.

- [ ] **Step 3: Read resumes/models.py**

Read `resumes/models.py` to get all field names for the form.

- [ ] **Step 4: Read base.html**

Read `templates/base.html` to understand the nav structure (for understanding the page height available).

- [ ] **Step 5: Create resume_builder.html**

Create `templates/resumes/resume_builder.html`. This is the core UI file. Structure:

```html
{% extends 'base.html' %}
{% block title %}Edit {{ resume.title }} - Placement Copilot{% endblock %}

{% block content %}
<input type="hidden" id="resume-id" value="{{ resume.id }}">

<div class="flex flex-col h-[calc(100vh-64px)]">
    <!-- Top Bar -->
    <div class="bg-white border-b px-6 py-3 flex items-center justify-between">
        <div class="flex items-center gap-4">
            <div class="w-48 bg-gray-200 rounded-full h-2">
                <div id="progress-bar" class="bg-blue-600 h-2 rounded-full transition-all" style="width: {{ progress_pct }}%"></div>
            </div>
            <span id="progress-text" class="text-sm text-gray-600">{{ progress_text }}</span>
        </div>
        <div id="template-switcher" class="flex gap-1 hidden md:flex">
            <button class="px-3 py-1 text-sm rounded template-btn {% if resume.template_style == 'classic' %}bg-blue-600 text-white{% else %}text-gray-600 hover:bg-gray-100{% endif %}" data-template="classic">Classic</button>
            <button class="px-3 py-1 text-sm rounded template-btn {% if resume.template_style == 'modern' %}bg-blue-600 text-white{% else %}text-gray-600 hover:bg-gray-100{% endif %}" data-template="modern">Modern</button>
            <button class="px-3 py-1 text-sm rounded template-btn {% if resume.template_style == 'minimal' %}bg-blue-600 text-white{% else %}text-gray-600 hover:bg-gray-100{% endif %}" data-template="minimal">Minimal</button>
        </div>
    </div>

    <!-- Main: Form + Preview -->
    <div class="flex flex-1 overflow-hidden">
        <!-- Left: Form (scrollable) -->
        <div class="w-full md:w-[55%] overflow-y-auto px-6 py-4 space-y-4">
            <form id="resume-form" method="POST" class="space-y-4">
                {% csrf_token %}

                <!-- Section 1: Personal Information (expanded) -->
                <div class="bg-white rounded-lg shadow-sm">
                    <div class="section-header flex justify-between items-center p-4 cursor-pointer">
                        <h2 class="text-lg font-semibold text-gray-800">Personal Information</h2>
                        <svg class="w-5 h-5 text-gray-400 transform transition-transform section-chevron" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                    </div>
                    <div class="section-content px-4 pb-4 space-y-3">
                        {{ resume_form.as_p }}
                    </div>
                </div>

                <!-- Section 2: Professional Summary (expanded) -->
                <div class="bg-white rounded-lg shadow-sm">
                    <div class="section-header flex justify-between items-center p-4 cursor-pointer">
                        <h2 class="text-lg font-semibold text-gray-800">Professional Summary</h2>
                        <svg class="w-5 h-5 text-gray-400 transform transition-transform section-chevron" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                    </div>
                    <div class="section-content px-4 pb-4 space-y-3">
                        <div>
                            <label for="id_professional_summary" class="block text-sm font-medium text-gray-700 mb-1">Summary</label>
                            <textarea name="professional_summary" id="id_professional_summary" rows="3" maxlength="500"
                                class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Brief overview of your skills and career goals...">{{ resume.professional_summary|default:'' }}</textarea>
                            <p class="text-xs text-gray-500 mt-1"><span id="summary-chars">0</span>/500 characters</p>
                        </div>
                    </div>
                </div>

                <!-- Section 3: Experience -->
                <div class="bg-white rounded-lg shadow-sm">
                    <div class="section-header flex justify-between items-center p-4 cursor-pointer">
                        <h2 class="text-lg font-semibold text-gray-800">Experience</h2>
                        <svg class="w-5 h-5 text-gray-400 transform transition-transform section-chevron" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                    </div>
                    <div class="section-content px-4 pb-4 space-y-3" id="experience-entries">
                        {% if resume.experience.all %}
                            {% for exp in resume.experience.all %}
                            <!-- Existing entry card -->
                            {% endfor %}
                        {% else %}
                            <p class="text-sm text-gray-400 py-2">No experience entries yet. Click 'Add Experience' below.</p>
                        {% endif %}
                    </div>
                    <div class="px-4 pb-4">
                        <button type="button" class="text-sm text-blue-600 hover:text-blue-700 add-entry-btn" data-section="experience">+ Add Experience</button>
                    </div>
                </div>

                <!-- Section 4: Education -->
                <div class="bg-white rounded-lg shadow-sm">
                    <div class="section-header flex justify-between items-center p-4 cursor-pointer">
                        <h2 class="text-lg font-semibold text-gray-800">Education</h2>
                        <svg class="w-5 h-5 text-gray-400 transform transition-transform section-chevron" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                    </div>
                    <div class="section-content px-4 pb-4 space-y-3" id="education-entries">
                        {% if resume.education.all %}
                            {% for edu in resume.education.all %}
                            <!-- Existing entry card -->
                            {% endfor %}
                        {% else %}
                            <p class="text-sm text-gray-400 py-2">No education entries yet. Click 'Add Education' below.</p>
                        {% endif %}
                    </div>
                    <div class="px-4 pb-4">
                        <button type="button" class="text-sm text-blue-600 hover:text-blue-700 add-entry-btn" data-section="education">+ Add Education</button>
                    </div>
                </div>

                <!-- Section 5: Projects -->
                <div class="bg-white rounded-lg shadow-sm">
                    <div class="section-header flex justify-between items-center p-4 cursor-pointer">
                        <h2 class="text-lg font-semibold text-gray-800">Projects</h2>
                        <svg class="w-5 h-5 text-gray-400 transform transition-transform section-chevron" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                    </div>
                    <div class="section-content px-4 pb-4 space-y-3" id="project-entries">
                        {% if resume.projects.all %}
                            {% for project in resume.projects.all %}
                            <!-- Existing entry card -->
                            {% endfor %}
                        {% else %}
                            <p class="text-sm text-gray-400 py-2">No project entries yet. Click 'Add Project' below.</p>
                        {% endif %}
                    </div>
                    <div class="px-4 pb-4">
                        <button type="button" class="text-sm text-blue-600 hover:text-blue-700 add-entry-btn" data-section="project">+ Add Project</button>
                    </div>
                </div>

                <!-- Section 6: Skills -->
                <div class="bg-white rounded-lg shadow-sm">
                    <div class="section-header flex justify-between items-center p-4 cursor-pointer">
                        <h2 class="text-lg font-semibold text-gray-800">Skills</h2>
                        <svg class="w-5 h-5 text-gray-400 transform transition-transform section-chevron" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                    </div>
                    <div class="section-content px-4 pb-4 space-y-3" id="skill-entries">
                        {% if resume.skills.all %}
                            {% for skill in resume.skills.all %}
                            <!-- Existing skill tag -->
                            {% endfor %}
                        {% else %}
                            <p class="text-sm text-gray-400 py-2">No skills added yet. Click 'Add Skill' below.</p>
                        {% endif %}
                    </div>
                    <div class="px-4 pb-4">
                        <button type="button" class="text-sm text-blue-600 hover:text-blue-700 add-entry-btn" data-section="skill">+ Add Skill</button>
                    </div>
                </div>

            </form>
        </div>

        <!-- Right: Live Preview (sticky) -->
        <div id="preview-panel" class="hidden md:block md:w-[45%] bg-gray-100 overflow-y-auto p-6 border-l">
            <!-- Preview loads here via JS -->
        </div>
    </div>
</div>

<!-- Toast container -->
<div id="toast-container" class="fixed bottom-4 right-4 space-y-2"></div>
{% endblock %}
```

- [ ] **Step 6: Add CSS for crispy forms**

Read `resumes/forms.py` to check if it uses Django crispy forms. If yes, make sure `{% load crispy_forms_tags %}` is in the template and use `{{ resume_form|crispy }}` for the personal info section, or render fields individually. If not using crispy, style fields manually with Tailwind classes as shown above.

- [ ] **Step 7: Add inline JavaScript for section collapse/expand**

Add inside a `<script>` block at the bottom of the template body (before `{% endblock %}`):

```javascript
// Section collapse/expand
document.querySelectorAll('.section-header').forEach(header => {
    header.addEventListener('click', () => {
        const content = header.nextElementSibling;
        content.classList.toggle('hidden');
        header.classList.toggle('bg-gray-50');
        const chevron = header.querySelector('.section-chevron');
        if (chevron) chevron.classList.toggle('rotate-180');
    });
});

// Initial preview load
(function() {
    const resumeId = document.getElementById('resume-id').value;
    fetch(`/resumes/${resumeId}/preview-fragment/`)
        .then(r => r.text())
        .then(html => {
            document.getElementById('preview-panel').innerHTML = html;
        });
})();
```

---

## Task 5: Live Preview + Auto-Save + Progress Indicator JavaScript

**Files:**
- Modify: `templates/resumes/resume_builder.html` (add JavaScript to the script block)

Add to the `<script>` block in `resume_builder.html` (after the section collapse code):

- [ ] **Step 1: Add getCookie helper**

```javascript
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
```

- [ ] **Step 2: Add Toast helper**

```javascript
function showToast(message, type) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    const colors = {
        success: 'bg-green-100 border-green-400 text-green-800',
        error: 'bg-red-100 border-red-400 text-red-800',
        info: 'bg-blue-100 border-blue-400 text-blue-800',
    };
    toast.className = `px-4 py-3 rounded border shadow-sm text-sm ${colors[type] || colors.info}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), type === 'success' ? 2000 : 4000);
}
```

- [ ] **Step 3: Add Progress Indicator**

```javascript
const sections = {
    personal: () => {
        const el = document.getElementById('id_full_name');
        return el && el.value.trim() !== '';
    },
    education: () => document.querySelectorAll('#education-entries .entry-card').length > 0,
    experience: () => document.querySelectorAll('#experience-entries .entry-card').length > 0,
    projects: () => document.querySelectorAll('#project-entries .entry-card').length > 0,
    skills: () => document.querySelectorAll('#skill-entries .skill-tag').length > 0,
};

function updateProgress() {
    const complete = Object.values(sections).filter(s => s()).length;
    const pct = (complete / 5) * 100;
    const bar = document.getElementById('progress-bar');
    if (bar) bar.style.width = pct + '%';
    const text = document.getElementById('progress-text');
    if (text) text.textContent = `${complete} of 5 sections complete`;
}

// Run on page load
updateProgress();
```

- [ ] **Step 4: Add Live Preview (300ms debounce)**

```javascript
let previewTimeout;

document.addEventListener('input', function(e) {
    if (e.target.matches('input, textarea, select')) {
        clearTimeout(previewTimeout);
        previewTimeout = setTimeout(updatePreview, 300);
        updateProgress();
        scheduleAutoSave();
    }
});

function updatePreview() {
    const resumeId = document.getElementById('resume-id').value;
    fetch(`/resumes/${resumeId}/preview-fragment/`)
        .then(r => r.text())
        .then(html => {
            document.getElementById('preview-panel').innerHTML = html;
        })
        .catch(() => {
            // Silently fail preview updates — don't interrupt typing
        });
}
```

- [ ] **Step 5: Add Auto-Save (30s debounce, with retry)**

```javascript
let saveTimeout;
let isDirty = false;

function scheduleAutoSave() {
    isDirty = true;
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(autoSave, 30000);
}

function autoSave() {
    if (!isDirty) return;
    showToast('Saving...', 'info');

    const form = document.getElementById('resume-form');
    const formData = new FormData(form);
    const resumeId = document.getElementById('resume-id').value;

    // Build JSON from form data
    const data = {};
    formData.forEach((value, key) => {
        if (key !== 'csrfmiddlewaretoken') data[key] = value;
    });

    fetch(`/api/resumes/${resumeId}/`, {
        method: 'PATCH',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(r => r.ok ? r.json() : Promise.reject())
    .then(data => {
        showToast('Saved', 'success');
        isDirty = false;
    })
    .catch(() => {
        showToast('Save failed. Retrying...', 'error');
        setTimeout(autoSave, 5000);
    });
}
```

- [ ] **Step 6: Add Template Switching**

```javascript
document.querySelectorAll('.template-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const template = this.dataset.template;
        const resumeId = document.getElementById('resume-id').value;

        // Save preference via API
        fetch(`/api/resumes/${resumeId}/`, {
            method: 'PATCH',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ template_style: template }),
        }).then(() => {
            // Update preview immediately
            updatePreview();
        });

        // Update active button style
        document.querySelectorAll('.template-btn').forEach(b => {
            b.classList.remove('bg-blue-600', 'text-white');
            b.classList.add('text-gray-600', 'hover:bg-gray-100');
        });
        this.classList.remove('text-gray-600', 'hover:bg-gray-100');
        this.classList.add('bg-blue-600', 'text-white');
    });
});
```

- [ ] **Step 7: Add Summary Character Counter**

```javascript
const summaryField = document.getElementById('id_professional_summary');
const summaryChars = document.getElementById('summary-chars');
if (summaryField && summaryChars) {
    summaryChars.textContent = summaryField.value.length;
    summaryField.addEventListener('input', () => {
        summaryChars.textContent = summaryField.value.length;
    });
}
```

- [ ] **Step 8: Add Professional Summary to form data**

The professional summary field must have `name="professional_summary"` in the form. Verify this matches what you created in Task 4 Step 5. The auto-save PATCH call sends it as part of `formData`.

---

## Task 6: Entry management (add/delete Experience, Education, Projects, Skills)

**Files:**
- Modify: `templates/resumes/resume_builder.html` (add entry card HTML + JS)

- [ ] **Step 1: Add inline entry templates**

Add empty hidden templates at the bottom of the template (inside a `<script type="text/template">` block or as JS strings):

```javascript
const entryTemplates = {
    experience: `
        <div class="entry-card bg-gray-50 rounded-lg p-3 border">
            <div class="flex justify-between items-center mb-2">
                <span class="entry-title text-sm font-medium text-gray-700">New Experience</span>
                <button type="button" class="text-red-500 text-xs hover:text-red-700 delete-entry">Delete</button>
            </div>
            <div class="space-y-2">
                <input type="text" name="experience_job_title" placeholder="Job Title" class="w-full px-3 py-1.5 border rounded text-sm">
                <input type="text" name="experience_company" placeholder="Company" class="w-full px-3 py-1.5 border rounded text-sm">
                <input type="text" name="experience_location" placeholder="Location" class="w-full px-3 py-1.5 border rounded text-sm">
                <div class="flex gap-2">
                    <input type="text" name="experience_start_date" placeholder="Start (MM/YYYY)" class="w-1/2 px-3 py-1.5 border rounded text-sm">
                    <input type="text" name="experience_end_date" placeholder="End (MM/YYYY)" class="w-1/2 px-3 py-1.5 border rounded text-sm">
                </div>
                <label class="flex items-center gap-2 text-sm">
                    <input type="checkbox" name="experience_is_current" class="rounded"> Currently working here
                </label>
                <textarea name="experience_description" rows="3" placeholder="Description (one bullet per line)" class="w-full px-3 py-1.5 border rounded text-sm"></textarea>
            </div>
        </div>
    `,
    education: `
        <div class="entry-card bg-gray-50 rounded-lg p-3 border">
            <div class="flex justify-between items-center mb-2">
                <span class="entry-title text-sm font-medium text-gray-700">New Education</span>
                <button type="button" class="text-red-500 text-xs hover:text-red-700 delete-entry">Delete</button>
            </div>
            <div class="space-y-2">
                <input type="text" name="education_school" placeholder="School/University" class="w-full px-3 py-1.5 border rounded text-sm">
                <input type="text" name="education_degree" placeholder="Degree (e.g. B.S.)" class="w-full px-3 py-1.5 border rounded text-sm">
                <input type="text" name="education_field_of_study" placeholder="Field of Study" class="w-full px-3 py-1.5 border rounded text-sm">
                <div class="flex gap-2">
                    <input type="text" name="education_start_date" placeholder="Start Year" class="w-1/2 px-3 py-1.5 border rounded text-sm">
                    <input type="text" name="education_end_date" placeholder="End Year" class="w-1/2 px-3 py-1.5 border rounded text-sm">
                </div>
                <input type="text" name="education_gpa" placeholder="GPA (optional)" class="w-full px-3 py-1.5 border rounded text-sm">
            </div>
        </div>
    `,
    project: `
        <div class="entry-card bg-gray-50 rounded-lg p-3 border">
            <div class="flex justify-between items-center mb-2">
                <span class="entry-title text-sm font-medium text-gray-700">New Project</span>
                <button type="button" class="text-red-500 text-xs hover:text-red-700 delete-entry">Delete</button>
            </div>
            <div class="space-y-2">
                <input type="text" name="project_name" placeholder="Project Name" class="w-full px-3 py-1.5 border rounded text-sm">
                <input type="text" name="project_role" placeholder="Your Role (optional)" class="w-full px-3 py-1.5 border rounded text-sm">
                <input type="url" name="project_url" placeholder="URL (optional)" class="w-full px-3 py-1.5 border rounded text-sm">
                <div class="flex gap-2">
                    <input type="text" name="project_start_date" placeholder="Start" class="w-1/2 px-3 py-1.5 border rounded text-sm">
                    <input type="text" name="project_end_date" placeholder="End" class="w-1/2 px-3 py-1.5 border rounded text-sm">
                </div>
                <textarea name="project_description" rows="3" placeholder="Description" class="w-full px-3 py-1.5 border rounded text-sm"></textarea>
            </div>
        </div>
    `,
    skill: `
        <div class="entry-card skill-tag bg-blue-50 rounded px-2 py-1 flex items-center justify-between">
            <span class="text-sm text-blue-800">New Skill</span>
            <button type="button" class="text-red-500 hover:text-red-700 delete-entry ml-2">×</button>
            <input type="hidden" name="skill_name" value="">
        </div>
    `,
};
```

- [ ] **Step 2: Add "Add Entry" button JS**

Add to the `<script>` block:

```javascript
document.querySelectorAll('.add-entry-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const section = this.dataset.section;
        const container = document.getElementById(section + '-entries');
        const emptyMsg = container.querySelector('p.text-gray-400');
        if (emptyMsg) emptyMsg.remove();

        const wrapper = document.createElement('div');
        wrapper.innerHTML = entryTemplates[section];
        const card = wrapper.firstElementChild;
        container.appendChild(card);

        // For skill section, make it inline-editable
        if (section === 'skill') {
            const input = card.querySelector('input[name="skill_name"]');
            const span = card.querySelector('span');
            const skillInput = document.createElement('input');
            skillInput.type = 'text';
            skillInput.className = 'text-sm text-blue-800 bg-transparent border-none outline-none w-full';
            skillInput.value = '';
            skillInput.placeholder = 'Skill name';
            span.replaceWith(skillInput);
            skillInput.focus();
            skillInput.addEventListener('change', () => {
                input.value = skillInput.value;
                skillInput.replaceWith(Object.assign(document.createElement('span'), {textContent: skillInput.value || 'New Skill', className: 'text-sm text-blue-800'}));
            });
        }

        // Delete handler
        card.querySelector('.delete-entry').addEventListener('click', () => {
            card.remove();
            updateProgress();
        });

        updateProgress();
    });
});
```

- [ ] **Step 3: Add existing entry render in template**

In `resume_builder.html`, for each section (experience, education, projects, skills), add `{% for %}` loops that render existing entries using the same HTML structure as the templates above. Read the existing model fields to know what attributes each model has (job_title, company, location, start_date, end_date, description for Experience, etc.). Add inline edit capability (collapsible entry cards) matching the template structure.

---

## Task 7: Wire up the builder view + update URLs

**Files:**
- Modify: `resumes/views.py` (add builder view that renders resume_builder.html)
- Modify: `resumes/urls.py` (update resume_update URL to point to new builder)
- Modify: `resumes/admin.py` (register new fields)

- [ ] **Step 1: Add builder view to views.py**

Add to `resumes/views.py`:

```python
def resume_builder(request, resume_id):
    """Two-panel resume builder."""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    from .forms import ResumeForm
    resume_form = ResumeForm(instance=resume)

    # Compute progress
    sections = {
        'personal': bool(resume.full_name and resume.email),
        'education': resume.education.exists(),
        'experience': resume.experience.exists(),
        'projects': resume.projects.exists(),
        'skills': resume.skills.exists(),
    }
    complete = sum(sections.values())
    progress_pct = int((complete / 5) * 100)
    progress_text = f"{complete} of 5 sections complete"

    context = {
        'resume': resume,
        'resume_form': resume_form,
        'progress_pct': progress_pct,
        'progress_text': progress_text,
    }
    return render(request, 'resumes/resume_builder.html', context)
```

- [ ] **Step 2: Read existing resumes/urls.py**

Read `resumes/urls.py`.

- [ ] **Step 3: Update resume_update URL**

Find the existing `resume_update` URL and change its `view` to point to `views.resume_builder` (keep the same URL pattern and name `resume_update` — this preserves all existing links).

The URL pattern should look like:
```python
path('resumes/<int:resume_id>/edit/', views.resume_builder, name='resume_update'),
```

- [ ] **Step 4: Read resumes/admin.py**

Read `resumes/admin.py`.

- [ ] **Step 5: Register new fields in admin**

Add `professional_summary`, `template_style`, and `status` to the Resume admin `list_display` and/or `list_filter` as appropriate.

---

## Task 8: Tests

**Files:**
- Modify: `resumes/tests.py`

- [ ] **Step 1: Read existing resumes/tests.py**

Read `resumes/tests.py` to understand current test structure.

- [ ] **Step 2: Add ResumeAPITests class**

Add after existing tests:

```python
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from resumes.models import Resume


class ResumeAPITests(TestCase):
    """Tests for Resume REST API"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_patch_resume_updates_fields(self):
        response = self.client.patch(
            reverse('resume-api-detail', args=[self.resume.id]),
            data=json.dumps({'title': 'Updated Title', 'full_name': 'John Doe'}),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value,
        )
        self.assertEqual(response.status_code, 200)
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.title, 'Updated Title')
        self.assertEqual(self.resume.full_name, 'John Doe')

    def test_patch_template_style(self):
        response = self.client.patch(
            reverse('resume-api-detail', args=[self.resume.id]),
            data=json.dumps({'template_style': 'modern'}),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value,
        )
        self.assertEqual(response.status_code, 200)
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.template_style, 'modern')

    def test_preview_fragment_returns_html(self):
        response = self.client.get(reverse('resume_preview_fragment', args=[self.resume.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['Content-Type'])

    def test_cannot_access_other_user_resume_via_api(self):
        other = User.objects.create_user('other', 'other@example.com', 'pass123')
        other_resume = Resume.objects.create(user=other, title='Other')
        response = self.client.get(reverse('resume-api-detail', args=[other_resume.id]))
        self.assertEqual(response.status_code, 404)
```

- [ ] **Step 3: Add ResumeBuilderTests class**

```python
class ResumeBuilderTests(TestCase):
    """Tests for the two-panel resume builder."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('builderuser', 'builder@example.com', 'builderpass123')
        self.client.login(username='builderuser', password='builderpass123')
        self.resume = Resume.objects.create(user=self.user, title='Builder Test')

    def test_builder_page_loads(self):
        response = self.client.get(reverse('resume_update', args=[self.resume.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'resume-form')
        self.assertContains(response, 'preview-panel')
        self.assertContains(response, 'template-switcher')

    def test_progress_bar_shown(self):
        response = self.client.get(reverse('resume_update', args=[self.resume.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'progress-bar')

    def test_template_switcher_buttons(self):
        response = self.client.get(reverse('resume_update', args=[self.resume.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Classic')
        self.assertContains(response, 'Modern')
        self.assertContains(response, 'Minimal')

    def test_preview_fragment_loads(self):
        response = self.client.get(reverse('resume_preview_fragment', args=[self.resume.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['Content-Type'])

    def test_computed_status_property(self):
        self.assertEqual(self.resume.computed_status, 'draft')
        self.resume.full_name = 'Jane Doe'
        self.resume.email = 'jane@example.com'
        self.resume.save()
        self.assertEqual(self.resume.computed_status, 'draft')  # still draft (no entries)
        from resumes.models import ResumeEducation
        ResumeEducation.objects.create(resume=self.resume, school='MIT', degree='BS')
        self.assertEqual(self.resume.computed_status, 'complete')
```

- [ ] **Step 4: Run tests**

Run: `cd d:/EliteSttack && python manage.py test resumes --verbosity=2`

Expected: All tests pass. If tests fail, fix the implementation and re-run.

---

## Task 9: Verify full integration

**Files:** All — integration check

- [ ] **Step 1: Check server starts**

Run: `python manage.py check`

Expected: No errors.

- [ ] **Step 2: Check URL routing**

Run: `python manage.py show_urls | grep resume`

Expected output shows:
- `api/resumes/` with ViewSet URLs
- `resumes/<id>/preview-fragment/` pointing to `resume_preview_fragment`
- `resumes/<id>/edit/` pointing to `resume_builder`

- [ ] **Step 3: Verify all template files exist**

Check that all 4 template files exist:
- `templates/resumes/resume_builder.html`
- `templates/resumes/resume_classic.html`
- `templates/resumes/resume_modern.html`
- `templates/resumes/resume_minimal.html`

- [ ] **Step 4: Manual smoke test (if dev server can be started)**

Try starting the dev server and check that the builder page loads without errors.
