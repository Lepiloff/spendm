from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    user_role = models.ForeignKey("vendors.UserRoles", models.DO_NOTHING, blank=True, null=True)
    # assigned_vendor = models.ForeignKey("vendors.Vendors", models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.username
