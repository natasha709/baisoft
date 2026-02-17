# Architecture Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Browser    │  │   Mobile     │  │   Tablet     │          │
│  │  (Desktop)   │  │   Browser    │  │   Browser    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│         └──────────────────┴──────────────────┘                  │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             │
                             │ HTTPS
                             │
┌────────────────────────────┼──────────────────────────────────────┐
│                  FRONTEND LAYER (Next.js)                         │
├────────────────────────────┼──────────────────────────────────────┤
│                            │                                       │
│  ┌─────────────────────────▼────────────────────────┐            │
│  │         Next.js Application (Port 3000)          │            │
│  ├──────────────────────────────────────────────────┤            │
│  │  • Public Product Listing                        │            │
│  │  • Authentication (Login/Register)               │            │
│  │  • Product Management Dashboard                  │            │
│  │  • AI Chatbot Interface                          │            │
│  │  • Role-based UI Rendering                       │            │
│  └──────────────────────┬───────────────────────────┘            │
│                         │                                         │
└─────────────────────────┼─────────────────────────────────────────┘
                          │
                          │ REST API (JSON)
                          │ JWT Authentication
                          │
┌─────────────────────────┼─────────────────────────────────────────┐
│                  BACKEND LAYER (Django)                           │
├─────────────────────────┼─────────────────────────────────────────┤
│                         │                                          │
│  ┌──────────────────────▼───────────────────────────┐            │
│  │      Django REST Framework (Port 8000)           │            │
│  ├──────────────────────────────────────────────────┤            │
│  │                                                   │            │
│  │  ┌─────────────────┐  ┌─────────────────┐      │            │
│  │  │   businesses/   │  │    products/    │      │            │
│  │  │                 │  │                 │      │            │
│  │  │ • User Auth     │  │ • CRUD Ops      │      │            │
│  │  │ • JWT Tokens    │  │ • Approval      │      │            │
│  │  │ • Roles         │  │ • Permissions   │      │            │
│  │  │ • Business Mgmt │  │ • Public List   │      │            │
│  │  └─────────────────┘  └─────────────────┘      │            │
│  │                                                   │            │
│  │  ┌─────────────────┐                            │            │
│  │  │    chatbot/     │                            │            │
│  │  │                 │                            │            │
│  │  │ • AI Queries    │                            │            │
│  │  │ • Chat History  │                            │            │
│  │  │ • OpenAI API    │                            │            │
│  │  └─────────────────┘                            │            │
│  │                                                   │            │
│  └───────────────────┬───────────────┬──────────────┘            │
│                      │               │                            │
└──────────────────────┼───────────────┼────────────────────────────┘
                       │               │
                       │               │
        ┌──────────────▼──┐    ┌──────▼──────────┐
        │   Database      │    │   OpenAI API    │
        │   (SQLite/      │    │   (GPT-4)       │
        │   PostgreSQL)   │    │                 │
        └─────────────────┘    └─────────────────┘
```

## Authentication Flow

```
┌─────────┐                ┌──────────┐              ┌─────────┐
│ Browser │                │ Frontend │              │ Backend │
└────┬────┘                └────┬─────┘              └────┬────┘
     │                          │                         │
     │  1. Enter credentials    │                         │
     ├─────────────────────────>│                         │
     │                          │                         │
     │                          │  2. POST /auth/login/   │
     │                          ├────────────────────────>│
     │                          │     {email, password}   │
     │                          │                         │
     │                          │  3. Validate & Create   │
     │                          │     JWT Tokens          │
     │                          │<────────────────────────┤
     │                          │  {access, refresh}      │
     │                          │                         │
     │  4. Store tokens in      │                         │
     │     localStorage         │                         │
     │<─────────────────────────┤                         │
     │                          │                         │
     │  5. Redirect to          │                         │
     │     Dashboard            │                         │
     │<─────────────────────────┤                         │
     │                          │                         │
     │  6. Subsequent requests  │                         │
     │     include JWT token    │                         │
     │                          ├────────────────────────>│
     │                          │  Authorization: Bearer  │
     │                          │                         │
```

## Product Approval Workflow

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  DRAFT   │────────>│ PENDING  │────────>│ APPROVED │
│          │         │ APPROVAL │         │          │
└──────────┘         └──────────┘         └──────────┘
     │                    │                     │
     │                    │                     │
  Created            Submitted             Approved
  by Editor          by Editor            by Approver
     │                    │                     │
     │                    │                     │
  Not visible        Not visible          Visible to
  to public          to public            public
```

## Role-Based Permissions Matrix

```
┌─────────────────┬───────┬────────┬──────────┬─────────┐
│ Action          │ Admin │ Editor │ Approver │ Viewer  │
├─────────────────┼───────┼────────┼──────────┼─────────┤
│ Create Product  │   ✓   │   ✓    │    ✗     │    ✗    │
├─────────────────┼───────┼────────┼──────────┼─────────┤
│ Edit Product    │   ✓   │   ✓    │    ✗     │    ✗    │
├─────────────────┼───────┼────────┼──────────┼─────────┤
│ Approve Product │   ✓   │   ✗    │    ✓     │    ✗    │
├─────────────────┼───────┼────────┼──────────┼─────────┤
│ Delete Product  │   ✓   │   ✗    │    ✗     │    ✗    │
├─────────────────┼───────┼────────┼──────────┼─────────┤
│ View All        │   ✓   │   ✓    │    ✓     │    ✓    │
└─────────────────┴───────┴────────┴──────────┴─────────┘
```

## Database Schema

```
┌─────────────────────────────────────────────────────────────┐
│                      businesses_business                     │
├─────────────────────────────────────────────────────────────┤
│ id (PK)                                                      │
│ name                                                         │
│ description                                                  │
│ created_at                                                   │
│ updated_at                                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ 1:N
                         │
        ┌────────────────┴────────────────┐
        │                                  │
        ▼                                  ▼
┌───────────────────┐            ┌─────────────────────┐
│ businesses_user   │            │ products_product    │
├───────────────────┤            ├─────────────────────┤
│ id (PK)           │            │ id (PK)             │
│ email (unique)    │            │ name                │
│ password          │            │ description         │
│ first_name        │            │ price               │
│ last_name         │            │ status              │
│ role              │            │ business_id (FK)    │
│ business_id (FK)  │◄───────────┤ created_by_id (FK)  │
│ is_active         │            │ approved_by_id (FK) │
│ is_staff          │            │ created_at          │
│ is_superuser      │            │ updated_at          │
└─────────┬─────────┘            │ approved_at         │
          │                      └─────────────────────┘
          │
          │ 1:N
          │
          ▼
┌─────────────────────┐
│ chatbot_chatmessage │
├─────────────────────┤
│ id (PK)             │
│ user_id (FK)        │
│ user_message        │
│ ai_response         │
│ created_at          │
└─────────────────────┘
```

## API Request Flow

```
┌─────────┐                                              ┌─────────┐
│ Client  │                                              │ Server  │
└────┬────┘                                              └────┬────┘
     │                                                        │
     │  1. HTTP Request                                      │
     ├──────────────────────────────────────────────────────>│
     │     GET /api/products/                                │
     │     Authorization: Bearer <token>                     │
     │                                                        │
     │                                    2. Validate JWT    │
     │                                       Token           │
     │                                                        │
     │                                    3. Check           │
     │                                       Permissions     │
     │                                                        │
     │                                    4. Query           │
     │                                       Database        │
     │                                                        │
     │                                    5. Serialize       │
     │                                       Data            │
     │                                                        │
     │  6. HTTP Response                                     │
     │<──────────────────────────────────────────────────────┤
     │     200 OK                                            │
     │     {products: [...]}                                 │
     │                                                        │
```

## AI Chatbot Flow

```
┌──────┐         ┌──────────┐         ┌─────────┐         ┌─────────┐
│ User │         │ Frontend │         │ Backend │         │ OpenAI  │
└──┬───┘         └────┬─────┘         └────┬────┘         └────┬────┘
   │                  │                     │                    │
   │  1. Type query   │                     │                    │
   ├─────────────────>│                     │                    │
   │                  │                     │                    │
   │                  │  2. POST /chatbot/  │                    │
   │                  │     query/          │                    │
   │                  ├────────────────────>│                    │
   │                  │                     │                    │
   │                  │                     │  3. Get approved   │
   │                  │                     │     products       │
   │                  │                     │                    │
   │                  │                     │  4. Build context  │
   │                  │                     │     with products  │
   │                  │                     │                    │
   │                  │                     │  5. Call OpenAI    │
   │                  │                     ├───────────────────>│
   │                  │                     │                    │
   │                  │                     │  6. AI Response    │
   │                  │                     │<───────────────────┤
   │                  │                     │                    │
   │                  │                     │  7. Save to DB     │
   │                  │                     │                    │
   │                  │  8. Return response │                    │
   │                  │<────────────────────┤                    │
   │                  │                     │                    │
   │  9. Display      │                     │                    │
   │     response     │                     │                    │
   │<─────────────────┤                     │                    │
   │                  │                     │                    │
```

## Deployment Architecture (Production)

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS
                             │
                    ┌────────▼────────┐
                    │   CloudFlare    │
                    │   (CDN + SSL)   │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
        ┌───────▼────────┐       ┌───────▼────────┐
        │    Vercel      │       │    Railway     │
        │   (Frontend)   │       │   (Backend)    │
        │                │       │                │
        │  Next.js App   │       │  Django API    │
        └────────────────┘       └───────┬────────┘
                                         │
                                ┌────────┴────────┐
                                │                 │
                        ┌───────▼────────┐  ┌────▼─────┐
                        │   PostgreSQL   │  │ OpenAI   │
                        │   (Database)   │  │   API    │
                        └────────────────┘  └──────────┘
```

## Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: Transport Security                                │
│  ┌────────────────────────────────────────────────────┐    │
│  │ • HTTPS/TLS Encryption                             │    │
│  │ • Secure Cookies                                   │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 2: Authentication                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ • JWT Tokens                                       │    │
│  │ • Password Hashing (PBKDF2)                        │    │
│  │ • Token Expiration & Refresh                       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 3: Authorization                                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │ • Role-Based Access Control                        │    │
│  │ • Object-Level Permissions                         │    │
│  │ • Business Isolation                               │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 4: Input Validation                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │ • DRF Serializer Validation                        │    │
│  │ • SQL Injection Prevention (ORM)                   │    │
│  │ • XSS Prevention (React Escaping)                  │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 5: Application Security                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ • CORS Configuration                               │    │
│  │ • CSRF Protection                                  │    │
│  │ • Rate Limiting (Production)                       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Component Interaction

```
Frontend Components:
┌─────────────────────────────────────────────────────────┐
│                                                          │
│  ┌──────────────┐    ┌──────────────┐                  │
│  │   Layout     │───>│ AuthProvider │                  │
│  │  (Root)      │    │  (Context)   │                  │
│  └──────┬───────┘    └──────┬───────┘                  │
│         │                   │                           │
│         │                   │ Provides: user, logout,   │
│         │                   │ hasPermission()           │
│         │                   │                           │
│    ┌────┴────┬──────────────┴──────┬──────────┐        │
│    │         │                     │          │        │
│  ┌─▼──┐  ┌──▼────┐  ┌──────────┐ ┌▼────────┐ │        │
│  │Home│  │Login  │  │Dashboard │ │Chatbot  │ │        │
│  │Page│  │/      │  │          │ │         │ │        │
│  │    │  │Register│  │          │ │         │ │        │
│  └────┘  └───────┘  └──────────┘ └─────────┘ │        │
│                                                │        │
│  All use: api.ts (Axios with interceptors)    │        │
│                                                │        │
└────────────────────────────────────────────────┘        
```

## Data Flow Example: Creating a Product

```
1. User fills form in Dashboard
   ↓
2. Form validation (client-side)
   ↓
3. POST request to /api/products/
   ↓
4. Axios interceptor adds JWT token
   ↓
5. Backend receives request
   ↓
6. JWT middleware validates token
   ↓
7. Extract user from token
   ↓
8. Check user.has_permission('create_product')
   ↓
9. Validate product data (serializer)
   ↓
10. Create product in database
    - Set created_by = current user
    - Set business = user's business
    - Set status = 'draft'
   ↓
11. Return serialized product data
   ↓
12. Frontend receives response
   ↓
13. Update UI with new product
   ↓
14. Show success message
```

This architecture ensures:
- ✅ Separation of concerns
- ✅ Scalability
- ✅ Security
- ✅ Maintainability
- ✅ Testability
