"""
URL configuration for hostel_management project.

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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('students/', include('students.urls')),
    path('wardens/', include('wardens.urls')),
    path('admin-panel/', include('admin_panel.urls')),
    path('security/', include('security.urls')),
    path('complaints/', include('complaints.urls')),
    path('outings/', include('outings.urls')),
    path('attendance/', include('attendance.urls')),
    path('fees/', include('fees.urls', namespace='fees')),
    path('rooms/', include('rooms.urls', namespace='rooms')),
    path('', include('core.urls')),  # We'll create this later
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
