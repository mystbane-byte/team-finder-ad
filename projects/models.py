from django.conf import settings
from django.db import models
from django.urls import reverse

from projects.constants import PROJECT_NAME_MAX_LENGTH, PROJECT_STATUS_CHOICES, PROJECT_STATUS_OPEN


class Project(models.Model):
    name = models.CharField(max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True)
    status = models.CharField(
        max_length=max(len(v) for v, _ in PROJECT_STATUS_CHOICES),
        choices=PROJECT_STATUS_CHOICES,
        default=PROJECT_STATUS_OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("projects:project-detail", kwargs={"project_id": self.pk})
