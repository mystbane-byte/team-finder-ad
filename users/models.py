import random
from io import BytesIO

from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from users.constants import (
    ABOUT_MAX_LENGTH,
    AVATAR_BG_MAX,
    AVATAR_BG_MIN,
    AVATAR_FONT_FACTOR,
    AVATAR_SIZE,
    AVATAR_TEXT_COLOR,
    NAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    SURNAME_MAX_LENGTH,
)
from users.managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    name = models.CharField("Имя", max_length=NAME_MAX_LENGTH)
    surname = models.CharField("Фамилия", max_length=SURNAME_MAX_LENGTH)
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True)
    phone = models.CharField(
        "Телефон", max_length=PHONE_MAX_LENGTH, unique=True, blank=True, null=True
    )
    github_url = models.URLField("GitHub", blank=True)
    about = models.TextField("О себе", max_length=ABOUT_MAX_LENGTH, blank=True)
    favorites = models.ManyToManyField(
        "projects.Project", related_name="interested_users", blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname", "phone"]

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self.avatar = self.generate_avatar()
        super().save(*args, **kwargs)

    def generate_avatar(self):
        size = AVATAR_SIZE

        bg_color = tuple(random.randint(AVATAR_BG_MIN, AVATAR_BG_MAX) for _ in range(3))
        img = Image.new("RGB", (size, size), bg_color)
        draw = ImageDraw.Draw(img)

        font_size = int(size * AVATAR_FONT_FACTOR)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except (IOError, OSError):
            font = ImageFont.load_default()

        text = self.name[0].upper()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size - text_width) // 2, (size - text_height) // 2)
        draw.text(position, text, fill=AVATAR_TEXT_COLOR, font=font)

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return ContentFile(buffer.getvalue(), f"avatar_{self.email}.png")
