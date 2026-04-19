from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def template_gallery(request):
    """Show all available resume templates with preview."""
    templates = [
        {
            'id': 'classic',
            'name': 'Classic',
            'description': 'Traditional, serif fonts, standard margins — conservative and widely accepted across industries.',
            'best_for': 'Conservative industries: law, finance, government',
            'ats_friendly': True,
        },
        {
            'id': 'modern',
            'name': 'Modern',
            'description': 'Sans-serif, strong visual hierarchy, blue accents — clean and contemporary.',
            'best_for': 'Tech, startup, creative roles',
            'ats_friendly': True,
        },
        {
            'id': 'minimal',
            'name': 'Minimal',
            'description': 'Maximum whitespace, simple typography — elegant and highly ATS-friendly.',
            'best_for': 'All industries, ATS-optimized applications',
            'ats_friendly': True,
        },
    ]
    return render(request, 'resumes/template_gallery.html', {'templates': templates})


@login_required
def template_preview(request, template_id):
    """Render a sample resume in the specified template for gallery preview."""
    valid_templates = ['classic', 'modern', 'minimal']
    if template_id not in valid_templates:
        template_id = 'classic'

    # Create a minimal sample resume for preview
    class SampleResume:
        def __init__(self, data):
            for k, v in data.items():
                setattr(self, k, v)

        def __iter__(self):
            return iter([])

        def exists(self):
            return False

        def all(self):
            return []

        def count(self):
            return 0

        def filter(self, *a, **k):
            return type('empty', (), {
                'exists': lambda: False,
                'all': lambda: [],
                'count': lambda: 0
            })()

    sample_data = {
        'id': 0,
        'title': 'Sarah Chen',
        'full_name': 'Sarah Chen',
        'email': 'sarah.chen@email.com',
        'phone': '(555) 123-4567',
        'location': 'San Francisco, CA',
        'linkedin': 'linkedin.com/in/sarahchen',
        'github': '',
        'website': '',
        'professional_summary': 'Experienced software engineer with 5+ years building scalable web applications. Passionate about clean code and user experience.',
        'template_style': template_id,
        'status': 'complete',
        'is_primary': False,
        'copied_from': None,
    }
    sample = SampleResume(sample_data)
    template_name = f'resumes/resume_{template_id}.html'
    return render(request, template_name, {'resume': sample})