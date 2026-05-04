from django.db import models
from django.contrib.auth.models import User


GENDER_CHOICES = (
    ("male", "Male"),
    ("female", "Female"),
    ("other", "Other"),
)

LOOKING_FOR_CHOICES = (
    ("male", "Male"),
    ("female", "Female"),
    ("everyone", "Everyone"),
)


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    display_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    bio = models.TextField(max_length=500)
    location = models.CharField(max_length=100)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    looking_for = models.CharField(max_length=20, choices=LOOKING_FOR_CHOICES)
    profile_image = models.ImageField(
        upload_to="profile_images/",
        default="profile_images/default.jpg"
    )
    created_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name