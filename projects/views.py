from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Project
from .forms import ProjectForm


def project_list_view(request):
    projects = Project.objects.filter(status="open").order_by("-created_at")
    if request.user.is_authenticated:
        fav_ids = request.user.favorites.values_list("id", flat=True)
        for p in projects:
            p.is_favorited = p.id in fav_ids
    else:
        for p in projects:
            p.is_favorited = False
    paginator = Paginator(projects, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "projects/project_list.html", {"projects": page_obj})


def project_detail_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    is_owner = request.user.is_authenticated and request.user == project.owner
    is_participant = (
        request.user.is_authenticated and request.user in project.participants.all()
    )
    is_favorited = (
        request.user.is_authenticated and request.user in project.interested_users.all()
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
    if request.user.favorites.filter(id=project.id).exists():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user in project.participants.all():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": "ok", "participant": participant})


@login_required
def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user == project.owner and project.status == "open":
        project.status = "closed"
        project.save()
        return JsonResponse({"status": "ok", "project_status": "closed"})
    return JsonResponse({"status": "error"}, status=403)


@login_required
def create_project_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:project-detail", project_id=project.id)
    else:
        form = ProjectForm()
    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": False}
    )


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user != project.owner:
        return redirect("projects:project-detail", project_id=project.id)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:project-detail", project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": True}
    )


@login_required
def favorite_projects_view(request):
    projects = request.user.favorites.all().order_by("-created_at")
    for p in projects:
        p.is_favorited = True
    paginator = Paginator(projects, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "projects/favorite_projects.html", {"projects": page_obj})
