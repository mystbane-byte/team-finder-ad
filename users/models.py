from django.db import models
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    name = models.CharField("Имя", max_length=124)
    surname = models.CharField("Фамилия", max_length=124)
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True)
    phone = models.CharField(
        "Телефон", max_length=15, unique=True, blank=True, null=True
    )
    github_url = models.URLField("GitHub", blank=True)
    about = models.TextField("О себе", max_length=256, blank=True)
    favorites = models.ManyToManyField(
        "projects.Project", related_name="interested_users", blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname", "phone"]

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self.avatar = self.generate_avatar()
        super().save(*args, **kwargs)

    def generate_avatar(self):
        size = 200
        color = (
            random.randint(50, 200),
            random.randint(50, 200),
            random.randint(50, 200),
        )
        img = Image.new("RGB", (size, size), color)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 120)
        except:
            font = ImageFont.load_default()
        text = self.name[0].upper()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size - text_width) // 2, (size - text_height) // 2 - 10)
        draw.text(position, text, fill="white", font=font)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return ContentFile(buffer.getvalue(), f"avatar_{self.email}.png")
