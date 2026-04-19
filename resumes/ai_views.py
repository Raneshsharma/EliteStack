"""AI-powered API endpoints for resume features."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.http import HttpResponse
from .models import Resume, CoverLetter, ChatMessage
from .serializers import ResumeSerializer
from ai.services import generate_resume_rewrites, generate_cover_letter, generate_job_match, analyze_ats_score, chat_with_assistant, generate_interview_questions
from ai.rate_limiter import (
    record_ats, record_chat, get_rewrite_remaining, record_rewrite,
    get_coverletter_remaining, record_coverletter, get_chat_remaining,
    get_interview_remaining, record_interview,
)
from ai.salary_data import calculate_salary, get_offer_assessment, get_all_titles


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


class ATSScoreView(APIView):
    """POST /api/resumes/<id>/ats-score/ — analyze resume against job description."""
    permission_classes = [IsAuthenticated]

    def post(self, request, resume_id):
        user = request.user
        profile = getattr(user, 'profile', None)
        tier = profile.subscription_tier if profile else 'free'
        limit = settings.ATS_SCORE_RATE_LIMITS.get(tier, 0)

        if limit == 0:
            return Response(
                {'error': 'upgrade_required', 'message': 'Upgrade to Pro or Premium to use ATS scoring.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        job_description = request.data.get('job_description', '').strip()
        if len(job_description) < 30:
            return Response(
                {'error': 'validation_error', 'message': 'Job description must be at least 30 characters.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(job_description) > 5000:
            return Response(
                {'error': 'validation_error', 'message': 'Job description must be under 5000 characters.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            resume = Resume.objects.get(id=resume_id, user=user)
        except Resume.DoesNotExist:
            return Response(
                {'error': 'not_found', 'message': 'Resume not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        resume_text = serialize_resume_text(resume)
        result = analyze_ats_score(resume_text, job_description)

        remaining = record_ats(user.id, limit)

        return Response({
            'overall_score': result.get('overall_score', 0),
            'keyword_score': result.get('keyword_score', 0),
            'formatting_score': result.get('formatting_score', 0),
            'readability_score': result.get('readability_score', 0),
            'length_score': result.get('length_score', 0),
            'missing_keywords': result.get('missing_keywords', []),
            'matched_keywords': result.get('matched_keywords', []),
            'recommendations': result.get('recommendations', []),
            'remaining': remaining,
        })


class ChatView(APIView):
    """POST /api/chat/ — conversational AI chat. Free tier gets 5/day."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        profile = getattr(user, 'profile', None)
        tier = profile.subscription_tier if profile else 'free'
        daily_limit = settings.AI_CHAT_RATE_LIMITS.get(tier, 5)

        allowed = record_chat(user.id, daily_limit)
        if not allowed:
            return Response(
                {'error': 'rate_limited', 'message': 'Daily chat limit reached. Upgrade for more.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        remaining = get_chat_remaining(user.id, daily_limit)

        message = request.data.get('message', '').strip()
        if not message:
            return Response(
                {'error': 'validation_error', 'message': 'Message is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(message) > 2000:
            return Response(
                {'error': 'validation_error', 'message': 'Message must be under 2000 characters.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation_id = request.data.get('conversation_id', '')
        if not conversation_id:
            import uuid
            conversation_id = str(uuid.uuid4())

        # Build message history from prior messages in this conversation
        prior = ChatMessage.objects.filter(
            user=user,
            conversation_id=conversation_id
        ).order_by('created_at').values('role', 'content')

        messages = [{'role': m['role'], 'content': m['content']} for m in prior]
        messages.append({'role': 'user', 'content': message})

        reply = chat_with_assistant(messages)

        # Persist both user message and assistant reply
        ChatMessage.objects.create(user=user, conversation_id=conversation_id, role='user', content=message)
        ChatMessage.objects.create(user=user, conversation_id=conversation_id, role='assistant', content=reply)

        return Response({
            'reply': reply,
            'conversation_id': conversation_id,
            'remaining': remaining,
        })


class SalaryCalculatorView(APIView):
    """GET /api/salary/calculate/ — salary estimates by title, level, location."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        tier = profile.subscription_tier if profile else 'free'

        title = request.query_params.get('title', '').strip()
        level = request.query_params.get('level', 'mid').strip().lower()
        location = request.query_params.get('location', '').strip()

        if not title:
            return Response(
                {'error': 'validation_error', 'message': 'Job title is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if level not in ('entry', 'mid', 'senior', 'lead'):
            level = 'mid'

        salary_data = calculate_salary(title, level, location)
        if 'error' in salary_data:
            return Response(salary_data, status=status.HTTP_404_NOT_FOUND)

        # Free tier: only show median (hide min/max)
        if tier == 'free':
            salary_data = {
                'title': salary_data['title'],
                'level': salary_data['level'],
                'location': salary_data['location'],
                'currency': salary_data['currency'],
                'median': salary_data['median'],
                'limited': True,
                'message': 'Upgrade to Pro or Premium to see full salary ranges.',
            }

        return Response(salary_data)


class SalaryOfferView(APIView):
    """POST /api/salary/offer/ — compare an offer against market data."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        title = request.data.get('title', '').strip()
        level = request.data.get('level', 'mid').strip().lower()
        location = request.data.get('location', '').strip()
        offer = request.data.get('offer')

        if not title:
            return Response({'error': 'validation_error', 'message': 'Job title is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if offer is None:
            return Response({'error': 'validation_error', 'message': 'Offer amount is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            offer = int(float(offer))
            if offer < 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response({'error': 'validation_error', 'message': 'Offer must be a positive number.'}, status=status.HTTP_400_BAD_REQUEST)

        salary_data = calculate_salary(title, level, location)
        if 'error' in salary_data:
            return Response(salary_data, status=status.HTTP_404_NOT_FOUND)

        assessment = get_offer_assessment(offer, salary_data)
        assessment['salary_data'] = salary_data
        return Response(assessment)


class SalaryTitlesView(APIView):
    """GET /api/salary/titles/ — return all supported job titles for autocomplete."""
    permission_classes = [IsAuthenticated]

    def get(self, _request):
        return Response({'titles': get_all_titles()})


class InterviewPrepView(APIView):
    """POST /api/interview-prep/generate/ — generate interview questions."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = getattr(request.user, 'profile', None)
        tier = profile.subscription_tier if profile else 'free'
        daily_limit = settings.INTERVIEW_PREP_RATE_LIMITS.get(tier, 0)

        if daily_limit == 0:
            return Response(
                {'error': 'upgrade_required', 'message': 'Upgrade to Pro or Premium to use Interview Prep.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        job_title = request.data.get('job_title', '').strip()
        job_description = request.data.get('job_description', '').strip()
        resume_id = request.data.get('resume_id')

        if not job_title:
            return Response(
                {'error': 'validation_error', 'message': 'job_title is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        remaining = get_interview_remaining(request.user.id, daily_limit)
        if remaining <= 0:
            return Response(
                {'error': 'rate_limit', 'message': 'Daily Interview Prep limit reached.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        resume_data = ""
        if resume_id:
            resume = Resume.objects.filter(user=request.user, id=resume_id).first()
            if resume:
                resume_data = serialize_resume_text(resume)

        try:
            questions = generate_interview_questions(
                resume_data=resume_data,
                job_title=job_title,
                job_description=job_description[:3000] if job_description else "",
            )
        except Exception as e:
            import logging
            logging.error(f"Interview prep failed for user {request.user.id}: {e}")
            return Response(
                {'error': 'Failed to generate questions. Please try again.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        record_interview(request.user.id, daily_limit)
        return Response({
            'questions': questions,
            'remaining': get_interview_remaining(request.user.id, daily_limit),
        })