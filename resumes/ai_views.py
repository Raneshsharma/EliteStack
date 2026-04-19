"""AI-powered API endpoints for resume features."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.http import HttpResponse
from .models import Resume
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