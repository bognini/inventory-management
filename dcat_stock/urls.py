from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from apps.inventory.views import logout_view

urlpatterns = [
	path('admin/', admin.site.urls),
	path('connexion/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
	path('deconnexion/', logout_view, name='logout'),
	path('', include('apps.inventory.urls')),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
