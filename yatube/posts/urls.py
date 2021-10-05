from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'), # доступно всем
    path('group/<slug:slug>/', views.group_posts, name='group_posts'), # доступно всем
    path('profile/<str:username>/', views.profile, name='profile'), # доступно всем
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'), # доступно всем
    path('create/', views.post_create, name='post_create'), # только авторизованным
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'), # только авторизованным

]
