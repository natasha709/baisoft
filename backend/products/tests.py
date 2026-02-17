from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from businesses.models import Business, User
from products.models import Product


class ProductAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create business
        self.business = Business.objects.create(name="Test Business")
        
        # Create users with different roles
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            business=self.business,
            role="admin"
        )
        
        self.editor = User.objects.create_user(
            email="editor@test.com",
            password="testpass123",
            business=self.business,
            role="editor"
        )
        
        self.approver = User.objects.create_user(
            email="approver@test.com",
            password="testpass123",
            business=self.business,
            role="approver"
        )
        
        self.viewer = User.objects.create_user(
            email="viewer@test.com",
            password="testpass123",
            business=self.business,
            role="viewer"
        )

    def test_admin_can_create_product(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/products/', {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': '99.99'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)

    def test_editor_can_create_product(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.post('/api/products/', {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': '99.99'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_viewer_cannot_create_product(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.post('/api/products/', {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': '99.99'
        })
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_approver_can_approve_product(self):
        product = Product.objects.create(
            name='Test Product',
            description='Test',
            price='99.99',
            business=self.business,
            created_by=self.admin,
            status='pending_approval'
        )
        
        self.client.force_authenticate(user=self.approver)
        response = self.client.post(f'/api/products/{product.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        product.refresh_from_db()
        self.assertEqual(product.status, 'approved')

    def test_editor_cannot_approve_product(self):
        product = Product.objects.create(
            name='Test Product',
            description='Test',
            price='99.99',
            business=self.business,
            created_by=self.admin,
            status='pending_approval'
        )
        
        self.client.force_authenticate(user=self.editor)
        response = self.client.post(f'/api/products/{product.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_public_listing_shows_only_approved(self):
        Product.objects.create(
            name='Draft Product',
            description='Test',
            price='99.99',
            business=self.business,
            created_by=self.admin,
            status='draft'
        )
        
        Product.objects.create(
            name='Approved Product',
            description='Test',
            price='99.99',
            business=self.business,
            created_by=self.admin,
            status='approved'
        )
        
        response = self.client.get('/api/products/?public=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        products = data if isinstance(data, list) else data.get('results', [])
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['status'], 'approved')
