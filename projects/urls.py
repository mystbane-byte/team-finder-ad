from django.urls import path
from . import views

app_name = "projects"
urlpatterns = [
    path("list/", views.project_list_view, name="project-list"),
    path("<int:project_id>/", views.project_detail_view, name="project-detail"),
    path(
        "<int:project_id>/toggle-favorite/",
        views.toggle_favorite,
        name="toggle-favorite",
    ),
    path(
        "<int:project_id>/toggle-participate/",
        views.toggle_participate,
        name="toggle-participate",
    ),
    path("<int:project_id>/complete/", views.complete_project, name="complete-project"),
    path("create-project/", views.create_project_view, name="create-project"),
    path("<int:project_id>/edit/", views.edit_project_view, name="edit-project"),
    path("favorites/", views.favorite_projects_view, name="favorites"),
]
