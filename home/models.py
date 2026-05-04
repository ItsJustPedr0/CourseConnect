from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserManager(BaseUserManager):
  use_in_migrations = True

  def _create_user(self, student_id, email, password, **extra_fields):
    if not student_id:
      raise ValueError('The given student_id must be set')
    email = self.normalize_email(email)
    user = self.model(student_id=student_id, email=email, **extra_fields)
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_user(self, student_id, email=None, password=None, **extra_fields):
    extra_fields.setdefault('is_staff', False)
    extra_fields.setdefault('is_superuser', False)
    return self._create_user(student_id, email, password, **extra_fields)

  def create_superuser(self, student_id, email=None, password=None, **extra_fields):
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)

    if extra_fields.get('is_staff') is not True:
      raise ValueError('Superuser must have is_staff=True.')
    if extra_fields.get('is_superuser') is not True:
      raise ValueError('Superuser must have is_superuser=True.')

    return self._create_user(student_id, email, password, **extra_fields)


class CustomUser(AbstractUser):
  username = None
  student_id = models.CharField(max_length=6, unique=True)
  
  USERNAME_FIELD = 'student_id'
  REQUIRED_FIELDS = []  
  
  objects = CustomUserManager()
  
  class Meta:
    verbose_name = 'User'
    verbose_name_plural = 'Users'

  def __str__(self):
    return f"{self.student_id}"