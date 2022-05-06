from uuid import uuid4 as uuid
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):

    def create_user(self, username, password, date_of_birth, clubChoice, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.dob = date_of_birth
        if extra_fields.get("first_name") is not None:
            user.first_name = extra_fields.get("first_name")
        if extra_fields.get("last_name") is not None:
            user.last_name = extra_fields.get("last_name")
        user.clubChoice = clubChoice
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be staff=true')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be superuser=true')
        return self.create_user(username, password, None, '', **extra_fields)
