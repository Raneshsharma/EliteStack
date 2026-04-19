# Placement Copilot MVP - Implementation Plan

**Project:** Placement Copilot MVP
**Stack:** Python + Django + PostgreSQL + Tailwind CSS
**Date:** 2026-04-16

## Build Order

### Phase 1: Foundation
1. **Django Project Setup** - Create Django project, apps, configure settings, PostgreSQL
2. **Database Models** - User, Resume, ResumeEducation, ResumeExperience, ResumeProject, ResumeSkill
3. **Authentication** - Signup, Login, Logout, Password Change

### Phase 2: Core Features
4. **Resume Builder** - Multi-step form for creating resumes
5. **Resume Management** - List, Edit, Delete resumes
6. **Resume Preview/Export** - Preview resume, basic export

### Phase 3: Polish
7. **Onboarding** - Welcome page, empty states
8. **Minimal Settings** - Profile, password change, account deletion
9. **Admin & QA** - Django admin, final testing

---

## Phase 1: Foundation

### Task 1.1: Django Project Setup

**Owner:** Backend Tech Lead
**File:** `placement_copilot/`
**Apps:** `accounts/`, `resumes/`

**Steps:**
1. Create Django project structure
2. Configure `settings.py` with PostgreSQL
3. Configure `urls.py` with app routing
4. Configure `requirements.txt` with dependencies
5. Create `.env` template
6. Run initial migrations

**Dependencies:** None

**Verify:**
- `python manage.py check` passes
- Server starts on `python manage.py runserver`

---

### Task 1.2: Database Models

**Owner:** Database Agent
**File:** `resumes/models.py`
**Supporting Files:** `resumes/admin.py`

**Models to create:**
- `Resume` - user FK, title, is_primary, timestamps
- `ResumeEducation` - resume FK, school, degree, field_of_study, dates, gpa, description, order
- `ResumeExperience` - resume FK, company, job_title, location, dates, is_current, description, order
- `ResumeProject` - resume FK, name, role, dates, description, url, order
- `ResumeSkill` - resume FK, name, proficiency

**Dependencies:** Task 1.1 complete

**Verify:**
- `python manage.py makemigrations resumes` creates migrations
- `python manage.py migrate` succeeds
- Admin shows all models

---

### Task 1.3: Authentication

**Owner:** Auth Agent + Frontend Tech Lead
**File:** `accounts/`
**Templates:** `templates/account/`

**Steps:**
1. Create `accounts` app
2. Implement signup view/form
3. Implement login view/form
4. Implement logout view
5. Implement password change view/form
6. Create base template with auth nav
7. Create signup/login templates
8. Configure auth URLs

**Dependencies:** Task 1.1 complete

**Verify:**
- User can sign up
- User can log in
- User can log out
- Protected views redirect to login
- Playwright: signup → login → logout flow works

---

## Phase 2: Core Features

### Task 2.1: Resume Builder

**Owner:** Frontend Tech Lead + Backend Tech Lead
**File:** `resumes/views.py`, `resumes/forms.py`, `resumes/models.py`
**Templates:** `templates/resumes/builder/`

**Steps:**
1. Create ResumeBuilderForm (multi-step)
2. Create resume_create view
3. Create resume sections (personal, education, experience, projects, skills)
4. Create step indicator UI
5. Create section templates
6. Implement save functionality
7. Implement step navigation (next/back)
8. Handle form validation per step

**Dependencies:** Task 1.2, Task 1.3 complete

**Verify:**
- Can create resume with all sections
- Form validates each step
- Data saves to database
- Can navigate between steps

---

### Task 2.2: Resume Management

**Owner:** Backend Tech Lead + Frontend Tech Lead
**File:** `resumes/views.py`
**Templates:** `templates/resumes/`

**Steps:**
1. Create resume_list view
2. Create resume_list template
3. Create resume_update view
4. Create resume_delete view (with confirmation)
5. Implement set_primary functionality
6. Create empty state

**Dependencies:** Task 2.1 complete

**Verify:**
- List shows all user resumes
- Can edit existing resume
- Can delete resume (with confirmation)
- Can set primary resume
- Cannot see other users' resumes

---

### Task 2.3: Resume Preview & Export

**Owner:** Frontend Tech Lead + Backend Tech Lead
**File:** `resumes/views.py`
**Templates:** `templates/resumes/preview.html`

**Steps:**
1. Create resume_preview view
2. Create preview template
3. Create print-friendly CSS
4. Implement PDF export (basic HTML-to-print)

**Dependencies:** Task 2.1 complete

**Verify:**
- Preview shows complete resume
- Print/CSS export works
- Preview is responsive

---

## Phase 3: Polish

### Task 3.1: Onboarding

**Owner:** Product Manager Agent + Frontend Tech Lead
**Templates:** `templates/onboarding/`

**Steps:**
1. Create welcome page (for first-time users)
2. Create dashboard empty state
3. Add redirect logic for new users
4. Style onboarding components

**Dependencies:** Task 2.2 complete

**Verify:**
- New users see welcome page
- Empty state shows on dashboard with no resumes
- Skip option works
- "Create Resume" button prominent

---

### Task 3.2: Minimal Settings

**Owner:** Frontend Tech Lead + Auth Agent
**Templates:** `templates/settings/`

**Steps:**
1. Create settings page
2. Profile information form (username, email)
3. Password change form
4. Account deletion (with confirmation)
5. Style danger zone

**Dependencies:** Task 1.3 complete

**Verify:**
- Can update profile
- Can change password
- Can delete account
- Confirmation required for deletion

---

### Task 3.3: Admin & QA

**Owner:** QA Lead
**Files:** `resumes/admin.py`

**Steps:**
1. Configure Django admin for all models
2. Register Resume with inline sections
3. Add list filters and search
4. Run full Playwright test suite
5. Fix any issues

**Dependencies:** Tasks 3.1, 3.2 complete

**Verify:**
- Admin shows all models correctly
- Can manage resumes from admin
- All Playwright tests pass
- No console errors

---

## File Structure

```
d:/EliteSttack/
├── placement_copilot/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   └── templates/account/
├── resumes/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   └── templates/resumes/
├── templates/
│   ├── base.html
│   └── onboarding/
├── static/
│   ├── css/
│   └── js/
├── requirements.txt
├── manage.py
└── .env.example
```
