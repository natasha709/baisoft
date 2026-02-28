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

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='products')
    business_name_snapshot = models.CharField(max_length=255, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_products')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_products')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """
        Custom save method to capture business name snapshot

        This ensures we have historical data even if business names change.
        Important for audit trails and reporting.
        """

        if not self.business_name_snapshot and self.business:
            self.business_name_snapshot = self.business.name
        super().save(*args, **kwargs)

    def __str__(self):
        """String representation for admin interface and debugging"""
        return f"{self.name} - {self.status}"
