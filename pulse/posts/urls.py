from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("create/", views.create_post, name="create_post"),
    path("post/<int:pk>/", views.post_detail, name="post_detail"),

    path("post/<int:pk>/upvote/", views.toggle_post_vote, {"value": 1}, name="post_upvote"),
    path("post/<int:pk>/downvote/", views.toggle_post_vote, {"value": -1}, name="post_downvote"),

    path("comment/<int:pk>/upvote/", views.toggle_comment_vote, {"value": 1}, name="comment_upvote"),
    path("comment/<int:pk>/downvote/", views.toggle_comment_vote, {"value": -1}, name="comment_downvote"),

    path("post/<int:pk>/edit/", views.edit_post, name="edit_post"),
    path("post/<int:pk>/delete/", views.delete_post, name="delete_post"),

    path("comment/<int:pk>/edit/", views.edit_comment, name="edit_comment"),
    path("comment/<int:pk>/delete/", views.delete_comment, name="delete_comment"),

    path("department/<int:department_id>/", views.department_posts, name="department_posts"),
    path("communities/search/", views.search_communities, name="search_communities"),

    path("profile/<str:username>/", views.user_profile, name="user_profile"),
]

