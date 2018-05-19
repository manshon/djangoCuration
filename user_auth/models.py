from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    class Meta(AbstractUser.Meta):
        db_table = 'user'
        swappable = 'AUTH_USER_MODEL'

    def get_full_name(self):
        return self.last_name + ' ' + self.first_name

