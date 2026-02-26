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
    can_create_users = models.BooleanField(default=True)  # Business permission to create users
    can_assign_roles = models.BooleanField(default=True)  # Business permission to assign roles
    owner = models.ForeignKey('User', on_delete=models.CASCADE, related_name='owned_businesses', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Businesses"
        indexes = [
            models.Index(fields=['owner']),  # Index for faster owner queries
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
        email = self.normalize_email(email)  # Normalize email format
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with admin privileges"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')  # Superusers are admins by default
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
    
    # Define the four role types with their capabilities
    ROLE_CHOICES = [
        ('admin', 'Admin'),        # Full access - manage users, products, approvals
        ('editor', 'Editor'),      # Create and edit products, cannot approve
        ('approver', 'Approver'),  # Approve products only, cannot create/edit
        ('viewer', 'Viewer'),      # Read-only access to products
    ]

    # Authentication fields
    username = None  # Remove default username field
    email = models.EmailField(unique=True)  # Use email as primary identifier
    
    # Business relationship - ensures data isolation
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    
    # Role-based access control
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    
    # Invitation system fields - for secure user onboarding
    password_change_required = models.BooleanField(default=False)  # True for newly invited users
    temporary_password_expires = models.DateTimeField(null=True, blank=True)  # 7 days from invitation
    invitation_sent_at = models.DateTimeField(null=True, blank=True)  # Track invitation timestamp

    objects = UserManager()  # Use custom manager

    USERNAME_FIELD = 'email'  # Use email for authentication instead of username
    REQUIRED_FIELDS = []  # No additional required fields for superuser creation

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
