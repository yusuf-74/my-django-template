from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView

urlpatterns = [
    path('api/docs/', SpectacularAPIView.as_view(), name='swagger_docs'),
    path('api/admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
]

if settings.DEBUG and settings.DEV_ENV != 'production':
    import debug_toolbar

    urlpatterns += [
        path('api/__debug__/', include(debug_toolbar.urls)),
    ]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
