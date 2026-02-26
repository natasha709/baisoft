# Product Management Models
# This module defines the Product model for the marketplace system.
# Products go through an approval workflow with role-based permissions.
#
# Key Features:
# - Product approval workflow (Draft → Pending → Approved)
# - Role-based product management (Editor creates, Approver approves)
# - Business isolation (products belong to specific businesses)
# - Audit trail with creation and approval tracking
# - Business name snapshots for historical data integrity

from django.db import models
from businesses.models import User, Business


class Product(models.Model):
    """
    Product Model for Marketplace System
    
    Represents products that businesses want to sell through the marketplace.
    Implements a three-stage approval workflow with role-based permissions.
    
    Workflow:
    1. Draft: Editor creates product (not visible to customers)
    2. Pending Approval: Editor submits for review
    3. Approved: Approver approves product (visible to customers)
    
    Business Rules:
    - Only Editors can create and edit products
    - Only Approvers can approve products
    - Products are isolated by business (multi-tenancy)
    - Audit trail tracks who created and approved each product
    """
    
    # Product approval workflow states
    STATUS_CHOICES = [
        ('draft', 'Draft'),                    # Editor is still working on it
        ('pending_approval', 'Pending Approval'),  # Submitted for approval
        ('approved', 'Approved'),              # Ready for customers
    ]

    # Core product information
    name = models.CharField(max_length=255)  # Product name (e.g., "iPhone 15")
    description = models.TextField()  # Detailed product description
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Product price (supports up to 99,999,999.99)
    
    # Workflow and approval system
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Business relationships and isolation
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='products')
    business_name_snapshot = models.CharField(max_length=255, blank=True)  # Historical business name
    
    # Audit trail - who created and approved
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_products')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_products')
    
    # Timestamps for tracking
    created_at = models.DateTimeField(auto_now_add=True)  # When product was created
    updated_at = models.DateTimeField(auto_now=True)      # When product was last modified
    approved_at = models.DateTimeField(null=True, blank=True)  # When product was approved

    class Meta:
        ordering = ['-created_at']  # Show newest products first

    def save(self, *args, **kwargs):
        """
        Custom save method to capture business name snapshot
        
        This ensures we have historical data even if business names change.
        Important for audit trails and reporting.
        """
        # Capture business name when product is first created
        if not self.business_name_snapshot and self.business:
            self.business_name_snapshot = self.business.name
        super().save(*args, **kwargs)

    def __str__(self):
        """String representation for admin interface and debugging"""
        return f"{self.name} - {self.status}"
