from django.urls import path
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Blog posts
    path('', HomeView.as_view(), name='home'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('category/<slug:slug>/', views.CategoryPostsView.as_view(), name='category_posts'),
    path('post/<int:pk>/duplicate/', views.duplicate_post, name='post_duplicate'),
    path('post/<int:pk>/delete-permanent/', views.delete_post_permanent, name='post_delete_permanent'),
    path('post/<int:pk>/soft-delete/', views.soft_delete_post, name='soft_delete_post'),
    path('post/<int:pk>/restore/', views.restore_post, name='post_restore'),
    path('trash/', TrashView.as_view(), name='trash'),

    # User dashboards
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('author/<str:username>/', AuthorPostsView.as_view(), name='author_posts'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),

    # Comments & likes
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('post/<int:pk>/like/', like_post, name='like_post'),

    # Authentication
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
