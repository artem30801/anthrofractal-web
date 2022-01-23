from django.urls import path


from . import views

urlpatterns = [
    path('', views.index, name='comic-index'),
    path('archive/', views.archive, name='comic-archive'),
    path('about/', views.howto, name='comic-howto'),
    path('<int:number>/', views.panel, name='comic-panel'),
    path('secret/<str:signature>/', views.secret_signed, name='comic-secret'),
    path('secret/admin-preview/<uuid:u_id>/', views.secret_preview, name='comic-secret-preview'),
    path('search/', views.search, name='comic-search-request'),
    path('search/live/', views.live_search, name='comic-search-live'),
    path('search/tag/<str:slug>/', views.tag, name='comic-search-tag'),
]
