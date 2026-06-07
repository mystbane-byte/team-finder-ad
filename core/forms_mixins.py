from django.core.exceptions import ValidationError


class GithubURLMixin:
    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url and "github.com" not in url:
            raise ValidationError("Ссылка должна вести на GitHub")
        return url
