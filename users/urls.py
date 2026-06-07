from django.urls import path
from . import views

app_name = "users"
urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("<int:user_id>/", views.user_detail_view, name="user-detail"),
    path("edit/", views.edit_profile_view, name="edit-profile"),
    path("edit-profile/", views.edit_profile_view, name="edit-profile-alt"),
    path("change-password/", views.change_password_view, name="change-password"),
    path("list/", views.users_list_view, name="users-list"),
]
