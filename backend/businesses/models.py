from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class Business(models.Model):
    """
    Business model - represents a company/organization in the marketplace

    Features:
    - Each business can have multiple users and products
    - Business isolation ensures data privacy between companies
    - Tracks business capabilities and ownership
    """
    name = models.CharField(max_length=255)
    can_create_users = models.BooleanField(default=True)
    can_assign_roles = models.BooleanField(default=True)
    owner = models.ForeignKey('User', on_delete=models.CASCADE, related_name='owned_businesses', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Businesses"
        indexes = [
            models.Index(fields=['owner']),
        ]

    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication

    Purpose:
    - Handles user creation with email as the primary identifier
    - Removes dependency on username field
    - Supports superuser creation with admin role
    """
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with email and password"""
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with admin privileges"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """
    Custom User model with role-based permissions and invitation system

    Key Features:
    - Email-based authentication (no username required)
    - Four role types with different permission levels
    - Invitation system with temporary passwords
    - Business isolation (users belong to one business)
    - Password change requirement for new users
    """

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
        """
        Check if user has specific permission based on their role

        Permission Matrix:
        - Admin: All permissions (create, edit, approve, delete, view)
        - Editor: Create and edit products, view all
        - Approver: Approve products, view all
        - Viewer: View all products only

        Args:
            permission (str): Permission to check (e.g., 'create_product')

        Returns:
            bool: True if user has permission, False otherwise
        """
        permissions_map = {
            'admin': ['create_product', 'edit_product', 'approve_product', 'delete_product', 'view_all'],
            'editor': ['create_product', 'edit_product', 'view_all'],
            'approver': ['approve_product', 'view_all'],
            'viewer': ['view_all'],
        }
        return permission in permissions_map.get(self.role, [])
