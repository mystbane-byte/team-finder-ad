from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import CustomUser


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("projects:project-list")
    else:
        form = UserRegistrationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                return redirect("projects:project-list")
            else:
                form.add_error(None, "Неверный имейл или пароль")
    else:
        form = UserLoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:project-list")


@login_required
def user_detail_view(request, user_id):
    user_obj = get_object_or_404(CustomUser, id=user_id)
    projects = user_obj.owned_projects.all().order_by("-created_at")
    return render(
        request,
        "users/user-details.html",
        {
            "user": user_obj,
            "user_obj": user_obj,
            "projects": projects,
            "is_owner": request.user == user_obj,
        },
    )


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:user-detail", user_id=request.user.id)
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})

# change password еуые
@login_required
def change_password_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect("users:user-detail", user_id=request.user.id)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


def users_list_view(request):
    users = CustomUser.objects.all().order_by("-id")
    active_filter = None

    if request.user.is_authenticated:
        filter_param = request.GET.get("filter")
        if filter_param:
            active_filter = filter_param
            if filter_param == "owners-of-favorite-projects":
                favorited = request.user.favorites.all()
                users = CustomUser.objects.filter(
                    owned_projects__in=favorited
                ).distinct()
            elif filter_param == "owners-of-participating-projects":
                participated = request.user.participated_projects.all()
                users = CustomUser.objects.filter(
                    owned_projects__in=participated
                ).distinct()
            elif filter_param == "interested-in-my-projects":
                my_projects = request.user.owned_projects.all()
                users = CustomUser.objects.filter(favorites__in=my_projects).distinct()
            elif filter_param == "participants-of-my-projects":
                my_projects = request.user.owned_projects.all()
                users = CustomUser.objects.filter(
                    participated_projects__in=my_projects
                ).distinct()
            users = users.order_by("-id")

    paginator = Paginator(users, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj,
            "active_filter": active_filter,
        },
    )
