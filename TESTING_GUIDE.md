# Testing Guide

## Manual Testing Checklist

### 1. User Registration & Authentication

**Test Registration:**
- [ ] Navigate to `/register`
- [ ] Fill in all fields (email, password, names, business name)
- [ ] Submit form
- [ ] Verify redirect to dashboard
- [ ] Verify user is logged in
- [ ] Check user role is "admin"

**Test Login:**
- [ ] Navigate to `/login`
- [ ] Enter valid credentials
- [ ] Submit form
- [ ] Verify redirect to dashboard
- [ ] Verify user data is displayed

**Test Invalid Login:**
- [ ] Try logging in with wrong password
- [ ] Verify error message is shown
- [ ] Try logging in with non-existent email
- [ ] Verify error message is shown

**Test Logout:**
- [ ] Click logout button
- [ ] Verify redirect to home page
- [ ] Verify cannot access dashboard without login

### 2. Product Management

**Test Create Product (Admin/Editor):**
- [ ] Login as admin or editor
- [ ] Click "Create Product" button
- [ ] Fill in product details
- [ ] Submit form
- [ ] Verify product appears in list
- [ ] Verify status is "draft"

**Test Create Product (Viewer):**
- [ ] Login as viewer
- [ ] Verify "Create Product" button is hidden
- [ ] Try direct API call (should fail)

**Test Submit for Approval:**
- [ ] Create a draft product
- [ ] Click "Submit for Approval"
- [ ] Verify status changes to "pending_approval"

**Test Approve Product (Approver/Admin):**
- [ ] Login as approver or admin
- [ ] Find pending product
- [ ] Click "Approve" button
- [ ] Verify status changes to "approved"
- [ ] Verify approved_by and approved_at are set

**Test Approve Product (Editor):**
- [ ] Login as editor
- [ ] Find pending product
- [ ] Verify "Approve" button is hidden
- [ ] Try direct API call (should fail)

**Test Delete Product (Admin):**
- [ ] Login as admin
- [ ] Click delete on a product
- [ ] Confirm deletion
- [ ] Verify product is removed

**Test Delete Product (Non-Admin):**
- [ ] Login as editor/approver/viewer
- [ ] Verify delete button is hidden
- [ ] Try direct API call (should fail)

### 3. Public Product Listing

**Test Public Access:**
- [ ] Logout (or use incognito)
- [ ] Navigate to home page
- [ ] Verify only approved products are shown
- [ ] Verify draft products are not shown
- [ ] Verify pending products are not shown

**Test Product Display:**
- [ ] Verify product name is displayed
- [ ] Verify description is displayed
- [ ] Verify price is displayed
- [ ] Verify business name is displayed

### 4. AI Chatbot

**Test Chatbot Access:**
- [ ] Login as any user
- [ ] Navigate to `/chatbot`
- [ ] Verify chat interface loads

**Test Product Queries:**
- [ ] Ask "What products are available?"
- [ ] Verify AI responds with product list
- [ ] Ask "Which products are under $50?"
- [ ] Verify AI filters by price
- [ ] Ask about specific product
- [ ] Verify AI provides details

**Test Chat History:**
- [ ] Send multiple messages
- [ ] Refresh page
- [ ] Verify chat history is preserved

**Test Unauthenticated Access:**
- [ ] Logout
- [ ] Try to access `/chatbot`
- [ ] Verify redirect to login

### 5. Role-Based Permissions

**Admin Role:**
- [ ] Can create products
- [ ] Can edit products
- [ ] Can approve products
- [ ] Can delete products
- [ ] Can view all products

**Editor Role:**
- [ ] Can create products
- [ ] Can edit products
- [ ] Cannot approve products
- [ ] Cannot delete products
- [ ] Can view all products

**Approver Role:**
- [ ] Cannot create products
- [ ] Cannot edit products
- [ ] Can approve products
- [ ] Cannot delete products
- [ ] Can view all products

**Viewer Role:**
- [ ] Cannot create products
- [ ] Cannot edit products
- [ ] Cannot approve products
- [ ] Cannot delete products
- [ ] Can view all products

### 6. UI/UX Testing

**Responsive Design:**
- [ ] Test on desktop (1920x1080)
- [ ] Test on tablet (768x1024)
- [ ] Test on mobile (375x667)
- [ ] Verify all elements are accessible
- [ ] Verify no horizontal scrolling

**Form Validation:**
- [ ] Try submitting empty forms
- [ ] Verify validation messages
- [ ] Try invalid email format
- [ ] Try short password (<8 chars)
- [ ] Try negative price

**Loading States:**
- [ ] Verify loading spinners appear
- [ ] Verify buttons disable during submission
- [ ] Verify no double submissions

**Error Handling:**
- [ ] Test with backend offline
- [ ] Verify error messages are user-friendly
- [ ] Test network timeout
- [ ] Test invalid API responses

## Automated Testing

### Backend Tests

**Run All Tests:**
```bash
cd backend
python manage.py test
```

**Run Specific Test:**
```bash
python manage.py test products.tests.ProductAPITestCase.test_admin_can_create_product
```

**Run with Coverage:**
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Cases Included

**Authentication Tests:**
- User registration
- User login
- Token refresh
- Permission checks

**Product Tests:**
- Create product (various roles)
- Update product
- Delete product
- Approve product
- Public listing filtering

**Permission Tests:**
- Role-based access control
- Object-level permissions
- Business isolation

## API Testing with Postman/cURL

### Setup
1. Import API_DOCUMENTATION.md endpoints
2. Set base URL: `http://localhost:8000/api`
3. Create environment variables for tokens

### Test Authentication

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User",
    "business_name": "Test Business"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### Test Products

**Create Product:**
```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Test Product",
    "description": "Test Description",
    "price": "99.99"
  }'
```

**List Products:**
```bash
curl http://localhost:8000/api/products/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Approve Product:**
```bash
curl -X POST http://localhost:8000/api/products/1/approve/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Performance Testing

### Load Testing with Apache Bench

**Test Product Listing:**
```bash
ab -n 1000 -c 10 http://localhost:8000/api/products/?public=true
```

**Test with Authentication:**
```bash
ab -n 1000 -c 10 -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/products/
```

### Expected Performance
- Response time: < 200ms
- Throughput: > 100 req/s
- Error rate: < 1%

## Security Testing

### Test Authentication
- [ ] Try accessing protected endpoints without token
- [ ] Try using expired token
- [ ] Try using invalid token
- [ ] Try token from different user

### Test Authorization
- [ ] Try accessing other business's products
- [ ] Try performing actions without permission
- [ ] Try SQL injection in inputs
- [ ] Try XSS in product descriptions

### Test Input Validation
- [ ] Try extremely long strings
- [ ] Try special characters
- [ ] Try negative numbers
- [ ] Try null/undefined values

## Browser Compatibility

Test on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

## Accessibility Testing

- [ ] Test with screen reader
- [ ] Test keyboard navigation
- [ ] Check color contrast
- [ ] Verify ARIA labels
- [ ] Test with browser zoom

## Common Issues & Solutions

### Issue: Tests fail with database errors
**Solution:** Run migrations: `python manage.py migrate`

### Issue: Frontend can't connect to backend
**Solution:** Check CORS settings and backend is running on port 8000

### Issue: AI chatbot returns errors
**Solution:** Verify OPENAI_API_KEY is set and valid

### Issue: Token expired errors
**Solution:** Use refresh token endpoint or login again

## Test Data Setup

### Create Test Users
```python
# In Django shell: python manage.py shell
from businesses.models import Business, User

business = Business.objects.create(name="Test Business")

admin = User.objects.create_user(
    email="admin@test.com",
    password="test123",
    business=business,
    role="admin"
)

editor = User.objects.create_user(
    email="editor@test.com",
    password="test123",
    business=business,
    role="editor"
)

approver = User.objects.create_user(
    email="approver@test.com",
    password="test123",
    business=business,
    role="approver"
)

viewer = User.objects.create_user(
    email="viewer@test.com",
    password="test123",
    business=business,
    role="viewer"
)
```

### Create Test Products
```python
from products.models import Product

Product.objects.create(
    name="Test Product 1",
    description="Description 1",
    price="99.99",
    status="approved",
    business=business,
    created_by=admin
)

Product.objects.create(
    name="Test Product 2",
    description="Description 2",
    price="49.99",
    status="draft",
    business=business,
    created_by=editor
)
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          python manage.py test
```

## Reporting Bugs

When reporting bugs, include:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Screenshots/logs
5. Environment (OS, browser, versions)
6. User role and permissions
