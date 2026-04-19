from django.db import models
from django.contrib.auth.models import User


class Resume(models.Model):
    """Main resume model - each user can have multiple resumes"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='resumes'
    )
    title = models.CharField(max_length=255)

    # Personal Information
    full_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    website = models.URLField(blank=True)

    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # New fields
    professional_summary = models.TextField(max_length=500, blank=True)
    template_style = models.CharField(max_length=20, default='classic')  # classic | modern | minimal
    status = models.CharField(max_length=20, default='draft')  # draft | complete

    copied_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='copies'
    )

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    @property
    def computed_status(self):
        has_personal = bool(self.full_name and self.email)
        has_entries = self.education.exists() or self.experience.exists()
        return 'complete' if (has_personal and has_entries) else 'draft'


class ResumeEducation(models.Model):
    """Education section of a resume"""
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='education'
    )
    order = models.PositiveIntegerField(default=0)
    school = models.CharField(max_length=255)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    gpa = models.CharField(max_length=10, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['order', '-start_date']

    def __str__(self):
        return f"{self.degree} at {self.school}"


class ResumeExperience(models.Model):
    """Work experience section of a resume"""
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='experience'
    )
    order = models.PositiveIntegerField(default=0)
    company = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['order', '-start_date']

    def __str__(self):
        return f"{self.job_title} at {self.company}"


class ResumeProject(models.Model):
    """Project section of a resume"""
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='projects'
    )
    order = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    url = models.URLField(blank=True)

    class Meta:
        ordering = ['order', '-start_date']

    def __str__(self):
        return self.name


class ResumeSkill(models.Model):
    """Skills section of a resume"""
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='skills'
    )
    name = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=50, blank=True)  # Beginner, Intermediate, Advanced, Expert

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


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