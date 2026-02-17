from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class Business(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Businesses"

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('approver', 'Approver'),
        ('viewer', 'Viewer'),
    ]

    username = None
    email = models.EmailField(unique=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    password_change_required = models.BooleanField(default=False)
    temporary_password_expires = models.DateTimeField(null=True, blank=True)
    invitation_sent_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_permission(self, permission):
        """Check if user has specific permission based on role"""
        permissions_map = {
            'admin': ['create_product', 'edit_product', 'approve_product', 'delete_product', 'view_all'],
            'editor': ['create_product', 'edit_product', 'view_all'],
            'approver': ['approve_product', 'view_all'],
            'viewer': ['view_all'],
        }
        return permission in permissions_map.get(self.role, [])
