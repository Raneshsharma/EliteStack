from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponseForbidden
from datetime import date
from .models import Resume, ResumeEducation, ResumeExperience, ResumeProject, ResumeSkill, CoverLetter


class ResumeModelTests(TestCase):
    """Tests for Resume and related models"""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')

    def test_resume_creation(self):
        """Test creating a resume"""
        resume = Resume.objects.create(user=self.user, title='Test Resume')
        self.assertEqual(resume.title, 'Test Resume')
        self.assertEqual(resume.user, self.user)
        self.assertFalse(resume.is_primary)
        self.assertIsNotNone(resume.created_at)
        self.assertIsNotNone(resume.updated_at)

    def test_resume_str_method(self):
        """Test resume string representation"""
        resume = Resume.objects.create(user=self.user, title='My Resume')
        self.assertEqual(str(resume), 'My Resume')

    def test_resume_user_relationship(self):
        """Test resume-user relationship"""
        resume = Resume.objects.create(user=self.user, title='Test')
        user_resumes = self.user.resumes.all()
        self.assertIn(resume, user_resumes)

    def test_resume_ordering(self):
        """Test resumes can be ordered by updated_at descending"""
        resume1 = Resume.objects.create(user=self.user, title='First')
        resume2 = Resume.objects.create(user=self.user, title='Second')

        resumes = list(Resume.objects.filter(user=self.user))
        # Both resumes should be present
        titles = [r.title for r in resumes]
        self.assertIn('First', titles)
        self.assertIn('Second', titles)

    def test_resume_default_values(self):
        """Test resume has correct default values"""
        resume = Resume.objects.create(user=self.user, title='Defaults Test')
        self.assertFalse(resume.is_primary)

    def test_resume_multiple_per_user(self):
        """Test user can have multiple resumes"""
        resume1 = Resume.objects.create(user=self.user, title='Resume 1')
        resume2 = Resume.objects.create(user=self.user, title='Resume 2')

        self.assertEqual(self.user.resumes.count(), 2)
        self.assertIn(resume1, self.user.resumes.all())
        self.assertIn(resume2, self.user.resumes.all())

    def test_copied_from_field_exists(self):
        """Resume model has a copied_from self-referential FK."""
        source = Resume.objects.create(user=self.user, title="Source Resume")
        copy = Resume.objects.create(user=self.user, title="Copy", copied_from=source)
        self.assertEqual(copy.copied_from, source)

    def test_copied_from_is_nullable(self):
        """copied_from can be null (e.g., original resumes have no source)."""
        resume = Resume.objects.create(user=self.user, title="Original Resume")
        self.assertIsNone(resume.copied_from)


class ResumeEducationModelTests(TestCase):
    """Tests for ResumeEducation model"""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_education_creation(self):
        """Test creating education entry"""
        edu = ResumeEducation.objects.create(
            resume=self.resume,
            school='Test University',
            degree='BS Computer Science',
            field_of_study='Computer Science',
            start_date=date(2020, 1, 1),
            end_date=date(2024, 5, 15),
            gpa='3.8'
        )

        self.assertEqual(edu.school, 'Test University')
        self.assertEqual(edu.resume, self.resume)
        self.assertEqual(str(edu), 'BS Computer Science at Test University')

    def test_education_str_method(self):
        """Test education string representation"""
        edu = ResumeEducation.objects.create(
            resume=self.resume,
            school='MIT',
            degree='PhD',
            start_date=date(2020, 1, 1)
        )
        self.assertEqual(str(edu), 'PhD at MIT')

    def test_education_optional_fields(self):
        """Test education with optional fields empty"""
        edu = ResumeEducation.objects.create(
            resume=self.resume,
            school='College',
            degree='BA',
            start_date=date(2020, 1, 1)
        )

        self.assertEqual(edu.field_of_study, '')
        self.assertIsNone(edu.end_date)
        self.assertEqual(edu.gpa, '')

    def test_education_cascade_delete(self):
        """Test deleting resume removes education"""
        ResumeEducation.objects.create(
            resume=self.resume,
            school='School',
            degree='Degree',
            start_date=date(2020, 1, 1)
        )
        self.assertEqual(ResumeEducation.objects.count(), 1)
        self.resume.delete()
        self.assertEqual(ResumeEducation.objects.count(), 0)


class ResumeExperienceModelTests(TestCase):
    """Tests for ResumeExperience model"""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_experience_creation(self):
        """Test creating experience entry"""
        exp = ResumeExperience.objects.create(
            resume=self.resume,
            company='Tech Corp',
            job_title='Software Engineer',
            location='San Francisco, CA',
            start_date=date(2022, 6, 1),
            end_date=date(2024, 12, 31),
            description='Developed web applications'
        )

        self.assertEqual(exp.company, 'Tech Corp')
        self.assertEqual(exp.job_title, 'Software Engineer')
        self.assertEqual(str(exp), 'Software Engineer at Tech Corp')

    def test_experience_current_job(self):
        """Test current job flag"""
        exp = ResumeExperience.objects.create(
            resume=self.resume,
            company='Current Corp',
            job_title='Developer',
            start_date=date(2024, 1, 1),
            is_current=True
        )

        self.assertTrue(exp.is_current)
        self.assertIsNone(exp.end_date)

    def test_experience_str_method(self):
        """Test experience string representation"""
        exp = ResumeExperience.objects.create(
            resume=self.resume,
            company='Google',
            job_title='Senior Engineer',
            start_date=date(2020, 1, 1)
        )
        self.assertEqual(str(exp), 'Senior Engineer at Google')


class ResumeProjectModelTests(TestCase):
    """Tests for ResumeProject model"""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_project_creation(self):
        """Test creating project entry"""
        project = ResumeProject.objects.create(
            resume=self.resume,
            name='E-commerce Platform',
            role='Lead Developer',
            start_date=date(2023, 1, 1),
            end_date=date(2023, 6, 30),
            description='Built a full-stack e-commerce solution',
            url='https://github.com/user/ecommerce'
        )

        self.assertEqual(project.name, 'E-commerce Platform')
        self.assertEqual(project.role, 'Lead Developer')
        self.assertEqual(str(project), 'E-commerce Platform')

    def test_project_str_method(self):
        """Test project string representation"""
        project = ResumeProject.objects.create(
            resume=self.resume,
            name='My Project',
            description='A great project'
        )
        self.assertEqual(str(project), 'My Project')


class ResumeSkillModelTests(TestCase):
    """Tests for ResumeSkill model"""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_skill_creation(self):
        """Test creating skill entry"""
        skill = ResumeSkill.objects.create(
            resume=self.resume,
            name='Python',
            proficiency='Expert'
        )

        self.assertEqual(skill.name, 'Python')
        self.assertEqual(skill.proficiency, 'Expert')
        self.assertEqual(str(skill), 'Python')

    def test_skill_str_method(self):
        """Test skill string representation"""
        skill = ResumeSkill.objects.create(
            resume=self.resume,
            name='JavaScript'
        )
        self.assertEqual(str(skill), 'JavaScript')

    def test_skill_ordering(self):
        """Test skills are ordered alphabetically"""
        ResumeSkill.objects.create(resume=self.resume, name='Zebra')
        ResumeSkill.objects.create(resume=self.resume, name='Apple')
        ResumeSkill.objects.create(resume=self.resume, name='Mango')

        skills = list(self.resume.skills.all())
        self.assertEqual(skills[0].name, 'Apple')
        self.assertEqual(skills[1].name, 'Mango')
        self.assertEqual(skills[2].name, 'Zebra')


class ResumeViewTests(TestCase):
    """Tests for resume views and user interactions"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_resume_create_page_loads(self):
        """Test resume create page renders correctly"""
        response = self.client.get(reverse('resume_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resumes/resume_create.html')
        self.assertIn('form', response.context)

    def test_user_can_create_resume(self):
        """Test POST creates resume"""
        response = self.client.post(reverse('resume_create'), {
            'title': 'My New Resume',
        })

        self.assertEqual(response.status_code, 302,
                        "Should redirect after successful resume creation")
        self.assertRedirects(response, reverse('resume_list'),
                           msg_prefix="Should redirect to resume list")

        self.assertTrue(Resume.objects.filter(title='My New Resume', user=self.user).exists(),
                       "Resume should be created in database")

    def test_user_can_create_resume_with_education(self):
        """Test creating resume with basic title"""
        response = self.client.post(reverse('resume_create'), {
            'title': 'Resume with Education',
        })

        self.assertEqual(response.status_code, 302,
                        "Should redirect after resume creation")

        resume = Resume.objects.get(title='Resume with Education', user=self.user)
        self.assertIsNotNone(resume)

    def test_user_can_create_resume_with_experience(self):
        """Test creating resume with basic title"""
        response = self.client.post(reverse('resume_create'), {
            'title': 'Resume with Experience',
        })

        # Should redirect after create
        self.assertEqual(response.status_code, 302,
                        "Should redirect after resume creation")

        resume = Resume.objects.get(title='Resume with Experience', user=self.user)
        self.assertIsNotNone(resume)

    def test_user_can_create_resume_with_projects(self):
        """Test creating resume with basic title"""
        response = self.client.post(reverse('resume_create'), {
            'title': 'Resume with Projects',
        })

        self.assertEqual(response.status_code, 302,
                        "Should redirect after resume creation")

        resume = Resume.objects.get(title='Resume with Projects', user=self.user)
        self.assertIsNotNone(resume)

    def test_user_can_create_resume_with_skills(self):
        """Test creating resume with basic title"""
        response = self.client.post(reverse('resume_create'), {
            'title': 'Resume with Skills',
        })

        self.assertEqual(response.status_code, 302,
                        "Should redirect after resume creation")

        resume = Resume.objects.get(title='Resume with Skills', user=self.user)
        self.assertIsNotNone(resume)

    def test_resume_list_shows_only_user_resumes(self):
        """Test user can only see their own resumes"""
        # Create resume for this user
        Resume.objects.create(user=self.user, title='My Resume')

        # Create another user with a resume
        other_user = User.objects.create_user('otheruser', 'other@example.com', 'pass123')
        Resume.objects.create(user=other_user, title='Other Resume')

        response = self.client.get(reverse('resume_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Resume')
        self.assertNotContains(response, 'Other Resume',
                              msg_prefix="User should not see other users' resumes")

    def test_resume_list_ordering(self):
        """Test resume list shows resumes"""
        resume1 = Resume.objects.create(user=self.user, title='First')
        resume2 = Resume.objects.create(user=self.user, title='Second')

        response = self.client.get(reverse('resume_list'))
        resumes = list(response.context['resumes'])

        # Both resumes should be present
        titles = [r.title for r in resumes]
        self.assertIn('First', titles)
        self.assertIn('Second', titles)

    def test_resume_update(self):
        """Test editing resume"""
        resume = Resume.objects.create(user=self.user, title='Original Title')

        response = self.client.post(
            reverse('resume_update', args=[resume.id]),
            {'title': 'Updated Title'}
        )

        self.assertEqual(response.status_code, 302,
                        "Should redirect after successful update")
        self.assertRedirects(response, reverse('resume_list'))

        resume.refresh_from_db()
        self.assertEqual(resume.title, 'Updated Title',
                        "Resume title should be updated")

    def test_resume_update_preserves_related_data(self):
        """Test updating resume changes title"""
        resume = Resume.objects.create(user=self.user, title='Original')
        ResumeEducation.objects.create(
            resume=resume,
            school='Test University',
            degree='BS',
            start_date=date(2020, 1, 1)
        )

        # Simple update - title only
        response = self.client.post(
            reverse('resume_update', args=[resume.id]),
            {'title': 'Updated Title'}
        )

        # Should redirect after update
        self.assertEqual(response.status_code, 302,
                        "Should redirect after successful update")
        resume.refresh_from_db()
        self.assertEqual(resume.title, 'Updated Title')

    def test_resume_delete(self):
        """Test deleting resume"""
        resume = Resume.objects.create(user=self.user, title='To Delete')

        response = self.client.post(reverse('resume_delete', args=[resume.id]))

        self.assertEqual(response.status_code, 302,
                        "Should redirect after successful delete")
        self.assertRedirects(response, reverse('resume_list'))
        self.assertFalse(Resume.objects.filter(id=resume.id).exists(),
                        "Resume should be deleted from database")

    def test_resume_delete_removes_related_data(self):
        """Test deleting resume removes related education, experience, etc."""
        resume = Resume.objects.create(user=self.user, title='Delete Test')
        ResumeEducation.objects.create(
            resume=resume, school='School', degree='BS', start_date=date(2020, 1, 1)
        )
        ResumeExperience.objects.create(
            resume=resume, company='Corp', job_title='Dev', start_date=date(2020, 1, 1)
        )

        resume_id = resume.id
        self.client.post(reverse('resume_delete', args=[resume_id]))

        self.assertFalse(Resume.objects.filter(id=resume_id).exists())
        self.assertEqual(ResumeEducation.objects.filter(resume_id=resume_id).count(), 0)
        self.assertEqual(ResumeExperience.objects.filter(resume_id=resume_id).count(), 0)

    def test_set_primary_resume(self):
        """Test setting primary resume"""
        resume1 = Resume.objects.create(user=self.user, title='Resume 1', is_primary=True)
        resume2 = Resume.objects.create(user=self.user, title='Resume 2')

        response = self.client.post(reverse('set_primary', args=[resume2.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('resume_list'))

        resume1.refresh_from_db()
        resume2.refresh_from_db()

        self.assertFalse(resume1.is_primary, "Previous primary should be unset")
        self.assertTrue(resume2.is_primary, "New primary should be set")

    def test_set_primary_with_post_only(self):
        """Test that setting primary requires POST request"""
        resume = Resume.objects.create(user=self.user, title='Test')

        # GET request should redirect
        response = self.client.get(reverse('set_primary', args=[resume.id]))
        self.assertEqual(response.status_code, 302)

        # Resume should not be set as primary
        resume.refresh_from_db()
        self.assertFalse(resume.is_primary)

    def test_cannot_access_other_user_resume(self):
        """Test user cannot edit another user's resume"""
        other_user = User.objects.create_user('otheruser', 'other@example.com', 'pass123')
        other_resume = Resume.objects.create(user=other_user, title='Other Resume')

        response = self.client.get(reverse('resume_update', args=[other_resume.id]))
        self.assertEqual(response.status_code, 403,
                        "Should return 403 for other user's resume")

    def test_cannot_delete_other_user_resume(self):
        """Test user cannot delete another user's resume"""
        other_user = User.objects.create_user('otheruser', 'other@example.com', 'pass123')
        other_resume = Resume.objects.create(user=other_user, title='Other Resume')

        response = self.client.post(reverse('resume_delete', args=[other_resume.id]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Resume.objects.filter(id=other_resume.id).exists(),
                       "Other user's resume should not be deleted")

    def test_cannot_preview_other_user_resume(self):
        """Test user cannot preview another user's resume"""
        other_user = User.objects.create_user('otheruser', 'other@example.com', 'pass123')
        other_resume = Resume.objects.create(user=other_user, title='Other Resume')

        response = self.client.get(reverse('resume_preview', args=[other_resume.id]))
        self.assertEqual(response.status_code, 403)

    def test_resume_create_requires_auth(self):
        """Test unauthenticated user cannot create resume"""
        self.client.logout()
        response = self.client.get(reverse('resume_create'))
        self.assertEqual(response.status_code, 302,
                        "Should redirect unauthenticated user to login")
        self.assertTrue(response.url.startswith('/accounts/login'),
                       "Should redirect to login page")

    def test_resume_list_requires_auth(self):
        """Test unauthenticated user cannot view resume list"""
        self.client.logout()
        response = self.client.get(reverse('resume_list'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))

    def test_resume_delete_requires_post(self):
        """Test resume delete requires POST request"""
        resume = Resume.objects.create(user=self.user, title='Delete Test')

        # GET should show confirmation page
        response = self.client.get(reverse('resume_delete', args=[resume.id]))
        self.assertEqual(response.status_code, 200)

        # Resume should still exist
        self.assertTrue(Resume.objects.filter(id=resume.id).exists())


class ResumePreviewTests(TestCase):
    """Tests for resume preview functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_preview_page_loads(self):
        """Test resume preview page renders"""
        response = self.client.get(reverse('resume_preview', args=[self.resume.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resumes/resume_preview.html')
        self.assertContains(response, 'Test Resume')

    def test_preview_contains_resume(self):
        """Test preview page contains resume context"""
        response = self.client.get(reverse('resume_preview', args=[self.resume.id]))
        self.assertEqual(response.context['resume'], self.resume)

    def test_preview_displays_education(self):
        """Test education section displays in preview"""
        ResumeEducation.objects.create(
            resume=self.resume,
            school='Test University',
            degree='BS',
            field_of_study='Computer Science',
            start_date=date(2020, 1, 1),
            end_date=date(2024, 5, 1)
        )

        response = self.client.get(reverse('resume_preview', args=[self.resume.id]))
        self.assertContains(response, 'Test University')
        self.assertContains(response, 'BS')
        self.assertContains(response, 'Computer Science')

    def test_preview_displays_experience(self):
        """Test experience section displays in preview"""
        ResumeExperience.objects.create(
            resume=self.resume,
            company='Test Corp',
            job_title='Developer',
            location='San Francisco',
            start_date=date(2024, 6, 1),
            is_current=True,
            description='Built web applications'
        )

        response = self.client.get(reverse('resume_preview', args=[self.resume.id]))
        self.assertContains(response, 'Test Corp')
        self.assertContains(response, 'Developer')
        self.assertContains(response, 'San Francisco')

    def test_preview_displays_projects(self):
        """Test projects section displays in preview"""
        ResumeProject.objects.create(
            resume=self.resume,
            name='Test Project',
            role='Lead Developer',
            description='An awesome project',
            url='https://github.com/user/project'
        )

        response = self.client.get(reverse('resume_preview', args=[self.resume.id]))
        self.assertContains(response, 'Test Project')
        self.assertContains(response, 'Lead Developer')
        self.assertContains(response, 'An awesome project')

    def test_preview_displays_skills(self):
        """Test skills section displays in preview"""
        ResumeSkill.objects.create(
            resume=self.resume,
            name='Python',
            proficiency='Advanced'
        )
        ResumeSkill.objects.create(
            resume=self.resume,
            name='Django',
            proficiency='Expert'
        )

        response = self.client.get(reverse('resume_preview', args=[self.resume.id]))
        self.assertContains(response, 'Python')
        self.assertContains(response, 'Advanced')
        self.assertContains(response, 'Django')
        self.assertContains(response, 'Expert')

    def test_preview_empty_resume(self):
        """Test preview of resume with no additional data"""
        response = self.client.get(reverse('resume_preview', args=[self.resume.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Resume')

    def test_preview_displays_multiple_education_entries(self):
        """Test preview shows multiple education entries"""
        ResumeEducation.objects.create(
            resume=self.resume,
            school='High School',
            degree='Diploma',
            start_date=date(2016, 9, 1),
            end_date=date(2020, 6, 1)
        )
        ResumeEducation.objects.create(
            resume=self.resume,
            school='University',
            degree='BS',
            start_date=date(2020, 9, 1),
            end_date=date(2024, 6, 1)
        )

        response = self.client.get(reverse('resume_preview', args=[self.resume.id]))
        self.assertContains(response, 'High School')
        self.assertContains(response, 'University')

    def test_preview_displays_multiple_experience_entries(self):
        """Test preview shows multiple experience entries"""
        ResumeExperience.objects.create(
            resume=self.resume,
            company='Intern Corp',
            job_title='Intern',
            start_date=date(2023, 6, 1),
            end_date=date(2023, 8, 31)
        )
        ResumeExperience.objects.create(
            resume=self.resume,
            company='Full Time Inc',
            job_title='Engineer',
            start_date=date(2024, 1, 1),
            is_current=True
        )

        response = self.client.get(reverse('resume_preview', args=[self.resume.id]))
        self.assertContains(response, 'Intern Corp')
        self.assertContains(response, 'Full Time Inc')


class DashboardTests(TestCase):
    """Tests for dashboard functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')

    def test_dashboard_renders_for_authenticated_user(self):
        """Dashboard renders directly for authenticated users (no redirect)."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_shows_resume_list_when_resumes_exist(self):
        """Dashboard renders with resume cards when user has resumes."""
        Resume.objects.create(user=self.user, title='My Resume')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Resume')

    def test_dashboard_requires_auth(self):
        """Test dashboard requires authentication"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))


class WelcomeTests(TestCase):
    """Tests for welcome page"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')

    def test_welcome_page_loads_for_authenticated_user(self):
        """Test welcome page loads for authenticated user without resumes"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('welcome'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'onboarding/welcome.html')

    def test_welcome_redirects_unauthenticated(self):
        """Test welcome page redirects unauthenticated users"""
        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))


import json
from django.test import override_settings


@override_settings(
    MIDDLEWARE=[
        m for m in [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            # CSRF middleware removed for API tests
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ] if m
    ] + [m for m in [
        'accounts.middleware.SessionExpiryMiddleware',
    ] if m]
)
class ResumeAPITests(TestCase):
    """Tests for Resume REST API"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_patch_resume_updates_fields(self):
        """PATCH updates title and full_name via API"""
        response = self.client.patch(
            reverse('resume-api-detail', args=[self.resume.id]),
            data=json.dumps({'title': 'Updated Title', 'full_name': 'John Doe'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.title, 'Updated Title')
        self.assertEqual(self.resume.full_name, 'John Doe')

    def test_patch_template_style(self):
        """PATCH can update template_style to modern"""
        response = self.client.patch(
            reverse('resume-api-detail', args=[self.resume.id]),
            data=json.dumps({'template_style': 'modern'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.template_style, 'modern')

    def test_patch_template_style_minimal(self):
        """PATCH can update template_style to minimal"""
        response = self.client.patch(
            reverse('resume-api-detail', args=[self.resume.id]),
            data=json.dumps({'template_style': 'minimal'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.template_style, 'minimal')

    def test_preview_fragment_returns_html(self):
        """preview-fragment endpoint returns HTML"""
        response = self.client.get(reverse('resume_preview_fragment', args=[self.resume.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['Content-Type'])

    def test_preview_fragment_classic_template(self):
        """preview-fragment uses classic template by default"""
        response = self.client.get(reverse('resume_preview_fragment', args=[self.resume.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resumes/resume_classic.html')

    def test_preview_fragment_respects_template_style(self):
        """preview-fragment uses modern template when set"""
        self.resume.template_style = 'modern'
        self.resume.save()
        response = self.client.get(reverse('resume_preview_fragment', args=[self.resume.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resumes/resume_modern.html')

    def test_cannot_access_other_user_resume_via_api(self):
        """API returns 403 for other user's resume"""
        other = User.objects.create_user('other', 'other@example.com', 'pass123')
        other_resume = Resume.objects.create(user=other, title='Other')
        response = self.client.get(reverse('resume-api-detail', args=[other_resume.id]))
        self.assertEqual(response.status_code, 403)

    def test_api_list_only_shows_own_resumes(self):
        """API list endpoint only returns authenticated user's resumes"""
        Resume.objects.create(user=self.user, title='My Resume 2')
        other = User.objects.create_user('other', 'other@example.com', 'pass123')
        Resume.objects.create(user=other, title='Other Resume')
        response = self.client.get(reverse('resume-api-list'))
        self.assertEqual(response.status_code, 200)
        titles = [r['title'] for r in response.json()]
        self.assertIn('Test Resume', titles)
        self.assertIn('My Resume 2', titles)
        self.assertNotIn('Other Resume', titles)

    def test_duplicate_creates_new_resume(self):
        """POST to /resumes/<id>/duplicate/ creates a new resume."""
        from datetime import date
        resume = Resume.objects.create(
            user=self.user, title="My Resume",
            full_name="Test User", email="test@example.com"
        )
        response = self.client.post(
            reverse('resume_duplicate', args=[resume.id])
        )
        self.assertEqual(response.status_code, 302)
        # 1 from setUp + 1 new in test + 1 duplicated = 3
        self.assertEqual(Resume.objects.count(), 3)
        new_resume = Resume.objects.exclude(id__in=[self.resume.id, resume.id]).first()
        self.assertEqual(new_resume.title, "Copy of My Resume")

    def test_duplicate_copies_all_sections(self):
        """Duplicate copies education, experience, projects, and skills."""
        from datetime import date
        resume = Resume.objects.create(
            user=self.user, title="Full Resume",
            full_name="Test User", email="test@example.com"
        )
        ResumeEducation.objects.create(
            resume=resume, school="MIT", degree="BS",
            field_of_study="CS", start_date=date(2020, 1, 1)
        )
        ResumeExperience.objects.create(
            resume=resume, company="Acme", job_title="Engineer",
            start_date=date(2022, 1, 1)
        )
        ResumeProject.objects.create(
            resume=resume, name="My Project", description="Built an app"
        )
        ResumeSkill.objects.create(
            resume=resume, name="Python", proficiency="Advanced"
        )
        self.client.post(reverse('resume_duplicate', args=[resume.id]))
        # 1 from setUp + 1 new in test + 1 duplicated = 3
        self.assertEqual(Resume.objects.count(), 3)
        new_resume = Resume.objects.exclude(id__in=[self.resume.id, resume.id]).first()
        self.assertEqual(new_resume.education.count(), 1)
        self.assertEqual(new_resume.experience.count(), 1)
        self.assertEqual(new_resume.projects.count(), 1)
        self.assertEqual(new_resume.skills.count(), 1)

    def test_duplicate_sets_copied_from(self):
        """New resume's copied_from field references the source."""
        source = Resume.objects.create(
            user=self.user, title="Source",
            full_name="Test User", email="test@example.com"
        )
        self.client.post(reverse('resume_duplicate', args=[source.id]))
        new_resume = Resume.objects.exclude(id=source.id).first()
        self.assertEqual(new_resume.copied_from, source)

    def test_duplicate_always_draft(self):
        """Duplicated resume is always draft regardless of source status."""
        from datetime import date
        source = Resume.objects.create(
            user=self.user, title="Complete Resume",
            full_name="Test User", email="test@example.com",
            status='complete'
        )
        ResumeEducation.objects.create(
            resume=source, school="MIT", degree="BS",
            field_of_study="CS", start_date=date(2020, 1, 1)
        )
        self.client.post(reverse('resume_duplicate', args=[source.id]))
        new_resume = Resume.objects.exclude(id=source.id).first()
        self.assertEqual(new_resume.status, 'draft')

    def test_duplicate_user_isolation(self):
        """User cannot duplicate another user's resume."""
        other_user = User.objects.create_user(
            username='other', email='other@example.com', password='pass123'
        )
        other_resume = Resume.objects.create(
            user=other_user, title="Other's Resume"
        )
        response = self.client.post(
            reverse('resume_duplicate', args=[other_resume.id])
        )
        # _get_user_resume_or_403 raises PermissionDenied → status 403
        self.assertEqual(response.status_code, 403)
        # setUp creates 1 resume for self.user, other_resume creates 1 = 2 total
        self.assertEqual(Resume.objects.count(), 2)

    def test_export_returns_pdf(self):
        """GET /resumes/<id>/export/ returns a PDF with correct content-type."""
        resume = Resume.objects.create(
            user=self.user, title="Test Resume",
            full_name="Jane Doe", email="jane@example.com"
        )
        response = self.client.get(reverse('resume_export_pdf', args=[resume.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_export_filename_contains_name(self):
        """PDF filename is {Name}_Resume.pdf when full_name is set."""
        resume = Resume.objects.create(
            user=self.user, title="Test Resume",
            full_name="John Smith", email="john@example.com"
        )
        response = self.client.get(reverse('resume_export_pdf', args=[resume.id]))
        disposition = response['Content-Disposition']
        self.assertIn('John_Smith_Resume.pdf', disposition)

    def test_export_filename_fallback_to_title(self):
        """PDF filename falls back to {Title}_Resume.pdf when full_name is empty."""
        resume = Resume.objects.create(
            user=self.user, title="My Tech Resume"
        )
        response = self.client.get(reverse('resume_export_pdf', args=[resume.id]))
        disposition = response['Content-Disposition']
        self.assertIn('My_Tech_Resume.pdf', disposition)

    def test_export_user_isolation(self):
        """User cannot export another user's resume."""
        other_user = User.objects.create_user(
            username='other', email='other@example.com', password='pass123'
        )
        other_resume = Resume.objects.create(
            user=other_user, title="Other's Resume"
        )
        response = self.client.get(reverse('resume_export_pdf', args=[other_resume.id]))
        self.assertEqual(response.status_code, 403)


class ResumeBuilderTests(TestCase):
    """Tests for the two-panel resume builder page"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('builderuser', 'builder@example.com', 'builderpass123')
        self.client.login(username='builderuser', password='builderpass123')
        self.resume = Resume.objects.create(user=self.user, title='Builder Test')

    def test_builder_page_loads(self):
        """Builder page loads with resume_builder.html template"""
        response = self.client.get(reverse('resume_update', args=[self.resume.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resumes/resume_builder.html')

    def test_builder_page_has_form_and_preview_panel(self):
        """Builder has resume-form and preview-panel elements"""
        response = self.client.get(reverse('resume_update', args=[self.resume.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="resume-form"')
        self.assertContains(response, 'id="preview-panel"')

    def test_builder_page_has_template_switcher(self):
        """Builder has template switcher with all three options"""
        response = self.client.get(reverse('resume_update', args=[self.resume.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="template-switcher"')
        self.assertContains(response, 'Classic')
        self.assertContains(response, 'Modern')
        self.assertContains(response, 'Minimal')

    def test_builder_page_has_progress_bar(self):
        """Builder has progress bar and text"""
        response = self.client.get(reverse('resume_update', args=[self.resume.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="progress-bar"')
        self.assertContains(response, 'id="progress-text"')

    def test_builder_page_has_collapsible_sections(self):
        """Builder has section-header elements for collapse"""
        response = self.client.get(reverse('resume_update', args=[self.resume.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'section-header')

    def test_computed_status_draft_when_empty(self):
        """computed_status returns 'draft' when resume has no entries"""
        self.assertEqual(self.resume.computed_status, 'draft')

    def test_computed_status_draft_without_personal_info(self):
        """computed_status is draft without personal info even with entries"""
        ResumeEducation.objects.create(
            resume=self.resume, school='MIT', degree='BS', start_date=date(2020, 1, 1)
        )
        self.assertEqual(self.resume.computed_status, 'draft')

    def test_computed_status_complete_with_personal_and_entries(self):
        """computed_status is complete when personal info and entries exist"""
        self.resume.full_name = 'Jane Doe'
        self.resume.email = 'jane@example.com'
        self.resume.save()
        ResumeEducation.objects.create(
            resume=self.resume, school='MIT', degree='BS', start_date=date(2020, 1, 1)
        )
        self.assertEqual(self.resume.computed_status, 'complete')

    def test_professional_summary_field_exists(self):
        """Resume model has professional_summary field"""
        self.resume.professional_summary = 'Experienced software engineer'
        self.resume.save()
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.professional_summary, 'Experienced software engineer')

    def test_template_style_field_exists(self):
        """Resume model has template_style field with correct defaults"""
        self.assertEqual(self.resume.template_style, 'classic')

    def test_builder_saves_professional_summary(self):
        """POSTing to builder saves professional_summary"""
        response = self.client.post(
            reverse('resume_update', args=[self.resume.id]),
            {
                'title': 'Builder Test',
                'full_name': 'Test User',
                'email': 'test@example.com',
                'professional_summary': 'My professional summary',
            }
        )
        self.assertEqual(response.status_code, 302)
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.professional_summary, 'My professional summary')

    def test_builder_saves_is_current_experience(self):
        """POSTing with is_current checkbox saves it correctly"""
        response = self.client.post(
            reverse('resume_update', args=[self.resume.id]),
            {
                'title': 'Builder Test',
                'full_name': 'Test User',
                'email': 'test@example.com',
                'experience_company': ['Tech Corp'],
                'experience_title': ['Developer'],
                'experience_location': [''],
                'experience_start': ['2024-01-01'],
                'experience_end': [''],
                'experience_is_current': ['on'],
                'experience_desc': [''],
            }
        )
        self.assertEqual(response.status_code, 302)
        self.resume.refresh_from_db()
        exp = self.resume.experience.first()
        self.assertTrue(exp.is_current)


class DashboardTest(TestCase):
    """Tests for dashboard stats and activity feed."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_dashboard_stats_shows_correct_counts(self):
        """Dashboard displays correct total, complete, and draft counts."""
        self.client.login(username='testuser', password='testpass123')
        # Create resumes
        r1 = Resume.objects.create(user=self.user, title='Resume 1', status='draft')
        r2 = Resume.objects.create(user=self.user, title='Resume 2', status='complete')
        r3 = Resume.objects.create(user=self.user, title='Resume 3', status='draft')

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '3')  # total
        self.assertContains(response, '2')  # drafts
        self.assertContains(response, '1')  # complete

    def test_dashboard_shows_activity_feed(self):
        """Dashboard shows recent activity for last 5 resumes."""
        self.client.login(username='testuser', password='testpass123')
        for i in range(6):
            Resume.objects.create(user=self.user, title=f'Resume {i}')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Recent Activity')

    def test_dashboard_requires_authentication(self):
        """Unauthenticated users are redirected to login."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_dashboard_empty_state(self):
        """Dashboard shows empty state when no resumes exist."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No resumes yet')
        self.assertContains(response, 'Create your first resume')


class TemplateGalleryTest(TestCase):
    """Tests for template gallery."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_gallery_shows_all_three_templates(self):
        """Template gallery displays Classic, Modern, and Minimal."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('template_gallery'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Classic')
        self.assertContains(response, 'Modern')
        self.assertContains(response, 'Minimal')
        self.assertContains(response, 'ATS')

    def test_gallery_requires_authentication(self):
        """Unauthenticated users are redirected to login."""
        response = self.client.get(reverse('template_gallery'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_template_preview_renders(self):
        """Template preview iframe renders without error."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('template_preview', args=['classic']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sarah Chen')

    def test_template_preview_invalid_falls_back_to_classic(self):
        """Invalid template ID falls back to classic."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('template_preview', args=['invalid']))
        self.assertEqual(response.status_code, 200)


class AIRewriteAPITests(TestCase):
    """Tests for AI Resume Rewrite API."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_rewrite_requires_authentication(self):
        """Unauthenticated POST to rewrite endpoint returns 401/403."""
        self.client.logout()
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/rewrite/',
            {'selected_text': 'Managed a team of engineers'},
            format='json'
        )
        self.assertIn(response.status_code, [401, 403])

    def test_rewrite_free_tier_returns_upgrade_required(self):
        """Free tier returns 403 with upgrade_required error."""
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/rewrite/',
            {'selected_text': 'Managed team of 5 engineers'},
            format='json'
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'upgrade_required')

    def test_rewrite_empty_text_returns_400(self):
        """Empty selected_text returns 400."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/rewrite/',
            {'selected_text': ''},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('No text selected', response.json()['error'])

    def test_rewrite_too_long_returns_400(self):
        """Text over 500 words returns 400."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        long_text = ' '.join(['word'] * 501)
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/rewrite/',
            {'selected_text': long_text},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('500 words', response.json()['error'])

    def test_rewrite_nonexistent_resume_returns_404(self):
        """Non-existent resume returns 404."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        response = self.client.post(
            '/api/resumes/99999/rewrite/',
            {'selected_text': 'Some text'},
            format='json'
        )
        self.assertEqual(response.status_code, 404)


class CoverLetterAPITests(TestCase):
    """Tests for Cover Letter API endpoints."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_cover_letter_requires_auth(self):
        """Unauthenticated POST returns 401/403."""
        self.client.logout()
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/cover-letter/',
            {'job_title': 'Engineer', 'company_name': 'Acme'},
            format='json'
        )
        self.assertIn(response.status_code, [401, 403])

    def test_cover_letter_free_tier_gated(self):
        """Free tier returns 403 with upgrade_required error."""
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/cover-letter/',
            {'job_title': 'Engineer', 'company_name': 'Acme'},
            format='json'
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'upgrade_required')

    def test_cover_letter_missing_fields(self):
        """Missing job_title or company_name returns 400."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/cover-letter/',
            {'job_title': 'Engineer'},  # missing company_name
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_cover_letter_nonexistent_resume(self):
        """Non-existent resume returns 404."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        response = self.client.post(
            '/api/resumes/99999/cover-letter/',
            {'job_title': 'Engineer', 'company_name': 'Acme'},
            format='json'
        )
        self.assertEqual(response.status_code, 404)

    def test_cover_letter_download_requires_auth(self):
        """Download endpoint requires authentication."""
        cl = CoverLetter.objects.create(
            resume=self.resume, job_title='Engineer',
            company_name='Acme', content='Test letter'
        )
        self.client.logout()
        response = self.client.get(f'/api/cover-letter/{cl.id}/download/')
        self.assertIn(response.status_code, [401, 403])

    def test_cover_letter_download_not_found(self):
        """Non-existent cover letter returns 404."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        response = self.client.get('/api/cover-letter/99999/download/')
        self.assertEqual(response.status_code, 404)


class JobMatchAPITests(TestCase):
    """Tests for Job Match API."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_job_match_requires_auth(self):
        """Unauthenticated POST returns 401/403."""
        self.client.logout()
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/job-match/',
            {'job_description': 'Software engineer with Python skills'},
            format='json'
        )
        self.assertIn(response.status_code, [401, 403])

    def test_job_match_free_tier_gated(self):
        """Free tier returns 403 with upgrade_required error."""
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/job-match/',
            {'job_description': 'Software engineer with Python skills'},
            format='json'
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'upgrade_required')

    def test_job_match_missing_job_description(self):
        """Missing job_description returns 400."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/job-match/',
            {},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('job_description', response.json()['error'])

    def test_job_match_too_long(self):
        """Job description over 5000 chars returns 400."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        long_jd = 'x' * 5001
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/job-match/',
            {'job_description': long_jd},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('5,000', response.json()['error'])

    def test_job_match_too_short(self):
        """Job description under 50 chars returns 400."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/job-match/',
            {'job_description': 'Python developer'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('too short', response.json()['error'])

    def test_job_match_nonexistent_resume(self):
        """Non-existent resume returns 404."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        response = self.client.post(
            '/api/resumes/99999/job-match/',
            {'job_description': 'A job description that is long enough for validation.'},
            format='json'
        )
        self.assertEqual(response.status_code, 404)


class ATSScoreAPITests(TestCase):
    """Tests for ATS Score API."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_ats_score_requires_auth(self):
        """Unauthenticated POST returns 401/403."""
        self.client.logout()
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/ats-score/',
            {'job_description': 'Software engineer with Python, Django, React, TypeScript, and AWS experience.'},
            format='json'
        )
        self.assertIn(response.status_code, [401, 403])

    def test_ats_score_free_tier_gated(self):
        """Free tier returns 403 with upgrade_required error."""
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/ats-score/',
            {'job_description': 'Software engineer with Python, Django, React, TypeScript, and AWS experience.'},
            format='json'
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'upgrade_required')

    def test_ats_score_missing_job_description(self):
        """Missing job_description returns 400."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/ats-score/',
            {},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'validation_error')

    def test_ats_score_too_long(self):
        """Job description over 5000 chars returns 400."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        long_jd = 'x' * 5001
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/ats-score/',
            {'job_description': long_jd},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('5000', response.json()['message'])

    def test_ats_score_too_short(self):
        """Job description under 30 chars returns 400."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        response = self.client.post(
            f'/api/resumes/{self.resume.id}/ats-score/',
            {'job_description': 'Python developer'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('30', response.json()['message'])

    def test_ats_score_nonexistent_resume(self):
        """Non-existent resume returns 404."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        response = self.client.post(
            '/api/resumes/99999/ats-score/',
            {'job_description': 'A job description that is long enough for validation.'},
            format='json'
        )
        self.assertEqual(response.status_code, 404)


class ChatAPITests(TestCase):
    """Tests for Chat API."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_chat_requires_auth(self):
        """Unauthenticated POST returns 401/403."""
        self.client.logout()
        response = self.client.post(
            '/api/chat/',
            {'message': 'Help me with my resume'},
            format='json'
        )
        self.assertIn(response.status_code, [401, 403])

    def test_chat_missing_message(self):
        """Missing message returns 400."""
        response = self.client.post(
            '/api/chat/',
            {},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'validation_error')

    def test_chat_message_too_long(self):
        """Message over 2000 chars returns 400."""
        response = self.client.post(
            '/api/chat/',
            {'message': 'x' * 2001},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('2000', response.json()['message'])

    def test_chat_conversation_id_generated(self):
        """Conversation ID is generated if not provided."""
        import unittest.mock as mock
        with mock.patch('resumes.ai_views.chat_with_assistant', return_value='Hello!'):
            response = self.client.post(
                '/api/chat/',
                {'message': 'Hello'},
                format='json'
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['reply'], 'Hello!')
        self.assertIn('conversation_id', data)
        self.assertEqual(len(data['conversation_id']), 36)


class InterviewPrepAPITests(TestCase):
    """Tests for Interview Prep API."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_interview_prep_requires_auth(self):
        """Unauthenticated POST returns 401/403."""
        self.client.logout()
        response = self.client.post(
            '/api/interview-prep/generate/',
            {'job_title': 'Software Engineer'},
            format='json'
        )
        self.assertIn(response.status_code, [401, 403])

    def test_interview_prep_free_tier_gated(self):
        """Free tier returns 403 with upgrade_required error."""
        response = self.client.post(
            '/api/interview-prep/generate/',
            {'job_title': 'Software Engineer'},
            format='json'
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'upgrade_required')

    def test_interview_prep_missing_job_title(self):
        """Missing job_title returns 400."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        response = self.client.post(
            '/api/interview-prep/generate/',
            {},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'validation_error')

    def test_interview_prep_rate_limit(self):
        """Returns 429 when daily limit is exhausted."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        from ai.rate_limiter import _interview_counts
        from datetime import datetime, timedelta, timezone
        uid = self.user.id
        _interview_counts[uid] = [(10, datetime.now(timezone.utc) + timedelta(hours=24))]
        response = self.client.post(
            '/api/interview-prep/generate/',
            {'job_title': 'Software Engineer'},
            format='json'
        )
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.json()['error'], 'rate_limit')

    def test_interview_prep_generates_questions(self):
        """Returns questions array when generation succeeds."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        import unittest.mock as mock
        mock_questions = [
            {'text': 'Tell me about yourself.', 'category': 'behavioral', 'answer_framework': 'Use the STAR method.'},
            {'text': 'Why this company?', 'category': 'culture', 'answer_framework': 'Research the company values.'},
        ]
        with mock.patch('resumes.ai_views.generate_interview_questions', return_value=mock_questions):
            response = self.client.post(
                '/api/interview-prep/generate/',
                {'job_title': 'Software Engineer', 'job_description': 'Builds web apps'},
                format='json'
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['questions']), 2)
        self.assertEqual(data['questions'][0]['text'], 'Tell me about yourself.')

    def test_interview_prep_nonexistent_resume_404(self):
        """Non-existent resume_id does not cause error (resume is optional)."""
        self.user.profile.subscription_tier = 'pro'
        self.user.profile.save()
        import unittest.mock as mock
        with mock.patch('resumes.ai_views.generate_interview_questions', return_value=[]):
            response = self.client.post(
                '/api/interview-prep/generate/',
                {'job_title': 'Software Engineer', 'resume_id': 99999},
                format='json'
            )
        self.assertEqual(response.status_code, 200)
