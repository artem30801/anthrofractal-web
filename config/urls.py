"""anthrofractal URL Configuration"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.views.defaults import page_not_found

from django.conf import settings
from comic import views

urlpatterns = [
    path('admin/logout/', RedirectView.as_view(url=f"https://auth.{settings.DOMAIN_NAME}/logout?rd=https://{settings.DOMAIN_NAME}")),
    path('admin/', admin.site.urls),
    path('comic/', include('comic.urls')),
    path('archive/', RedirectView.as_view(url='/comic/archive/')),
    path('about/', RedirectView.as_view(url='/comic/about/')),
    path('', views.index, name='comic-index'),
]

if settings.DEBUG:
    urlpatterns += path('404/', page_not_found, {'exception': Exception("Error text here")}),
    urlpatterns += path('__debug__/', include('debug_toolbar.urls')),

    # For development only!
    # from django.conf.urls.static import static
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
