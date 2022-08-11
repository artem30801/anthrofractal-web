from django.urls import path


from . import views

urlpatterns = [
    path('', views.index, name='comic-index'),
    path('archive/', views.archive, name='comic-archive'),
    path('about/', views.howto, name='comic-howto'),
    path('<int:number>/', views.panel, name='comic-panel'),
    # path('latest/', views.latest, name='comic-latest'),

    path('feed/', views.ComicPanelsFeed(), name='comic-feed'),
    path('image_feed/', views.ComicImagesFeed(), name='comic-image-feed'),

    path('secret/<str:signature>/', views.secret_signed, name='comic-secret'),
    path('secret/admin-preview/<uuid:u_id>/', views.secret_preview, name='comic-secret-preview'),

    path('search/', views.search, name='comic-search-request'),
    path('search/live/', views.live_search, name='comic-search-live'),
    path('search/tag/<str:slug>/', views.tag, name='comic-search-tag'),
]
