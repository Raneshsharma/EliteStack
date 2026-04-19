from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views, template_views, ai_views

router = DefaultRouter()
router.register(r'api/resumes', views.ResumeViewSet, basename='resume-api')

urlpatterns = [
    path('api/resumes/<int:resume_id>/rewrite/', ai_views.ResumeRewriteView.as_view(), name='resume_rewrite'),
    path('api/resumes/<int:resume_id>/cover-letter/', ai_views.CoverLetterGenerateView.as_view(), name='cover_letter_generate'),
    path('api/resumes/<int:resume_id>/job-match/', ai_views.JobMatchView.as_view(), name='job_match'),
    path('api/cover-letter/<int:letter_id>/download/', ai_views.CoverLetterDownloadView.as_view(), name='cover_letter_download'),
    path('resumes/<int:resume_id>/cover-letter/', views.cover_letter_page, name='cover_letter_page'),
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('welcome/', views.welcome, name='welcome'),
    path('resumes/create/', views.resume_create, name='resume_create'),
    path('resumes/', views.resume_list, name='resume_list'),
    path('resumes/<int:resume_id>/edit/', views.resume_update, name='resume_update'),
    path('resumes/<int:resume_id>/delete/', views.resume_delete, name='resume_delete'),
    path('resumes/<int:resume_id>/preview/', views.resume_preview, name='resume_preview'),
    path('resumes/<int:resume_id>/set-primary/', views.set_primary_resume, name='set_primary'),
    path('resumes/<int:resume_id>/duplicate/', views.resume_duplicate, name='resume_duplicate'),
    path('resumes/<int:resume_id>/preview-fragment/', views.resume_preview_fragment, name='resume_preview_fragment'),
    path('resumes/<int:resume_id>/export/', views.resume_export_pdf, name='resume_export_pdf'),
    path('templates/', template_views.template_gallery, name='template_gallery'),
    path('templates/<str:template_id>/preview/', template_views.template_preview, name='template_preview'),
] + router.urls
