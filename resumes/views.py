from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.conf import settings
from rest_framework import viewsets, permissions
from .models import Resume, ResumeEducation, ResumeExperience, ResumeProject, ResumeSkill
from .forms import ResumeForm
from .serializers import ResumeSerializer
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import re


def welcome(request):
    """Welcome page for new users"""
    if request.user.is_authenticated:
        return render(request, 'onboarding/welcome.html')
    return redirect('login')


def landing_page(request):
    """Landing page view - public, no authentication required"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


@login_required
def dashboard(request):
    """Dashboard view — show stats, activity, and resume cards."""
    user = request.user

    # Sync computed status on all resumes
    resumes = Resume.objects.filter(user=user).select_related('user')
    for r in resumes:
        r.status = r.computed_status
        r.save(update_fields=['status'])

    # Stats
    total = resumes.count()
    complete = resumes.filter(status='complete').count()
    draft = resumes.filter(status='draft').count()
    last_edited = resumes.order_by('-updated_at').first()

    # Activity feed — last 5 updated resumes
    activity = resumes.order_by('-updated_at')[:5]

    return render(request, 'resumes/dashboard.html', {
        'resumes': resumes,
        'stats': {
            'total': total,
            'complete': complete,
            'draft': draft,
            'last_edited': last_edited.updated_at if last_edited else None,
        },
        'activity': activity,
    })


@login_required
def resume_create(request):
    """Multi-step resume creation wizard"""
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            # Save personal info fields
            resume.full_name = request.POST.get('full_name', '')
            resume.email = request.POST.get('email', '')
            resume.phone = request.POST.get('phone', '')
            resume.location = request.POST.get('location', '')
            resume.linkedin = request.POST.get('linkedin', '')
            resume.github = request.POST.get('github', '')
            resume.website = request.POST.get('website', '')
            resume.save()

            # Use template from gallery URL param, else user's default
            valid_templates = ['classic', 'modern', 'minimal']
            template_from_url = request.GET.get('template', '')
            if template_from_url in valid_templates:
                resume.template_style = template_from_url
                resume.save(update_fields=['template_style'])
            elif not resume.template_style:
                resume.template_style = getattr(request.user.profile, 'default_template', 'classic')
                resume.save(update_fields=['template_style'])

            # Mark onboarding as complete on first resume creation
            if not request.user.profile.onboarding_completed:
                request.user.profile.onboarding_completed = True
                request.user.profile.save(update_fields=['onboarding_completed'])

            _save_education(request, resume)
            _save_experience(request, resume)
            _save_projects(request, resume)
            _save_skills(request, resume)

            messages.success(request, 'Resume created successfully!')
            return redirect('resume_list')
    else:
        default_template = getattr(request.user.profile, 'default_template', 'classic')
        form = ResumeForm(initial={'template_style': default_template})

    return render(request, 'resumes/resume_create.html', {'form': form})


def _save_education(request, resume):
    """Save education entries from POST data"""
    schools = request.POST.getlist('education_school')
    degrees = request.POST.getlist('education_degree')
    fields = request.POST.getlist('education_field')
    starts = request.POST.getlist('education_start')
    ends = request.POST.getlist('education_end')
    descs = request.POST.getlist('education_desc')
    for i, school in enumerate(schools):
        if school:
            start_str = starts[i] if i < len(starts) else ''
            end_str = ends[i] if i < len(ends) else ''
            ResumeEducation.objects.create(
                resume=resume,
                school=school,
                degree=degrees[i] if i < len(degrees) else '',
                field_of_study=fields[i] if i < len(fields) else '',
                start_date=start_str or None,
                end_date=end_str or None,
                description=descs[i] if i < len(descs) else '',
            )


def _save_experience(request, resume):
    """Save experience entries from POST data"""
    companies = request.POST.getlist('experience_company')
    is_current_list = request.POST.getlist('experience_is_current')
    titles = request.POST.getlist('experience_title')
    locations = request.POST.getlist('experience_location')
    starts = request.POST.getlist('experience_start')
    ends = request.POST.getlist('experience_end')
    descs = request.POST.getlist('experience_desc')
    for i, company in enumerate(companies):
        if company:
            start_str = starts[i] if i < len(starts) else ''
            end_str = ends[i] if i < len(ends) else ''
            ResumeExperience.objects.create(
                resume=resume,
                company=company,
                job_title=titles[i] if i < len(titles) else '',
                location=locations[i] if i < len(locations) else '',
                start_date=start_str or None,
                end_date=end_str or None,
                is_current='on' in is_current_list,
                description=descs[i] if i < len(descs) else '',
            )


def _save_projects(request, resume):
    """Save project entries from POST data"""
    names = request.POST.getlist('project_name')
    roles = request.POST.getlist('project_role')
    starts = request.POST.getlist('project_start')
    ends = request.POST.getlist('project_end')
    descs = request.POST.getlist('project_desc')
    urls = request.POST.getlist('project_url')
    for i, name in enumerate(names):
        if name:
            start_str = starts[i] if i < len(starts) else ''
            end_str = ends[i] if i < len(ends) else ''
            ResumeProject.objects.create(
                resume=resume,
                name=name,
                role=roles[i] if i < len(roles) else '',
                start_date=start_str or None,
                end_date=end_str or None,
                description=descs[i] if i < len(descs) else '',
                url=urls[i] if i < len(urls) else '',
            )


def _save_skills(request, resume):
    """Save skills from POST data"""
    names = request.POST.getlist('skill_name')
    proficiencies = request.POST.getlist('skill_proficiency')
    for i, name in enumerate(names):
        if name:
            ResumeSkill.objects.create(
                resume=resume,
                name=name,
                proficiency=proficiencies[i] if i < len(proficiencies) else '',
            )


@login_required
def resume_list(request):
    """List all user's resumes"""
    resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'resumes/resume_list.html', {'resumes': resumes})


def _get_user_resume_or_403(request, resume_id):
    """Fetch a resume owned by the current user, or raise PermissionDenied."""
    resume = get_object_or_404(Resume, id=resume_id)
    if resume.user != request.user:
        raise PermissionDenied
    return resume


@login_required
def resume_update(request, resume_id):
    """Two-panel resume builder."""
    resume = _get_user_resume_or_403(request, resume_id)

    if request.method == 'POST':
        form = ResumeForm(request.POST, instance=resume)
        if form.is_valid():
            # Save personal info fields
            resume.full_name = request.POST.get('full_name', '')
            resume.email = request.POST.get('email', '')
            resume.phone = request.POST.get('phone', '')
            resume.location = request.POST.get('location', '')
            resume.linkedin = request.POST.get('linkedin', '')
            resume.github = request.POST.get('github', '')
            resume.website = request.POST.get('website', '')
            resume.professional_summary = request.POST.get('professional_summary', '')
            form.save()

            # Clear existing and re-save sections
            resume.education.all().delete()
            resume.experience.all().delete()
            resume.projects.all().delete()
            resume.skills.all().delete()

            _save_education(request, resume)
            _save_experience(request, resume)
            _save_projects(request, resume)
            _save_skills(request, resume)

            messages.success(request, 'Resume updated successfully!')
            return redirect('resume_list')
    else:
        form = ResumeForm(instance=resume)

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

    return render(request, 'resumes/resume_builder.html', {
        'form': form,
        'resume': resume,
        'progress_pct': progress_pct,
        'progress_text': progress_text,
    })


@login_required
def resume_delete(request, resume_id):
    """Delete a resume"""
    resume = _get_user_resume_or_403(request, resume_id)

    if request.method == 'POST':
        resume.delete()
        messages.success(request, 'Resume deleted successfully.')
        return redirect('resume_list')

    return render(request, 'resumes/resume_delete.html', {'resume': resume})


@login_required
def resume_preview(request, resume_id):
    """Preview a resume"""
    resume = _get_user_resume_or_403(request, resume_id)
    return render(request, 'resumes/resume_preview.html', {'resume': resume})


@login_required
def set_primary_resume(request, resume_id):
    """Set a resume as primary"""
    if request.method == 'POST':
        # Unset all other primaries
        Resume.objects.filter(user=request.user, is_primary=True).update(is_primary=False)

        # Set this one as primary
        resume = _get_user_resume_or_403(request, resume_id)
        resume.is_primary = True
        resume.save()

        messages.success(request, f'{resume.title} set as primary resume.')
        return redirect('resume_list')

    return redirect('resume_list')


@login_required
def resume_duplicate(request, resume_id):
    """Duplicate an existing resume."""
    source = _get_user_resume_or_403(request, resume_id)
    with transaction.atomic():
        new_resume = Resume.objects.create(
            user=request.user,
            title=f"Copy of {source.title}",
            is_primary=False,
            status='draft',
            copied_from=source,
            full_name=source.full_name,
            email=source.email,
            phone=source.phone,
            location=source.location,
            linkedin=source.linkedin,
            github=source.github,
            website=source.website,
            professional_summary=source.professional_summary,
            template_style=source.template_style,
        )
        for edu in source.education.all():
            edu.pk = None
            edu.resume = new_resume
            edu.save()
        for exp in source.experience.all():
            exp.pk = None
            exp.resume = new_resume
            exp.save()
        for proj in source.projects.all():
            proj.pk = None
            proj.resume = new_resume
            proj.save()
        for skill in source.skills.all():
            skill.pk = None
            skill.resume = new_resume
            skill.save()
    messages.success(request, f'"{source.title}" duplicated successfully.')
    return redirect('resume_list')


class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def get_object(self):
        resume = get_object_or_404(Resume, id=self.kwargs['pk'])
        if resume.user != self.request.user:
            raise PermissionDenied
        return resume

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


def resume_preview_fragment(request, resume_id):
    """Returns just the resume content HTML for live preview refresh."""
    resume = _get_user_resume_or_403(request, resume_id)
    template_name = f"resumes/resume_{resume.template_style}.html"
    return render(request, template_name, {'resume': resume})


def _format_date(date_obj):
    """Format a date as 'Jan. Y'."""
    if not date_obj:
        return ''
    if hasattr(date_obj, 'strftime'):
        return date_obj.strftime('%b. %Y')
    return str(date_obj)


def _check_page_break(c, y, margin_bottom=36):
    """If y is below threshold, start a new page and return new y."""
    if y < margin_bottom + 60:
        c.showPage()
        return letter[1] - 36
    return y


@login_required
def resume_export_pdf(request, resume_id):
    """Generate and download a PDF of the resume using reportlab."""
    resume = _get_user_resume_or_403(request, resume_id)

    buffer = BytesIO()
    page_width, page_height = letter
    margin = 0.5 * inch
    left = margin
    right = page_width - margin
    top = page_height - margin
    y = top

    c = canvas.Canvas(buffer, pagesize=letter)
    c.setTitle(resume.title)

    FONT_NAME = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'
    FONT_ITALIC = 'Helvetica-Oblique'

    # Header - name
    if resume.full_name:
        name_text = resume.full_name.upper()
    else:
        name_text = resume.title.upper()
    c.setFont(FONT_BOLD, 16)
    c.drawCentredString(page_width / 2, y, name_text)
    y -= 16

    # Contact line
    contact_parts = []
    if resume.email:
        contact_parts.append(resume.email)
    if resume.phone:
        contact_parts.append(resume.phone)
    if resume.location:
        contact_parts.append(resume.location)
    if resume.linkedin:
        contact_parts.append(resume.linkedin)
    if resume.github:
        contact_parts.append(resume.github)
    if resume.website:
        contact_parts.append(resume.website)

    if contact_parts:
        c.setFont(FONT_NAME, 9)
        contact_line = '  |  '.join(contact_parts)
        c.drawCentredString(page_width / 2, y, contact_line)
        y -= 14

    # Divider
    y -= 4
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.setLineWidth(1)
    c.line(left, y, right, y)
    y -= 14

    def draw_section_title(title):
        nonlocal y
        y = _check_page_break(c, y)
        c.setFont(FONT_BOLD, 11)
        c.setFillColorRGB(0.15, 0.15, 0.15)
        c.drawString(left, y, title.upper())
        y -= 14
        c.setFillColorRGB(0.1, 0.1, 0.1)

    c.setFillColorRGB(0.1, 0.1, 0.1)

    # Experience
    if resume.experience.exists():
        draw_section_title('Experience')
        for exp in resume.experience.all():
            y = _check_page_break(c, y)
            date_str = ''
            if exp.start_date:
                date_str = _format_date(exp.start_date)
                if exp.end_date:
                    date_str += ' - ' + _format_date(exp.end_date)
                elif exp.is_current:
                    date_str += ' - Present'
            c.setFont(FONT_BOLD, 10)
            c.drawString(left, y, exp.job_title or '')
            if date_str:
                c.setFont(FONT_NAME, 9)
                c.drawRightString(right, y, date_str)
            y -= 12
            if exp.company:
                c.setFont(FONT_ITALIC, 9)
                c.setFillColorRGB(0.27, 0.27, 0.27)
                loc_str = exp.company + (f', {exp.location}' if exp.location else '')
                c.drawString(left, y, loc_str)
                y -= 12
            if exp.description:
                c.setFont(FONT_NAME, 9)
                c.setFillColorRGB(0.1, 0.1, 0.1)
                for line in exp.description.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    y = _check_page_break(c, y)
                    c.drawString(left + 12, y, f'\u2022 {line}')
                    y -= 11
            y -= 4

    # Education
    if resume.education.exists():
        draw_section_title('Education')
        for edu in resume.education.all():
            y = _check_page_break(c, y)
            date_str = ''
            if edu.start_date:
                date_str = str(edu.start_date.year)
                if edu.end_date:
                    date_str += f' - {edu.end_date.year}'
            c.setFont(FONT_BOLD, 10)
            c.drawString(left, y, edu.school or '')
            if date_str:
                c.setFont(FONT_NAME, 9)
                c.drawRightString(right, y, date_str)
            y -= 12
            c.setFont(FONT_ITALIC, 9)
            c.setFillColorRGB(0.27, 0.27, 0.27)
            deg_str = edu.degree or ''
            if edu.field_of_study:
                deg_str += f' in {edu.field_of_study}'
            if edu.gpa:
                deg_str += f'  |  GPA: {edu.gpa}'
            c.drawString(left, y, deg_str)
            y -= 12
            if edu.description:
                c.setFont(FONT_NAME, 9)
                c.setFillColorRGB(0.1, 0.1, 0.1)
                for line in edu.description.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    y = _check_page_break(c, y)
                    c.drawString(left + 12, y, f'\u2022 {line}')
                    y -= 11
            y -= 4

    # Projects
    if resume.projects.exists():
        draw_section_title('Projects')
        for proj in resume.projects.all():
            y = _check_page_break(c, y)
            date_str = ''
            if proj.start_date:
                date_str = _format_date(proj.start_date)
                if proj.end_date:
                    date_str += ' - ' + _format_date(proj.end_date)
            c.setFont(FONT_BOLD, 10)
            c.drawString(left, y, proj.name or '')
            if date_str:
                c.setFont(FONT_NAME, 9)
                c.drawRightString(right, y, date_str)
            y -= 12
            if proj.role:
                c.setFont(FONT_ITALIC, 9)
                c.setFillColorRGB(0.27, 0.27, 0.27)
                c.drawString(left, y, proj.role)
                y -= 12
            if proj.description:
                c.setFont(FONT_NAME, 9)
                c.setFillColorRGB(0.1, 0.1, 0.1)
                for line in proj.description.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    y = _check_page_break(c, y)
                    c.drawString(left + 12, y, f'\u2022 {line}')
                    y -= 11
            y -= 4

    # Skills
    if resume.skills.exists():
        draw_section_title('Skills')
        by_prof = {}
        for skill in resume.skills.all():
            prof = skill.proficiency or ''
            by_prof.setdefault(prof, []).append(skill.name)
        for prof, names in by_prof.items():
            y = _check_page_break(c, y)
            c.setFont(FONT_NAME, 9)
            c.setFillColorRGB(0.1, 0.1, 0.1)
            if prof:
                c.drawString(left, y, f'{prof}: {", ".join(names)}')
            else:
                c.drawString(left, y, ', '.join(names))
            y -= 12

    c.save()

    # Build filename
    if resume.full_name:
        safe_name = re.sub(r'[^\w\- ]', '', resume.full_name).strip().replace(' ', '_')
        filename = f"{safe_name}_Resume.pdf"
    else:
        safe_title = re.sub(r'[^\w\- ]', '', resume.title).strip().replace(' ', '_')
        filename = f"{safe_title}.pdf"

    pdf_data = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def cover_letter_page(request, resume_id):
    """Cover letter generation page."""
    resume = _get_user_resume_or_403(request, resume_id)
    tier = getattr(request.user, 'profile', None)
    current_tier = tier.subscription_tier if tier else 'free'
    daily_limit = settings.COVER_LETTER_RATE_LIMITS.get(current_tier, 0)
    from ai.rate_limiter import get_coverletter_remaining
    remaining = get_coverletter_remaining(request.user.id, daily_limit)
    return render(request, 'resumes/cover_letter.html', {
        'resume': resume,
        'tier': current_tier,
        'remaining': remaining,
        'limit': daily_limit,
    })


@login_required
def job_match_page(request, resume_id):
    """Job Match page — paste a job description and rewrite resume sections."""
    resume = _get_user_resume_or_403(request, resume_id)
    tier = getattr(request.user, 'profile', None)
    current_tier = tier.subscription_tier if tier else 'free'
    return render(request, 'resumes/job_match.html', {
        'resume': resume,
        'tier': current_tier,
    })


def ats_score_page(request, resume_id):
    """ATS Score Checker page — analyze resume against a job description."""
    resume = _get_user_resume_or_403(request, resume_id)
    tier = getattr(request.user, 'profile', None)
    current_tier = tier.subscription_tier if tier else 'free'
    return render(request, 'resumes/ats_score.html', {
        'resume': resume,
        'tier': current_tier,
    })


@login_required
def salary_calculator_page(request):
    """Salary Calculator page — no resume needed."""
    tier = getattr(request.user, 'profile', None)
    current_tier = tier.subscription_tier if tier else 'free'
    return render(request, 'resumes/salary_calculator.html', {
        'tier': current_tier,
    })
