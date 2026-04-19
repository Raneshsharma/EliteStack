---
name: P0.2 Resume Builder Design
description: Two-panel resume builder with live preview, auto-save, progress indicators, and 3 template styles
type: project
---

# P0.2 Resume Builder — Implementation Design

**Date:** 2026-04-18
**Epic:** P0.2 Resume Builder
**Stack:** Django 4.2, djangorestframework, Tailwind, vanilla JS

---

## 1. Model Changes

### `resumes/models.py` — Three new fields on Resume

Add after existing fields:

```python
professional_summary = models.TextField(max_length=500, blank=True)
template_style = models.CharField(max_length=20, default='classic')  # classic | modern | minimal
status = models.CharField(max_length=20, default='draft')  # draft | complete
```

**Status logic (computed property on model):**
```python
@property
def computed_status(self):
    has_personal = bool(self.full_name and self.email)
    has_entries = self.education.exists() or self.experience.exists()
    return 'complete' if (has_personal and has_entries) else 'draft'
```

---

## 2. REST API

### `requirements.txt` — Add dependency

```
djangorestframework
```

### `resumes/serializers.py` — New file

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

### `resumes/views.py` — Add ViewSet

```python
from rest_framework import viewsets, permissions
from .models import Resume
from .serializers import ResumeSerializer


class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
```

### `resumes/urls.py` — Add API router

```python
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/resumes', views.ResumeViewSet, basename='resume-api')

urlpatterns = [
    # ... existing URLs ...
    path('resumes/<int:resume_id>/preview-fragment/', views.resume_preview_fragment, name='resume_preview_fragment'),
] + router.urls
```

### `resumes/views.py` — Add preview fragment view

```python
def resume_preview_fragment(request, resume_id):
    """Returns just the resume content HTML for live preview refresh."""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    template_name = f"resumes/resume_{resume.template_style}.html"
    return render(request, template_name, {'resume': resume})
```

---

## 3. Resume Template Files

### `templates/resumes/resume_classic.html`

Copy of existing `resume_preview.html` — serif fonts, traditional layout, section headers with blue border. This is the default.

### `templates/resumes/resume_modern.html` — New

Clean sans-serif design with accent color headers, strong visual hierarchy. Uses `Inter` or `Segoe UI`. Different header treatment (no all-caps), colored section dividers.

### `templates/resumes/resume_minimal.html` — New

Maximum whitespace, simple typography, no decorative elements. Uses system fonts. Subtle separators instead of borders.

### Shared structure

All three templates share the same Django template structure:
- Header: name (uppercase), contact info line
- Sections loop: education, experience, projects, skills
- Each section uses the same `{% if resume.X.all %}` guards
- Skills rendered as chips/tags in modern/minimal, comma-separated in classic

### Preview fragment

The `resume_preview_fragment` view renders the correct template based on `resume.template_style`. JavaScript fetches this on every preview refresh.

---

## 4. Two-Panel Builder Layout

### `templates/resumes/resume_builder.html` — Replaces `resume_update.html`

```html
{% extends 'base.html' %}
{% block title %}Edit {{ resume.title }} - Placement Copilot{% endblock %}

{% block content %}
<div class="flex flex-col h-[calc(100vh-64px)]">
    <!-- Top Bar: Progress + Template Switcher -->
    <div class="bg-white border-b px-6 py-3 flex items-center justify-between">
        <div class="flex items-center gap-4">
            <div class="w-48 bg-gray-200 rounded-full h-2">
                <div id="progress-bar" class="bg-blue-600 h-2 rounded-full transition-all" style="width: 0%"></div>
            </div>
            <span id="progress-text" class="text-sm text-gray-600">0 of 5 sections complete</span>
        </div>
        <div id="template-switcher" class="flex gap-1 hidden md:flex">
            <button class="px-3 py-1 text-sm rounded template-btn" data-template="classic">Classic</button>
            <button class="px-3 py-1 text-sm rounded template-btn" data-template="modern">Modern</button>
            <button class="px-3 py-1 text-sm rounded template-btn" data-template="minimal">Minimal</button>
        </div>
    </div>

    <!-- Main: Form + Preview -->
    <div class="flex flex-1 overflow-hidden">
        <!-- Left: Form (scrollable) -->
        <div class="w-full md:w-[55%] overflow-y-auto px-6 py-4 space-y-6">
            <form id="resume-form" method="POST" class="space-y-6">
                {% csrf_token %}
                <!-- Collapsible sections... -->
            </form>
        </div>

        <!-- Right: Live Preview (sticky) -->
        <div id="preview-panel" class="hidden md:block md:w-[45%] bg-gray-100 overflow-y-auto p-6 border-l">
            <!-- Resume preview renders here -->
        </div>
    </div>
</div>

<!-- Toast container -->
<div id="toast-container" class="fixed bottom-4 right-4 space-y-2"></div>
{% endblock %}
```

### Section structure (each section is collapsible)

```html
<div class="bg-white rounded-lg shadow-md">
    <div class="section-header flex justify-between items-center p-4 cursor-pointer">
        <h2 class="text-xl font-semibold">Personal Information</h2>
        <span class="text-gray-400 section-status">Complete</span>
    </div>
    <div class="section-content p-4 space-y-4">
        <!-- Fields here -->
    </div>
</div>
```

Empty state for multi-entry sections: "No entries yet. Click 'Add' to get started."

### Mobile behavior

On `<768px`:
- Preview panel hidden by default
- "Preview" button in top bar opens preview in new view/modal
- Template switcher hidden (template selector on full preview page instead)

---

## 5. Live Preview JavaScript

### Preview refresh (300ms debounce)

```javascript
let previewTimeout;

document.addEventListener('input', function(e) {
    if (e.target.matches('input, textarea, select')) {
        clearTimeout(previewTimeout);
        previewTimeout = setTimeout(updatePreview, 300);
        updateProgress(); // Also update progress indicator
    }
});

function updatePreview() {
    const resumeId = document.getElementById('resume-id').value;
    fetch(`/resumes/${resumeId}/preview-fragment/`)
        .then(r => r.text())
        .then(html => {
            document.getElementById('preview-panel').innerHTML = html;
        });
}
```

### Template switching

```javascript
document.querySelectorAll('.template-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const template = this.dataset.template;
        // Save preference
        fetch(`/api/resumes/${resumeId}/`, {
            method: 'PATCH',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ template_style: template }),
        });
        // Update preview
        updatePreview();
        // Update active button style
        document.querySelectorAll('.template-btn').forEach(b => b.classList.remove('bg-blue-600', 'text-white'));
        this.classList.add('bg-blue-600', 'text-white');
    });
});
```

---

## 6. Auto-Save JavaScript

### Auto-save (30s debounce, with retry)

```javascript
let saveTimeout;
let isDirty = false;

document.addEventListener('input', function(e) {
    if (e.target.matches('input, textarea, select')) {
        isDirty = true;
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(autoSave, 30000);
    }
});

function autoSave() {
    if (!isDirty) return;
    showToast('Saving...', 'info');

    const formData = new FormData(document.getElementById('resume-form'));
    fetch(`/api/resumes/${resumeId}/`, {
        method: 'PATCH',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(Object.fromEntries(formData)),
    })
    .then(r => r.ok ? r.json() : Promise.reject())
    .then(data => {
        showToast('Saved', 'success');
        isDirty = false;
        // Update status badge
        if (data.status) {
            document.getElementById('status-badge').textContent = data.status;
        }
    })
    .catch(() => {
        showToast('Save failed. Retrying...', 'error');
        setTimeout(autoSave, 5000); // retry in 5s
    });
}
```

### Toast helper

```javascript
function showToast(message, type) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    const colors = {
        success: 'bg-green-100 border-green-400 text-green-800',
        error: 'bg-red-100 border-red-400 text-red-800',
        info: 'bg-blue-100 border-blue-400 text-blue-800',
    };
    toast.className = `px-4 py-3 rounded border ${colors[type] || colors.info}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), type === 'success' ? 2000 : 4000);
}
```

---

## 7. Progress Indicator

```javascript
const sections = {
    personal: () => document.getElementById('id_full_name').value.trim() !== '',
    education: () => document.querySelectorAll('#education-entries .entry-row').length > 0,
    experience: () => document.querySelectorAll('#experience-entries .entry-row').length > 0,
    projects: () => document.querySelectorAll('#project-entries .entry-row').length > 0,
    skills: () => document.querySelectorAll('#skill-entries .entry-row').length > 0,
};

function updateProgress() {
    const complete = Object.values(sections).filter(s => s()).length;
    const pct = (complete / 5) * 100;
    document.getElementById('progress-bar').style.width = pct + '%';
    document.getElementById('progress-text').textContent = `${complete} of 5 sections complete`;
}
```

---

## 8. Section Collapse/Expand

```javascript
document.querySelectorAll('.section-header').forEach(header => {
    header.addEventListener('click', () => {
        const content = header.nextElementSibling;
        content.classList.toggle('hidden');
        header.classList.toggle('collapsed');
    });
});
```

Sections start expanded. Clicking header collapses content.

---

## 9. Collapsible Entry Cards (Experience, Education, etc.)

Each entry card has:
- Edit button (expands inline edit)
- Delete button (removes card with confirmation)
- Collapsed view: shows title + company/date summary
- Expanded view: full form fields

---

## 10. Professional Summary Section

Add to the Personal Information section:

```html
<div>
    <label class="block text-sm font-medium text-gray-700 mb-1">Professional Summary</label>
    <textarea name="professional_summary" rows="3" maxlength="500"
        class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Brief overview of your skills and career goals..."></textarea>
    <p class="text-xs text-gray-500 mt-1"><span id="summary-chars">0</span>/500 characters</p>
</div>
```

Character counter updates on input.

---

## 11. Tests

### `resumes/tests.py` — Add builder and API tests

```python
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

### Builder page tests

```python
class ResumeBuilderTests(TestCase):
    def test_builder_page_has_form_and_preview(self):
        response = self.client.get(reverse('resume_update', args=[self.resume.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'resume-form')
        self.assertContains(response, 'preview-panel')
        self.assertContains(response, 'template-switcher')

    def test_progress_bar_shown(self):
        response = self.client.get(reverse('resume_update', args=[self.resume.id]))
        self.assertContains(response, 'progress-bar')

    def test_template_switcher_buttons(self):
        response = self.client.get(reverse('resume_update', args=[self.resume.id]))
        self.assertContains(response, 'Classic')
        self.assertContains(response, 'Modern')
        self.assertContains(response, 'Minimal')
```

---

## File Summary

| File | Action |
|------|--------|
| `requirements.txt` | Edit — add `djangorestframework` |
| `resumes/models.py` | Edit — add 3 fields to Resume |
| `resumes/serializers.py` | Create — ResumeSerializer |
| `resumes/views.py` | Edit — add ResumeViewSet + preview-fragment view |
| `resumes/urls.py` | Edit — add API router + preview-fragment URL |
| `resumes/tests.py` | Edit — add API and builder tests |
| `templates/resumes/resume_builder.html` | Create (replaces resume_update.html) |
| `templates/resumes/resume_classic.html` | Create (copy of existing preview) |
| `templates/resumes/resume_modern.html` | Create (new style) |
| `templates/resumes/resume_minimal.html` | Create (new style) |
| `resumes/admin.py` | Edit — register new fields |

---

## Dependencies

- Django 4.2 (already installed)
- `djangorestframework` (new)
- `python-dotenv` (already installed)
- No JavaScript framework needed — vanilla JS per spec
