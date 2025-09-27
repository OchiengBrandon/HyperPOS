# pos_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import RedirectView
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('pos/', include('pos_app.urls')),
    # Add favicon redirect to avoid 404
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]

# Static and media files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Only serve media files through Django in development
# On cPanel, Apache serves media files directly from public_html/media/
if not getattr(settings, 'CPANEL', False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

