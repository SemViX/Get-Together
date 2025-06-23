from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from botapp.views import telegram_webhook
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include("users.urls")),
    path("api/", include("events.urls")),

    path("webhook/", telegram_webhook),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
