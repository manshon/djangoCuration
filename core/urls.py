from django.urls import path
from . import views

app_name='core'
urlpatterns = [
    path('home', views.home, name='home'),
    path('home/<int:community_id>/', views.real_home, name='real_home'),
    path('home/<int:community_id>/article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('home/<int:community_id>/article/<int:article_id>/edit', views.article_edit, name='article_edit'),
    path('article/<int:article_id>/delete', views.article_delete, name='article_delete'),
    path('home/<int:community_id>/create/', views.article_create, name='article_create'),

    path('home/article/<int:article_id>/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),

    path('my_article/', views.my_article, name='my_article'),

    path('community_manage/', views.community_manage, name='community_manage'),
    path('community_create/', views.community_create, name='community_create'),
    path('home/<int:community_id>/detail/', views.community_detail, name='community_detail'),
    path('home/<int:community_id>/edit/', views.community_edit, name='community_edit'),
    path('home/<int:community_id>/delete/', views.community_delete, name='community_delete'),

    path('community_search/', views.community_search, name='community_search'),
    path('home/<int:community_id>/follow', views.community_follow, name='community_follow'),
    path('home/<int:community_id>/user_manage/', views.community_user_manage, name='community_user_manage'),
    path('home/<int:community_id>/permitted_user_manage/', views.community_permitted_user_manage,
         name='community_permitted_user_manage'),
]