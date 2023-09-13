from django.urls import path
from .views import PostListView, PostDetailView, post_share, create_comment, search_view

app_name = 'blog'

urlpatterns = [
    path('', PostListView.as_view(), name='index'),
    path('search/', search_view, name='search'),
    path('<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('tag/<slug:tag_slug>/', PostListView.as_view(), name='list_with_tag'),
    path('<slug:post_slug>/share/', post_share, name='post_share'),
    path('<slug:post_slug>/add-comment/', create_comment, name='add_comment'),

]
