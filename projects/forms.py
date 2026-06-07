from django import forms

from projects.constants import PROJECT_STATUS_CHOICES
from projects.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        widgets = {
            "status": forms.Select(choices=PROJECT_STATUS_CHOICES),
            "description": forms.Textarea(attrs={"rows": 5}),
        }
