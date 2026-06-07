from core.utils import paginate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from projects.constants import PROJECT_STATUS_CLOSED, PROJECT_STATUS_OPEN, PROJECTS_PER_PAGE
from projects.forms import ProjectForm
from projects.models import Project


def project_list_view(request):
    projects = (
        Project.objects.filter(status=PROJECT_STATUS_OPEN)
        .select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    if request.user.is_authenticated:
        fav_ids = request.user.favorites.values_list("id", flat=True)
        for p in projects:
            p.is_favorited = p.id in fav_ids
    else:
        for p in projects:
            p.is_favorited = False

    page_obj = paginate(projects, request, per_page=PROJECTS_PER_PAGE)
    return render(request, "projects/project_list.html", {"projects": page_obj})


def project_detail_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    is_owner = request.user.is_authenticated and request.user == project.owner

    is_participant = (
        request.user.is_authenticated
        and project.participants.filter(id=request.user.id).exists()
    )
    is_favorited = (
        request.user.is_authenticated
        and project.interested_users.filter(id=request.user.id).exists()
    )
    return render(
        request,
        "projects/project-details.html",
        {
            "project": project,
            "is_owner": is_owner,
            "is_participant": is_participant,
            "is_favorited": is_favorited,
            "user": request.user,
        },
    )


@login_required
def toggle_favorite(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if is_favorited := request.user.favorites.filter(id=project.id).exists():
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)
    return JsonResponse({"status": "ok", "favorited": not is_favorited})


@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if is_participant := project.participants.filter(id=request.user.id).exists():
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)
    return JsonResponse({"status": "ok", "participant": not is_participant})


@login_required
def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user == project.owner and project.status == PROJECT_STATUS_OPEN:
        project.status = PROJECT_STATUS_CLOSED
        project.save()
        return JsonResponse({"status": "ok", "project_status": PROJECT_STATUS_CLOSED})
    return JsonResponse({"status": "error"}, status=403)


@login_required
def create_project_view(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:project-detail", project_id=project.id)
    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": False}
    )


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user != project.owner:
        return redirect("projects:project-detail", project_id=project.id)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:project-detail", project_id=project.id)
    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": True}
    )


@login_required
def favorite_projects_view(request):
    projects = (
        request.user.favorites.all()
        .select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    for p in projects:
        p.is_favorited = True
    page_obj = paginate(projects, request, per_page=PROJECTS_PER_PAGE)
    return render(request, "projects/favorite_projects.html", {"projects": page_obj})
