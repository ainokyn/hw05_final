from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('posts.urls', namespace='post')),
    path('group/slug:slug>/', include('posts.urls', namespace='group')),
    path('auth/', include('users.urls', namespace='users')),
    path('about/', include('about.urls', namespace='about')),
    path('auth/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
]
handler404 = 'core.views.page_not_found'
handler500 = 'core.views.internal_server_error'
handler403 = 'core.views.csrf_failure'
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
