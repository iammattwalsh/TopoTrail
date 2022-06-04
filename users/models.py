from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    test = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return self.username