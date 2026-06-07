from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "status", "created_at")
    list_filter = ("status", "created_at", "owner")
    search_fields = (
        "name",
        "description",
        "owner__email",
        "owner__name",
        "owner__surname",
    )
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("name", "description", "github_url", "status")}),
        ("Участники", {"fields": ("participants",)}),
        ("Владелец", {"fields": ("owner",)}),
        ("Дата", {"fields": ("created_at",)}),
    )
    filter_horizontal = ("participants",)
