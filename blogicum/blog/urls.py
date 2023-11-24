from django.urls import path

from . import views

app_name = 'blog'


urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(),
         name='post_detail'),
    path('posts/<int:post_id>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:post_id>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
    path('category/<slug:category_slug>/',
         views.CategoryPostListView.as_view(),
         name='category_posts'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('profile/edit_profile/', views.ProfileUpdateView.as_view(),
         name='edit_profile'),
    path('profile/<slug:username>/', views.ProfileView.as_view(),
         name='profile'),
    path('posts/<int:pk>/comment/', views.CommentCreateView.as_view(),
         name='add_comment'),
    path('posts/<int:post_id>/comments/<int:comment_id>/edit_comment/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),
    path('posts/<int:post_id>/comments/<int:comment_id>/delete_comment/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),
]
