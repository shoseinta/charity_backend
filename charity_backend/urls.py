"""
URL configuration for charity_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
import silk

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user-api/', include('user.api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('charity-platform/', include('charity.api.urls')),
    path('beneficiary-platform/', include('beneficiary.api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('silk/', include('silk.urls', namespace='silk')),
    #path('__debug__/', include('debug_toolbar.urls')),
]

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from django.views.static import serve
import os


BASE_DIR = settings.BASE_DIR

urlpatterns  += [
    # your other paths here...
    
    # Serve /request_docs/ URLs from custom folder
    path('request_docs/<path:path>/', serve, {
        'document_root': os.path.join(BASE_DIR, 'request_docs'),
    }),
]
