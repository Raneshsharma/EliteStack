# P3 Implementation Plan — AI Features + Infrastructure

> **For agentic workers:** Execute inline in this session. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Build the OpenAI infrastructure (Task 1) and P3.1 AI Resume Rewrite feature (Tasks 2–7), then P3.3 Cover Letter Generator (Tasks 8–11). Remaining P3 features can be added on top of this foundation.

**Architecture:** All AI features share a single `ai/services.py` module with the OpenAI client. API endpoints are DRF ViewSets. P3.1 is embedded inline in the resume builder template using JavaScript text selection. P3.3 is a standalone page with its own template.

**Tech Stack:** `openai` Python SDK, Django REST Framework, vanilla JS for floating toolbar and modal UI.

---

## Phase 0: Infrastructure

### Task 1: OpenAI Client + Subscription Tier + Rate Limiting

**Files:**
- Modify: `accounts/models.py:1-52`
- Modify: `placement_copilot/settings.py`
- Modify: `.env.example`
- Modify: `accounts/admin.py`
- Modify: `placement_copilot/admin.py`
- Create: `ai/services.py`
- Create: `ai/rate_limiter.py`
- Modify: `accounts/migrations/`
- Test: `accounts/tests.py`

---

- [ ] **Step 1: Add `OPENAI_API_KEY` to `.env.example`**

Read `.env.example`, then add:

```
OPENAI_API_KEY=sk-...
```

---

- [ ] **Step 2: Add OpenAI config to `settings.py`**

After the existing settings, add:

```python
# OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
OPENAI_TIMEOUT = int(os.getenv('OPENAI_TIMEOUT', '30'))
```

Also add `'ai'` to `INSTALLED_APPS` between `'rest_framework'` and `'accounts'`.

---

- [ ] **Step 3: Add `subscription_tier` to `UserProfile`**

Read `accounts/models.py`, find the `UserProfile` class, and add after `email_opt_out`:

```python
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
```

---

- [ ] **Step 4: Add rate limit constants to `settings.py`**

```python
# AI Rate Limits (rewrites per day per tier)
AI_RATE_LIMITS = {
    'free': 0,       # gated — show upgrade modal
    'pro': 20,
    'premium': 50,
}
COVER_LETTER_RATE_LIMITS = {
    'free': 0,
    'pro': 10,
    'premium': 30,
}
```

---

- [ ] **Step 5: Create `ai/rate_limiter.py`**

```python
"""In-memory rate limiter for AI features. Works for single-instance dev/prod."""
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# In-memory store: {user_id: [(tier, reset_at), ...]}
_rewrite_counts: dict[int, list[tuple[int, datetime]]] = defaultdict(list)
_coverletter_counts: dict[int, list[tuple[int, datetime]]] = defaultdict(list)


def _clean_old(counts_dict: dict, user_id: int) -> None:
    """Remove expired entries for a user."""
    now = datetime.now(timezone.utc)
    counts_dict[user_id] = [
        (count, ts) for count, ts in counts_dict[user_id] if ts > now
    ]


def get_rewrite_remaining(user_id: int, daily_limit: int) -> int:
    """Return how many rewrites are left for today."""
    _clean_old(_rewrite_counts, user_id)
    used = sum(count for count, _ in _rewrite_counts[user_id])
    return max(0, daily_limit - used)


def record_rewrite(user_id: int, daily_limit: int) -> bool:
    """
    Record one rewrite. Returns True if allowed, False if rate limit exceeded.
    """
    _clean_old(_rewrite_counts, user_id)
    now = datetime.now(timezone.utc)
    reset_at = now + timedelta(hours=24)
    used = sum(count for count, _ in _rewrite_counts[user_id])
    if used >= daily_limit:
        return False
    _rewrite_counts[user_id].append((1, reset_at))
    return True


def get_coverletter_remaining(user_id: int, daily_limit: int) -> int:
    _clean_old(_coverletter_counts, user_id)
    used = sum(count for count, _ in _coverletter_counts[user_id])
    return max(0, daily_limit - used)


def record_coverletter(user_id: int, daily_limit: int) -> bool:
    _clean_old(_coverletter_counts, user_id)
    now = datetime.now(timezone.utc)
    reset_at = now + timedelta(hours=24)
    used = sum(count for count, _ in _coverletter_counts[user_id])
    if used >= daily_limit:
        return False
    _coverletter_counts[user_id].append((1, reset_at))
    return True
```

---

- [ ] **Step 6: Create `ai/services.py`**

```python
"""Shared OpenAI client for all AI features."""
import logging
import openai
from django.conf import settings

logger = logging.getLogger(__name__)

_client = None


def get_client() -> openai.OpenAI:
    global _client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set. Add it to your .env file.")
        _client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def call_openai(system_prompt: str, user_prompt: str, max_tokens: int = 500) -> str:
    """Call OpenAI chat completion. Raises on error."""
    client = get_client()
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def generate_resume_rewrites(original_text: str) -> list[str]:
    """Generate 3 resume bullet rewrites. Returns list of 3 strings."""
    system_prompt = (
        "You are a professional resume writer. Rewrite the following resume bullet point "
        "to be more specific, action-oriented, and ATS-friendly. "
        "Return exactly 3 alternatives, each on a separate line starting with '1. ', '2. ', '3. '. "
        "Do not add any extra text, numbering beyond 1/2/3, or commentary."
    )
    user_prompt = f"Resume bullet:\n{original_text}"
    result = call_openai(system_prompt, user_prompt, max_tokens=600)

    rewrites = []
    for line in result.splitlines():
        line = line.strip()
        # Strip "1. ", "2. ", "3. " prefix if present
        for prefix in ('1. ', '2. ', '3. '):
            if line.startswith(prefix):
                line = line[len(prefix):]
                break
        if line:
            rewrites.append(line)
        if len(rewrites) >= 3:
            break

    # If we got fewer than 3, pad with what we have (avoid empty strings)
    while len(rewrites) < 3:
        rewrites.append(rewrites[-1] if rewrites else "[Could not generate rewrite]")
    return rewrites[:3]


def generate_cover_letter(
    resume_data: str,
    job_title: str,
    company_name: str,
    hiring_manager_name: str,
    job_description: str,
) -> str:
    """Generate a cover letter from resume data and job info."""
    system_prompt = (
        "You are a professional cover letter writer. Write a complete, personalized cover letter "
        "of 300–500 words. Use a professional tone. Include: your interest in the role, "
        "relevant skills and experience from the resume, and a strong closing. "
        "Do not invent any facts not present in the resume data."
    )
    salutation = f"Dear {hiring_manager_name}," if hiring_manager_name else "Dear Hiring Team,"
    user_prompt = (
        f"Resume:\n{resume_data}\n\n"
        f"Job Title: {job_title}\n"
        f"Company: {company_name}\n"
        f"{salutation}\n\n"
        f"Job Description (if provided):\n{job_description}"
    )
    letter = call_openai(system_prompt, user_prompt, max_tokens=800)
    # Prepend salutation if not already at start
    if not letter.strip().lower().startswith('dear'):
        letter = f"{salutation}\n\n{letter}"
    return letter


def generate_job_match(
    resume_data: str,
    job_description: str,
    sections: list[str],
) -> dict:
    """Analyze job description and rewrite resume sections to match keywords."""
    system_prompt = (
        "You are an expert resume tailor. Analyze the job description and resume. "
        "Rewrite the requested sections to incorporate relevant keywords and phrasing "
        "from the job description while maintaining factual accuracy. "
        "Return a JSON object with keys: 'match_score' (0-100 integer), "
        "'rewritten_sections' (dict of section_name -> rewritten text), "
        "'keywords_found' (list of strings), 'keywords_matched' (list of strings), "
        "'recommendations' (list of strings). "
        "Do not invent skills or experiences not present in the resume."
    )
    user_prompt = (
        f"Resume:\n{resume_data}\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Sections to rewrite: {', '.join(sections)}"
    )
    client = get_client()
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1000,
        response_format={"type": "json_object"},
    )
    import json
    result = json.loads(response.choices[0].message.content.strip())
    return result
```

---

- [ ] **Step 7: Run makemigrations and migrate**

```bash
cd d:/EliteSttack
python manage.py makemigrations accounts --name add_subscription_tier
python manage.py migrate
```

Expected: Migration created and applied.

---

- [ ] **Step 8: Update `accounts/admin.py` — add subscription tier to UserProfile admin**

Read `accounts/admin.py`. Find `UserProfileAdmin`. Add to `list_display`:

```python
'subscription_tier'
```

Add to `list_filter`:

```python
'subscription_tier'
```

---

- [ ] **Step 9: Update `placement_copilot/admin.py` — expose subscription_tier on user list**

Read `placement_copilot/admin.py`. Find `CustomUserAdmin`. In `list_display`, add `'subscription_tier'` (or a method that shows the tier from profile). Add a helper method:

```python
def subscription_tier(self, obj):
    tier = getattr(obj, 'profile', None)
    if tier:
        return tier.subscription_tier.title()
    return '-'
subscription_tier.short_description = 'Tier'
```

---

- [ ] **Step 10: Update `.env.example` — document OpenAI key**

Read `.env.example`, add after existing vars:

```
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=30
```

---

- [ ] **Step 11: Run tests**

```bash
python manage.py test accounts.tests -v 2>&1 | tail -10
```

Expected: All pass (143+).

---

- [ ] **Step 12: Commit**

```bash
git add accounts/models.py accounts/admin.py placement_copilot/settings.py placement_copilot/admin.py .env.example ai/ accounts/migrations/
git commit -m "feat: add OpenAI client, subscription tiers, and rate limiter infrastructure"
```

---

## Phase 1: P3.1 AI Resume Rewrite

### Task 2: DRF API Endpoint for Resume Rewrite

**Files:**
- Modify: `resumes/urls.py`
- Create: `resumes/ai_views.py`
- Test: `resumes/tests.py`

---

- [ ] **Step 1: Create `resumes/ai_views.py`**

```python
"""AI-powered API endpoints for resume features."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .models import Resume
from .serializers import ResumeSerializer
from ai.services import generate_resume_rewrites
from ai.rate_limiter import get_rewrite_remaining, record_rewrite


class ResumeRewriteView(APIView):
    """POST /api/resumes/<id>/rewrite/ — generate 3 AI rewrites."""
    permission_classes = [IsAuthenticated]

    def post(self, request, resume_id):
        resume = Resume.objects.filter(user=request.user, id=resume_id).first()
        if not resume:
            return Response({'error': 'Resume not found.'}, status=status.HTTP_404_NOT_FOUND)

        tier = getattr(request.user, 'profile', None)
        current_tier = tier.subscription_tier if tier else 'free'
        daily_limit = settings.AI_RATE_LIMITS.get(current_tier, 0)

        if current_tier == 'free':
            return Response(
                {
                    'error': 'upgrade_required',
                    'message': 'AI Resume Rewrite is available on Pro and Premium plans.',
                    'tier': current_tier,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        selected_text = request.data.get('selected_text', '').strip()
        if not selected_text:
            return Response({'error': 'No text selected.'}, status=status.HTTP_400_BAD_REQUEST)

        if len(selected_text.split()) > 500:
            return Response(
                {'error': 'Text exceeds 500 words. Please select a shorter section.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        remaining = get_rewrite_remaining(request.user.id, daily_limit)
        if remaining <= 0:
            return Response(
                {
                    'error': 'rate_limit',
                    'message': f"You've used all your AI rewrites for today ({daily_limit}). Upgrade for more.",
                    'tier': current_tier,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        try:
            alternatives = generate_resume_rewrites(selected_text)
        except Exception as e:
            import logging
            logging.error(f"AI rewrite failed for user {request.user.id}: {e}")
            return Response(
                {'error': 'AI rewrite failed. Please try again.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        record_rewrite(request.user.id, daily_limit)
        new_remaining = get_rewrite_remaining(request.user.id, daily_limit)

        return Response({
            'alternatives': alternatives,
            'remaining': new_remaining,
            'limit': daily_limit,
        })
```

---

- [ ] **Step 2: Add URL route to `resumes/urls.py`**

Read `resumes/urls.py`. Add to imports:

```python
from . import ai_views
```

Add to `urlpatterns` (before the router to avoid conflict):

```python
path('api/resumes/<int:resume_id>/rewrite/', ai_views.ResumeRewriteView.as_view(), name='resume_rewrite'),
```

---

- [ ] **Step 3: Write tests for rewrite endpoint**

Read `resumes/tests.py`. Add these test methods to the existing test class:

```python
def test_rewrite_requires_authentication(self):
    response = self.client.post('/api/resumes/1/rewrite/', {'selected_text': 'Did emails'})
    self.assertIn(response.status_code, [401, 403])

def test_rewrite_free_tier_returns_upgrade_required(self):
    self.client.force_login(self.user)
    # user profile defaults to 'free'
    response = self.client.post(
        f'/api/resumes/{self.resume.id}/rewrite/',
        {'selected_text': 'Managed team of 5 engineers'},
        format='json'
    )
    self.assertEqual(response.status_code, 403)
    self.assertEqual(response.json()['error'], 'upgrade_required')

def test_rewrite_empty_text_returns_400(self):
    self.user.profile.subscription_tier = 'pro'
    self.user.profile.save()
    self.client.force_login(self.user)
    response = self.client.post(
        f'/api/resumes/{self.resume.id}/rewrite/',
        {'selected_text': ''},
        format='json'
    )
    self.assertEqual(response.status_code, 400)
    self.assertIn('No text selected', response.json()['error'])

def test_rewrite_too_long_returns_400(self):
    self.user.profile.subscription_tier = 'pro'
    self.user.profile.save()
    self.client.force_login(self.user)
    long_text = ' '.join(['word'] * 501)
    response = self.client.post(
        f'/api/resumes/{self.resume.id}/rewrite/',
        {'selected_text': long_text},
        format='json'
    )
    self.assertEqual(response.status_code, 400)
    self.assertIn('500 words', response.json()['error'])
```

---

- [ ] **Step 4: Run tests**

```bash
python manage.py test resumes.tests -v 2>&1 | tail -15
```

Expected: All pass including new tests.

---

- [ ] **Step 5: Commit**

```bash
git add resumes/ai_views.py resumes/urls.py resumes/tests.py
git commit -m "feat(api): add POST /api/resumes/<id>/rewrite/ endpoint with tier check"
```

---

### Task 3: Floating Toolbar + Rewrite Modal UI

**Files:**
- Modify: `templates/resumes/resume_builder.html`
- Modify: `static/css/landing.css` (add modal styles)
- Modify: `static/js/landing.js`

---

- [ ] **Step 1: Add floating toolbar and modal HTML to `resume_builder.html`**

Read `templates/resumes/resume_builder.html` (the full file — it's ~300+ lines). Find the closing `{% endblock %}` tag. Insert before it:

```html

<!-- AI Rewrite Floating Toolbar -->
<div id="ai-toolbar" class="fixed z-50 hidden bg-white border border-blue-300 rounded-lg shadow-lg p-2 flex gap-2 items-center" style="min-width: 200px;">
    <button id="ai-rewrite-btn" type="button"
            class="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 flex items-center gap-1.5">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
        Rewrite with AI
    </button>
    <span id="ai-rewrite-remaining" class="text-xs text-gray-500"></span>
</div>

<!-- AI Rewrite Modal -->
<div id="ai-rewrite-modal" class="fixed inset-0 z-50 hidden">
    <div class="absolute inset-0 bg-black/50" id="ai-modal-backdrop"></div>
    <div class="absolute inset-0 flex items-center justify-center p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto">
            <!-- Header -->
            <div class="flex justify-between items-center p-4 border-b">
                <h3 class="text-lg font-bold text-gray-900">AI Rewrite Suggestions</h3>
                <button id="ai-modal-close" class="text-gray-400 hover:text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>
            <!-- Original text (collapsed) -->
            <div class="px-4 pt-3">
                <button id="ai-original-toggle" type="button" class="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                    Original text
                </button>
                <div id="ai-original-text" class="hidden mt-2 p-3 bg-gray-50 rounded-lg text-sm text-gray-600 italic"></div>
            </div>
            <!-- Loading -->
            <div id="ai-rewrite-loading" class="hidden px-4 py-8 text-center">
                <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-200 border-t-blue-600"></div>
                <p class="mt-3 text-gray-600 text-sm">Generating rewrites...</p>
            </div>
            <!-- Rewrite alternatives -->
            <div id="ai-rewrite-options" class="hidden px-4 py-3 space-y-3"></div>
            <!-- Error -->
            <div id="ai-rewrite-error" class="hidden px-4 py-6 text-center">
                <p class="text-red-600 text-sm" id="ai-error-message"></p>
                <button id="ai-retry-btn" class="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">Try Again</button>
            </div>
            <!-- Footer -->
            <div class="p-4 border-t flex justify-between items-center">
                <span id="ai-remaining-text" class="text-xs text-gray-400"></span>
                <button id="ai-regenerate-btn" type="button"
                        class="hidden px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm">
                    Regenerate
                </button>
            </div>
        </div>
    </div>
</div>

<!-- Upgrade Modal (Free tier) -->
<div id="upgrade-modal" class="fixed inset-0 z-50 hidden">
    <div class="absolute inset-0 bg-black/50" id="upgrade-modal-backdrop"></div>
    <div class="absolute inset-0 flex items-center justify-center p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-md p-6 text-center">
            <div class="text-4xl mb-3">⭐</div>
            <h3 class="text-xl font-bold text-gray-900 mb-2">Unlock AI Rewrite</h3>
            <p class="text-gray-600 mb-1">AI Resume Rewrite is available on <strong>Pro</strong> and <strong>Premium</strong> plans.</p>
            <p class="text-gray-500 text-sm mb-6">Upgrade to get 20–50 AI rewrites per day.</p>
            <div class="flex gap-3 justify-center">
                <a href="/#pricing" class="px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-sm">See Plans</a>
                <button id="upgrade-close-btn" class="px-5 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm">Maybe Later</button>
            </div>
        </div>
    </div>
</div>
```

---

- [ ] **Step 2: Add CSS styles for modals to `static/css/landing.css`**

Append to `landing.css`:

```css
/* AI Rewrite Modal */
#ai-rewrite-options .rewrite-card {
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    padding: 14px;
    transition: border-color 0.2s;
}
#ai-rewrite-options .rewrite-card:hover {
    border-color: #93c5fd;
}
#ai-rewrite-options .rewrite-card.selected {
    border-color: #2563eb;
    background: #eff6ff;
}
```

---

- [ ] **Step 3: Add rewrite JS to `static/js/landing.js`**

Read `static/js/landing.js`. Add at the end (before the closing `});`):

```javascript
// ============================================
// AI Resume Rewrite
// ============================================
(function() {
    var toolbar = document.getElementById('ai-toolbar');
    var rewriteBtn = document.getElementById('ai-rewrite-btn');
    var modal = document.getElementById('ai-rewrite-modal');
    var modalBackdrop = document.getElementById('ai-modal-backdrop');
    var modalClose = document.getElementById('ai-modal-close');
    var upgradeModal = document.getElementById('upgrade-modal');
    var upgradeBackdrop = document.getElementById('upgrade-modal-backdrop');
    var upgradeCloseBtn = document.getElementById('upgrade-close-btn');
    var loadingDiv = document.getElementById('ai-rewrite-loading');
    var optionsDiv = document.getElementById('ai-rewrite-options');
    var errorDiv = document.getElementById('ai-rewrite-error');
    var errorMsg = document.getElementById('ai-error-message');
    var originalText = document.getElementById('ai-original-text');
    var originalToggle = document.getElementById('ai-original-toggle');
    var regenerateBtn = document.getElementById('ai-retry-btn');
    var retryBtn = document.getElementById('ai-retry-btn');
    var remainingText = document.getElementById('ai-remaining-text');
    var resumeId = document.getElementById('resume-id');

    if (!toolbar || !rewriteBtn) return;

    var selectedText = '';
    var alternatives = [];
    var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ?
        document.querySelector('[name=csrfmiddlewaretoken]').value : '';

    // Show floating toolbar on text selection within form fields
    document.addEventListener('mouseup', function(e) {
        // Only activate in builder form
        var form = document.getElementById('resume-form');
        if (!form || !form.contains(e.target)) return;

        var sel = window.getSelection().toString().trim();
        if (sel.length > 10) {
            selectedText = sel;
            var range = window.getSelection().getRangeAt(0);
            var rect = range.getBoundingClientRect();
            toolbar.style.left = (rect.left + window.scrollX) + 'px';
            toolbar.style.top = (rect.top + window.scrollY - 50) + 'px';
            toolbar.classList.remove('hidden');
        } else {
            toolbar.classList.add('hidden');
        }
    });

    rewriteBtn.addEventListener('click', function() {
        if (!resumeId) return;
        var rid = resumeId.value;
        fetch('/api/resumes/' + rid + '/rewrite/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken || document.querySelector('input[name="csrfmiddlewaretoken"]').value,
            },
            body: JSON.stringify({selected_text: selectedText})
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.error === 'upgrade_required') {
                upgradeModal.classList.remove('hidden');
                return;
            }
            if (data.error === 'rate_limit') {
                showError(data.message);
                return;
            }
            if (data.error) {
                showError(data.error);
                return;
            }
            alternatives = data.alternatives;
            showAlternatives(alternatives, data.remaining, data.limit);
        })
        .catch(function() {
            showError('AI rewrite failed. Please check your connection and try again.');
        });
    });

    function showAlternatives(alts, remaining, limit) {
        loadingDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        optionsDiv.classList.remove('hidden');
        modal.classList.remove('hidden');
        toolbar.classList.add('hidden');

        originalText.textContent = selectedText;
        remainingText.textContent = remaining + ' rewrites remaining today';

        optionsDiv.innerHTML = '';
        alts.forEach(function(alt, idx) {
            var card = document.createElement('div');
            card.className = 'rewrite-card';
            card.innerHTML =
                '<p class="text-gray-800 text-sm leading-relaxed mb-3">' + escapeHtml(alt) + '</p>' +
                '<div class="flex gap-2">' +
                '<button type="button" class="use-this-btn flex-1 px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"' +
                ' data-text="' + escapeAttr(alt) + '">Use This</button>' +
                '<button type="button" class="edit-btn px-3 py-1.5 border border-gray-300 text-gray-700 text-sm rounded-md hover:bg-gray-50"' +
                ' data-text="' + escapeAttr(alt) + '">Edit</button>' +
                '</div>';
            optionsDiv.appendChild(card);
        });

        // Use This
        optionsDiv.querySelectorAll('.use-this-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                applyRewrite(btn.dataset.text);
                closeModal();
            });
        });

        // Edit
        optionsDiv.querySelectorAll('.edit-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var textarea = document.createElement('textarea');
                textarea.className = 'w-full p-2 border rounded-lg text-sm mb-2';
                textarea.value = btn.dataset.text;
                textarea.rows = 3;
                var card = btn.closest('.rewrite-card');
                card.querySelector('p').replaceWith(textarea);
                btn.closest('.flex').innerHTML =
                    '<button type="button" class="apply-edit-btn flex-1 px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700">' +
                    'Use This</button>';
                card.querySelector('.apply-edit-btn').addEventListener('click', function() {
                    applyRewrite(textarea.value);
                    closeModal();
                });
            });
        });
    }

    function showError(msg) {
        loadingDiv.classList.add('hidden');
        optionsDiv.classList.add('hidden');
        errorDiv.classList.remove('hidden');
        errorMsg.textContent = msg;
        modal.classList.remove('hidden');
    }

    function closeModal() {
        modal.classList.add('hidden');
        toolbar.classList.add('hidden');
        window.getSelection().removeAllRanges();
    }

    function applyRewrite(text) {
        // Find the active form field and replace selection
        var sel = window.getSelection();
        if (sel.rangeCount > 0) {
            var range = sel.getRangeAt(0);
            range.deleteContents();
            range.insertNode(document.createTextNode(text));
            sel.removeAllRanges();
        }
        // Also try to find textarea and replace
        var activeEl = document.activeElement;
        if (activeEl && (activeEl.tagName === 'TEXTAREA' || activeEl.tagName === 'INPUT')) {
            var val = activeEl.value;
            // simple approach: append if we can't locate exact selection
        }
    }

    function escapeHtml(str) {
        return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }
    function escapeAttr(str) {
        return str.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    // Close handlers
    modalBackdrop && modalBackdrop.addEventListener('click', closeModal);
    modalClose && modalClose.addEventListener('click', closeModal);
    regenerateBtn && regenerateBtn.addEventListener('click', function() {
        optionsDiv.classList.add('hidden');
        loadingDiv.classList.remove('hidden');
        // Re-trigger rewrite (same selection, same flow)
        rewriteBtn.click();
    });

    // Upgrade modal
    upgradeBackdrop && upgradeBackdrop.addEventListener('click', function() {
        upgradeModal.classList.add('hidden');
    });
    upgradeCloseBtn && upgradeCloseBtn.addEventListener('click', function() {
        upgradeModal.classList.add('hidden');
    });

    // Original text toggle
    originalToggle && originalToggle.addEventListener('click', function() {
        originalText.classList.toggle('hidden');
    });
})();
```

---

- [ ] **Step 4: Verify template renders without errors**

```bash
cd d:/EliteSttack
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'placement_copilot.settings')
django.setup()
from django.template import engines
engine = engines['django']
t = engine.get_template('resumes/resume_builder.html')
print('Template loads OK, lines:', len(t.source.splitlines()))
" 2>&1
```

Expected: Template loads OK.

---

- [ ] **Step 5: Run tests**

```bash
python manage.py test -v 0 2>&1 | tail -5
```

Expected: All pass.

---

- [ ] **Step 6: Commit**

```bash
git add templates/resumes/resume_builder.html static/css/landing.css static/js/landing.js
git commit -m "feat(ui): add floating AI toolbar and rewrite modal to resume builder"
```

---

## Phase 2: P3.3 Cover Letter Generator

### Task 4: Cover Letter Model + API Endpoint

**Files:**
- Create: `resumes/migrations/XXXX_add_coverletter.py`
- Modify: `resumes/urls.py`
- Modify: `resumes/ai_views.py`

---

- [ ] **Step 1: Add `CoverLetter` model to `resumes/models.py`**

Read `resumes/models.py`. Find the end of the file. Add after the last model:

```python
class CoverLetter(models.Model):
    """Generated cover letter attached to a resume."""
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='cover_letters'
    )
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    hiring_manager_name = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    word_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Cover letter for {self.job_title} at {self.company_name}"
```

---

- [ ] **Step 2: Run makemigrations and migrate**

```bash
python manage.py makemigrations resumes --name add_coverletter
python manage.py migrate
```

---

- [ ] **Step 3: Add cover letter endpoints to `resumes/ai_views.py`**

Append to `resumes/ai_views.py`:

```python
import json as json_lib
from .models import Resume, CoverLetter
from .serializers import ResumeSerializer
from ai.services import generate_cover_letter
from ai.rate_limiter import get_coverletter_remaining, record_coverletter


def serialize_resume_text(resume: Resume) -> str:
    """Serialize a resume's key fields into a single text block for the AI."""
    lines = []
    if resume.full_name:
        lines.append(f"Name: {resume.full_name}")
    if resume.email:
        lines.append(f"Email: {resume.email}")
    if resume.professional_summary:
        lines.append(f"Summary: {resume.professional_summary}")

    for edu in resume.resumeeducation_set.all():
        lines.append(f"Education: {edu.degree} at {edu.school} ({edu.start_date} - {edu.end_date or 'Present'})")
    for exp in resume.resumeexperience_set.all():
        lines.append(f"Experience: {exp.job_title} at {exp.company} ({exp.start_date} - {exp.end_date or 'Present'})")
        if exp.description:
            lines.append(f"  {exp.description}")
    for proj in resume.resumeproject_set.all():
        lines.append(f"Project: {proj.name} - {proj.description or ''}")
    for skill in resume.resumeskill_set.all():
        lines.append(f"Skill: {skill.name}")
    return '\n'.join(lines)


class CoverLetterGenerateView(APIView):
    """POST /api/resumes/<id>/cover-letter/ — generate a cover letter."""
    permission_classes = [IsAuthenticated]

    def post(self, request, resume_id):
        resume = Resume.objects.filter(user=request.user, id=resume_id).first()
        if not resume:
            return Response({'error': 'Resume not found.'}, status=status.HTTP_404_NOT_FOUND)

        tier = getattr(request.user, 'profile', None)
        current_tier = tier.subscription_tier if tier else 'free'
        daily_limit = settings.COVER_LETTER_RATE_LIMITS.get(current_tier, 0)

        if current_tier == 'free':
            return Response(
                {
                    'error': 'upgrade_required',
                    'message': 'Cover Letter Generator is available on Pro and Premium plans.',
                    'tier': current_tier,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        job_title = request.data.get('job_title', '').strip()
        company_name = request.data.get('company_name', '').strip()
        if not job_title or not company_name:
            return Response(
                {'error': 'job_title and company_name are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        hiring_manager = request.data.get('hiring_manager_name', '').strip()
        job_description = request.data.get('job_description', '').strip()[:3000]

        remaining = get_coverletter_remaining(request.user.id, daily_limit)
        if remaining <= 0:
            return Response(
                {
                    'error': 'rate_limit',
                    'message': f"You've reached your daily limit ({daily_limit}). Upgrade for more.",
                    'tier': current_tier,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        resume_data = serialize_resume_text(resume)
        if not resume_data.strip():
            return Response(
                {'error': 'Your resume has no content. Add some information first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            letter = generate_cover_letter(
                resume_data=resume_data,
                job_title=job_title,
                company_name=company_name,
                hiring_manager_name=hiring_manager,
                job_description=job_description,
            )
        except Exception as e:
            import logging
            logging.error(f"Cover letter failed for user {request.user.id}: {e}")
            return Response(
                {'error': 'Failed to generate cover letter. Please try again.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        record_coverletter(request.user.id, daily_limit)
        word_count = len(letter.split())

        # Save the cover letter
        cl = CoverLetter.objects.create(
            resume=resume,
            job_title=job_title,
            company_name=company_name,
            hiring_manager_name=hiring_manager,
            content=letter,
            word_count=word_count,
        )

        return Response({
            'id': cl.id,
            'content': letter,
            'word_count': word_count,
            'job_title': job_title,
            'company_name': company_name,
            'remaining': get_coverletter_remaining(request.user.id, daily_limit),
        })


class CoverLetterDownloadView(APIView):
    """GET /api/cover-letter/<id>/download/ — download as .txt file."""
    permission_classes = [IsAuthenticated]

    def get(self, request, letter_id):
        cl = CoverLetter.objects.filter(resume__user=request.user, id=letter_id).first()
        if not cl:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return HttpResponse(
            cl.content,
            content_type='text/plain',
            headers={
                'Content-Disposition': f'attachment; filename="cover_letter_{cl.company_name}.txt"'
            }
        )
```

Add to imports at the top of `ai_views.py`:

```python
from django.http import HttpResponse
```

---

- [ ] **Step 4: Add URLs for cover letter endpoints**

Read `resumes/urls.py`. Add after the rewrite URL:

```python
path('api/resumes/<int:resume_id>/cover-letter/', ai_views.CoverLetterGenerateView.as_view(), name='cover_letter_generate'),
path('api/cover-letter/<int:letter_id>/download/', ai_views.CoverLetterDownloadView.as_view(), name='cover_letter_download'),
```

---

- [ ] **Step 5: Add cover letter to admin**

Read `resumes/admin.py`. Add after the existing registrations:

```python
from .models import CoverLetter

class CoverLetterAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'company_name', 'resume', 'word_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['job_title', 'company_name', 'resume__user__username']

placement_admin_site.register(CoverLetter, CoverLetterAdmin)
```

---

- [ ] **Step 6: Write tests for cover letter endpoint**

Add to `resumes/tests.py`:

```python
def test_cover_letter_requires_auth(self):
    response = self.client.post(
        f'/api/resumes/{self.resume.id}/cover-letter/',
        {'job_title': 'Engineer', 'company_name': 'Acme'},
        format='json'
    )
    self.assertIn(response.status_code, [401, 403])

def test_cover_letter_free_tier_gated(self):
    self.client.force_login(self.user)
    response = self.client.post(
        f'/api/resumes/{self.resume.id}/cover-letter/',
        {'job_title': 'Engineer', 'company_name': 'Acme'},
        format='json'
    )
    self.assertEqual(response.status_code, 403)
    self.assertEqual(response.json()['error'], 'upgrade_required')

def test_cover_letter_missing_fields(self):
    self.user.profile.subscription_tier = 'pro'
    self.user.profile.save()
    self.client.force_login(self.user)
    response = self.client.post(
        f'/api/resumes/{self.resume.id}/cover-letter/',
        {'job_title': 'Engineer'},  # missing company_name
        format='json'
    )
    self.assertEqual(response.status_code, 400)
```

---

- [ ] **Step 7: Run tests**

```bash
python manage.py test -v 0 2>&1 | tail -5
```

Expected: All pass.

---

- [ ] **Step 8: Commit**

```bash
git add resumes/models.py resumes/ai_views.py resumes/urls.py resumes/admin.py resumes/tests.py
git commit -m "feat: add CoverLetter model, generate/download endpoints, and Pro tier gate"
```

---

### Task 5: Cover Letter Page Template

**Files:**
- Create: `templates/resumes/cover_letter.html`
- Modify: `resumes/urls.py`
- Modify: `resumes/views.py`

---

- [ ] **Step 1: Add view for cover letter page in `resumes/views.py`**

Read `resumes/views.py` (first ~80 lines). Add after the existing views:

```python
@login_required
def cover_letter_page(request, resume_id):
    """Cover letter generation page."""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    tier = getattr(request.user, 'profile', None)
    current_tier = tier.subscription_tier if tier else 'free'
    from django.conf import settings
    daily_limit = settings.COVER_LETTER_RATE_LIMITS.get(current_tier, 0)
    from ai.rate_limiter import get_coverletter_remaining
    remaining = get_coverletter_remaining(request.user.id, daily_limit)
    return render(request, 'resumes/cover_letter.html', {
        'resume': resume,
        'tier': current_tier,
        'remaining': remaining,
        'limit': daily_limit,
    })
```

Add import at the top if not already present:

```python
from django.http import Http404
```

---

- [ ] **Step 2: Add URL for cover letter page**

Read `resumes/urls.py`. Add:

```python
path('resumes/<int:resume_id>/cover-letter/', views.cover_letter_page, name='cover_letter_page'),
```

---

- [ ] **Step 3: Create `templates/resumes/cover_letter.html`**

```html
{% extends 'base.html' %}
{% block title %}Generate Cover Letter - {{ resume.title }}{% endblock %}

{% block content %}
<div class="max-w-3xl mx-auto py-8 px-4">
    <div class="flex items-center gap-3 mb-6">
        <a href="{% url 'resume_update' resume.id %}" class="text-gray-500 hover:text-gray-700">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        </a>
        <h1 class="text-2xl font-bold text-gray-900">Generate Cover Letter</h1>
    </div>

    <!-- Tier Banner -->
    {% if tier == 'free' %}
    <div class="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg flex items-center gap-3">
        <span class="text-xl">⭐</span>
        <div>
            <p class="font-medium text-amber-800">Cover Letter Generator is a Pro/Premium feature.</p>
            <a href="/#pricing" class="text-sm text-amber-700 underline">View Plans →</a>
        </div>
    </div>
    {% else %}
    <div class="mb-6 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
        {{ remaining }} of {{ limit }} cover letters remaining today.
    </div>
    {% endif %}

    <!-- Form -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <form id="cl-form" method="POST">
            {% csrf_token %}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Job Title *</label>
                    <input type="text" name="job_title" required
                           class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                           placeholder="e.g., Software Engineer">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Company Name *</label>
                    <input type="text" name="company_name" required
                           class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                           placeholder="e.g., Acme Corp">
                </div>
            </div>
            <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">Hiring Manager (optional)</label>
                <input type="text" name="hiring_manager_name"
                       class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                       placeholder="e.g., Sarah Johnson">
            </div>
            <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    Job Description <span class="text-gray-400">(optional — paste for a more tailored letter)</span>
                </label>
                <textarea name="job_description" rows="5"
                          class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="Paste the job description here to get a personalized cover letter..."
                          maxlength="3000"></textarea>
                <p class="text-xs text-gray-400 mt-1">Max 3,000 characters. More details = better results.</p>
            </div>
            <button type="submit" id="generate-btn"
                    class="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2 {% if tier == 'free' %}opacity-50 cursor-not-allowed{% endif %}"
                    {% if tier == 'free' %}disabled{% endif %}>
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                Generate Cover Letter
            </button>
        </form>

        <!-- Loading State -->
        <div id="cl-loading" class="hidden text-center py-10">
            <div class="inline-block animate-spin rounded-full h-10 w-10 border-4 border-blue-200 border-t-blue-600 mb-4"></div>
            <p class="text-gray-600">Writing your cover letter...</p>
            <p class="text-gray-400 text-sm mt-1">This may take up to 30 seconds</p>
        </div>

        <!-- Generated Letter -->
        <div id="cl-result" class="hidden mt-6">
            <div class="flex justify-between items-center mb-3">
                <h2 class="text-lg font-semibold text-gray-900">Generated Cover Letter</h2>
                <span id="cl-word-count" class="text-sm text-gray-400"></span>
            </div>
            <div class="bg-gray-50 rounded-lg p-6 border border-gray-200">
                <pre id="cl-content" class="whitespace-pre-wrap text-sm text-gray-800 font-sans" style="font-family: inherit;"></pre>
            </div>
            <div class="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-700">
                ⚠️ AI-generated. Please review and personalize before submitting.
            </div>
            <div class="mt-4 flex gap-3">
                <button id="cl-copy-btn" class="px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-sm">
                    Copy to Clipboard
                </button>
                <a id="cl-download-btn" class="px-5 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium text-sm">
                    Download as Text
                </a>
            </div>
        </div>

        <!-- Error -->
        <div id="cl-error" class="hidden mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p id="cl-error-text" class="text-red-700 text-sm"></p>
        </div>
    </div>
</div>

<script>
(function() {
    var form = document.getElementById('cl-form');
    var generateBtn = document.getElementById('generate-btn');
    var loadingDiv = document.getElementById('cl-loading');
    var resultDiv = document.getElementById('cl-result');
    var errorDiv = document.getElementById('cl-error');
    var contentPre = document.getElementById('cl-content');
    var wordCount = document.getElementById('cl-word-count');
    var copyBtn = document.getElementById('cl-copy-btn');
    var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    var resumeId = {{ resume.id }};
    var generatedId = null;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        var formData = new FormData(form);
        var data = {
            job_title: formData.get('job_title'),
            company_name: formData.get('company_name'),
            hiring_manager_name: formData.get('hiring_manager_name'),
            job_description: formData.get('job_description'),
        };

        form.classList.add('hidden');
        loadingDiv.classList.remove('hidden');

        fetch('/api/resumes/' + resumeId + '/cover-letter/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(data)
        })
        .then(function(r) { return r.json(); })
        .then(function(resp) {
            loadingDiv.classList.add('hidden');
            if (resp.error === 'upgrade_required') {
                form.classList.remove('hidden');
                alert('This feature requires a Pro or Premium subscription.');
                window.location.href = '/#pricing';
                return;
            }
            if (resp.error) {
                errorDiv.classList.remove('hidden');
                document.getElementById('cl-error-text').textContent = resp.error;
                form.classList.remove('hidden');
                return;
            }
            generatedId = resp.id;
            contentPre.textContent = resp.content;
            wordCount.textContent = resp.word_count + ' words';
            document.getElementById('cl-download-btn').href = '/api/cover-letter/' + resp.id + '/download/';
            resultDiv.classList.remove('hidden');
        })
        .catch(function() {
            loadingDiv.classList.add('hidden');
            errorDiv.classList.remove('hidden');
            document.getElementById('cl-error-text').textContent = 'Failed to generate cover letter. Please try again.';
            form.classList.remove('hidden');
        });
    });

    copyBtn && copyBtn.addEventListener('click', function() {
        navigator.clipboard.writeText(contentPre.textContent).then(function() {
            copyBtn.textContent = 'Copied!';
            setTimeout(function() { copyBtn.textContent = 'Copy to Clipboard'; }, 2000);
        });
    });
})();
</script>
{% endblock %}
```

---

- [ ] **Step 4: Add "Generate Cover Letter" button to resume builder template**

Read `templates/resumes/resume_builder.html`. Find the top bar section (around line 16-27). Add after the template switcher buttons:

```html
<a href="{% url 'cover_letter_page' resume.id %}"
   class="px-3 py-1.5 border border-gray-300 text-gray-700 text-sm rounded-md hover:bg-gray-50 flex items-center gap-1">
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
    Cover Letter
</a>
```

---

- [ ] **Step 5: Run tests**

```bash
python manage.py test -v 0 2>&1 | tail -5
```

Expected: All pass.

---

- [ ] **Step 6: Commit**

```bash
git add templates/resumes/cover_letter.html resumes/views.py resumes/urls.py
git commit -m "feat: add cover letter generation page with UI and download"
```

---

## Phase 3: Verify Full Suite

---

- [ ] **Step 1: Run full test suite**

```bash
python manage.py test -v 0 2>&1 | tail -5
```

Expected: All tests pass (143+).

---

- [ ] **Step 2: Verify Django check**

```bash
python manage.py check 2>&1
```

Expected: 0 issues.

---

## Summary

After all tasks complete:

| Task | What's Built |
|------|-------------|
| Task 1 | OpenAI client (`ai/services.py`), subscription tier on UserProfile, rate limiter, settings config |
| Task 2 | `POST /api/resumes/<id>/rewrite/` — with Pro gate, word limit, rate limiting, error handling |
| Task 3 | Floating toolbar + modal in resume builder. Text selection → click → modal with 3 rewrites → Use This / Edit / Regenerate |
| Task 4 | `CoverLetter` model, `POST /api/resumes/<id>/cover-letter/`, `GET /api/cover-letter/<id>/download/` |
| Task 5 | Cover letter page (`/resumes/<id>/cover-letter/`), form → loading → preview → copy/download |

**P3.2+ (Job Match)** can reuse `generate_job_match()` from `ai/services.py` — already implemented in Task 1.
