"""Resume admin — registers all resume models to the shared placement admin site."""
from django.contrib import admin
from placement_copilot.admin import placement_admin_site
from .models import Resume, ResumeEducation, ResumeExperience, ResumeProject, ResumeSkill, CoverLetter


class EducationInline(admin.TabularInline):
    model = ResumeEducation
    extra = 1
    ordering = ['order', '-start_date']


class ExperienceInline(admin.TabularInline):
    model = ResumeExperience
    extra = 1
    ordering = ['order', '-start_date']


class ProjectInline(admin.TabularInline):
    model = ResumeProject
    extra = 1
    ordering = ['order', '-start_date']


class SkillInline(admin.TabularInline):
    model = ResumeSkill
    extra = 3


class ResumeAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'is_primary', 'template_style', 'status', 'created_at', 'updated_at']
    list_filter = ['is_primary', 'template_style', 'status', 'created_at']
    list_editable = ['template_style', 'status']
    search_fields = ['title', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'copied_from']
    ordering = ['-updated_at']
    inlines = [EducationInline, ExperienceInline, ProjectInline, SkillInline]

    fieldsets = (
        (None, {'fields': ('user', 'title', 'is_primary')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


class ResumeEducationAdmin(admin.ModelAdmin):
    list_display = ['school', 'degree', 'resume', 'start_date', 'end_date']
    list_filter = ['start_date']
    search_fields = ['school', 'degree', 'resume__title']


class ResumeExperienceAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'company', 'resume', 'start_date', 'is_current']
    list_filter = ['is_current', 'start_date']
    search_fields = ['company', 'job_title', 'resume__title']


class ResumeProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'resume', 'start_date', 'end_date']
    search_fields = ['name', 'resume__title']


class ResumeSkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'proficiency', 'resume']
    list_filter = ['proficiency']
    search_fields = ['name', 'resume__title']


class CoverLetterAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'company_name', 'resume', 'word_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['job_title', 'company_name', 'resume__user__username']


placement_admin_site.register(Resume, ResumeAdmin)
placement_admin_site.register(ResumeEducation, ResumeEducationAdmin)
placement_admin_site.register(ResumeExperience, ResumeExperienceAdmin)
placement_admin_site.register(ResumeProject, ResumeProjectAdmin)
placement_admin_site.register(ResumeSkill, ResumeSkillAdmin)
placement_admin_site.register(CoverLetter, CoverLetterAdmin)
