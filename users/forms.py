import re
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from .models import CustomUser


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = CustomUser
        fields = ("name", "surname", "email")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            return phone
        pattern = re.compile(r"^(\+7|8)(\d{10})$")
        match = pattern.match(phone)
        if not match:
            raise ValidationError(
                "Номер должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX"
            )
        phone = "+7" + match.group(2)
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(phone=phone).exists():
            raise ValidationError(
                "Пользователь с таким номером телефона уже существует"
            )
        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url and "github.com" not in url:
            raise ValidationError("Ссылка должна вести на GitHub")
        return url
