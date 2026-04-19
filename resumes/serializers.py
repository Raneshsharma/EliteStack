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
