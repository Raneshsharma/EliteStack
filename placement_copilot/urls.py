"""
URL configuration for Placement Copilot project.
"""
from django.urls import path, include
from placement_copilot.admin import placement_admin_site

urlpatterns = [
    path('admin/', placement_admin_site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('resumes.urls')),
]
