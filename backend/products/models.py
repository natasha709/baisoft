from django.db import models
from businesses.models import User, Business


class Product(models.Model):
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
    business_name_snapshot = models.CharField(max_length=255, blank=True)  # Snapshot of business name at creation
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_products')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Set snapshot on initial creation if not already set
        if not self.business_name_snapshot and self.business:
            self.business_name_snapshot = self.business.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.status}"
