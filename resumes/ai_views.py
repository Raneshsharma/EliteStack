"""AI-powered API endpoints for resume features."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.http import HttpResponse
from .models import Resume, CoverLetter
from .serializers import ResumeSerializer
from ai.services import generate_resume_rewrites, generate_cover_letter, generate_job_match
from ai.rate_limiter import get_rewrite_remaining, record_rewrite, get_coverletter_remaining, record_coverletter


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


def serialize_resume_text(resume: Resume) -> str:
    """Serialize a resume's key fields into a single text block for the AI."""
    lines = []
    if resume.full_name:
        lines.append(f"Name: {resume.full_name}")
    if resume.email:
        lines.append(f"Email: {resume.email}")
    if resume.professional_summary:
        lines.append(f"Summary: {resume.professional_summary}")

    for edu in resume.education.all():
        lines.append(f"Education: {edu.degree} at {edu.school} ({str(edu.start_date) if edu.start_date else '?'} - {str(edu.end_date) if edu.end_date else 'Present'})")
    for exp in resume.experience.all():
        lines.append(f"Experience: {exp.job_title} at {exp.company} ({str(exp.start_date) if exp.start_date else '?'} - {str(exp.end_date) if exp.end_date else 'Present'})")
        if exp.description:
            lines.append(f"  {exp.description}")
    for proj in resume.projects.all():
        lines.append(f"Project: {proj.name} - {proj.description or ''}")
    for skill in resume.skills.all():
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


class JobMatchView(APIView):
    """POST /api/resumes/<id>/job-match/ — rewrite resume sections to match a job description."""
    permission_classes = [IsAuthenticated]

    def post(self, request, resume_id):
        resume = Resume.objects.filter(user=request.user, id=resume_id).first()
        if not resume:
            return Response({'error': 'Resume not found.'}, status=status.HTTP_404_NOT_FOUND)

        tier = getattr(request.user, 'profile', None)
        current_tier = tier.subscription_tier if tier else 'free'

        if current_tier == 'free':
            return Response(
                {
                    'error': 'upgrade_required',
                    'message': 'Job Match is available on Pro and Premium plans.',
                    'tier': current_tier,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        job_description = request.data.get('job_description', '').strip()
        if not job_description:
            return Response(
                {'error': 'job_description is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(job_description) > 5000:
            return Response(
                {'error': 'Job description exceeds 5,000 characters. Please paste a shorter excerpt.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(job_description) < 50:
            return Response(
                {'error': 'Job description is too short for accurate matching. Paste more content.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sections_raw = request.data.get('sections', ['experience', 'skills', 'summary'])
        if isinstance(sections_raw, str):
            sections = [s.strip() for s in sections_raw.split(',') if s.strip()]
        else:
            sections = sections_raw

        resume_data = serialize_resume_text(resume)
        if not resume_data.strip():
            return Response(
                {'error': 'Your resume has no content. Add some information first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = generate_job_match(resume_data, job_description, sections)
        except Exception as e:
            import logging
            logging.error(f"Job match failed for user {request.user.id}: {e}")
            return Response(
                {'error': 'Job matching failed. Please try again.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({
            'match_score': result.get('match_score', 0),
            'rewritten_sections': result.get('rewritten_sections', {}),
            'keywords_found': result.get('keywords_found', []),
            'keywords_matched': result.get('keywords_matched', []),
            'recommendations': result.get('recommendations', []),
        })