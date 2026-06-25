from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('patients/', include('patients.urls')),
    path('doctors/', include('doctors.urls')),
    path('portal/', include('admin_portal.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
