from django.urls import path
from . import views

# Keep account authentication routes together under the /accounts/ namespace.
urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
