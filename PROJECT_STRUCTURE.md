# Project Structure

## Complete Directory Tree

```
product-marketplace/
│
├── README.md                      # Main project documentation
├── QUICKSTART.md                  # Quick setup guide
├── API_DOCUMENTATION.md           # Complete API reference
├── PROJECT_OVERVIEW.md            # Architecture overview
├── TESTING_GUIDE.md               # Testing procedures
├── DEPLOYMENT.md                  # Production deployment guide
├── CONTRIBUTING.md                # Contribution guidelines
├── SUBMISSION_SUMMARY.md          # Assignment submission summary
├── PROJECT_STRUCTURE.md           # This file
├── LICENSE                        # MIT License
├── .gitignore                     # Git ignore rules
├── setup.sh                       # Linux/Mac setup script
└── setup.bat                      # Windows setup script
│
├── backend/                       # Django Backend
│   ├── config/                    # Django project configuration
│   │   ├── __init__.py
│   │   ├── settings.py           # Django settings
│   │   ├── urls.py               # Main URL configuration
│   │   ├── wsgi.py               # WSGI configuration
│   │   └── asgi.py               # ASGI configuration
│   │
│   ├── businesses/                # Business & User management app
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py             # Business, User models
│   │   ├── serializers.py        # DRF serializers
│   │   ├── views.py              # API views
│   │   ├── urls.py               # App URLs
│   │   └── admin.py              # Django admin config
│   │
│   ├── products/                  # Product management app
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py             # Product model
│   │   ├── serializers.py        # DRF serializers
│   │   ├── views.py              # API views
│   │   ├── urls.py               # App URLs
│   │   ├── permissions.py        # Custom permissions
│   │   ├── admin.py              # Django admin config
│   │   └── tests.py              # Unit tests
│   │
│   ├── chatbot/                   # AI Chatbot app
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py             # ChatMessage model
│   │   ├── serializers.py        # DRF serializers
│   │   ├── views.py              # API views
│   │   ├── urls.py               # App URLs
│   │   ├── ai_service.py         # OpenAI integration
│   │   └── admin.py              # Django admin config
│   │
│   ├── manage.py                  # Django management script
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example              # Environment variables template
│   ├── .gitignore                # Git ignore rules
│   └── db.sqlite3                # SQLite database (created on setup)
│
└── frontend/                      # Next.js Frontend
    ├── src/
    │   ├── app/                   # Next.js App Router
    │   │   ├── layout.tsx        # Root layout
    │   │   ├── page.tsx          # Home page (public products)
    │   │   ├── globals.css       # Global styles
    │   │   │
    │   │   ├── login/
    │   │   │   └── page.tsx      # Login page
    │   │   │
    │   │   ├── register/
    │   │   │   └── page.tsx      # Registration page
    │   │   │
    │   │   ├── dashboard/
    │   │   │   └── page.tsx      # Product management dashboard
    │   │   │
    │   │   └── chatbot/
    │   │       └── page.tsx      # AI chatbot interface
    │   │
    │   ├── components/            # React components (if needed)
    │   │
    │   ├── contexts/
    │   │   └── AuthContext.tsx   # Authentication context
    │   │
    │   └── lib/
    │       ├── api.ts            # Axios instance & interceptors
    │       └── auth.ts           # Auth utilities
    │
    ├── public/                    # Static assets
    │
    ├── package.json               # Node dependencies
    ├── tsconfig.json             # TypeScript configuration
    ├── next.config.js            # Next.js configuration
    ├── tailwind.config.js        # TailwindCSS configuration
    ├── postcss.config.js         # PostCSS configuration
    ├── .env.local.example        # Environment variables template
    ├── .gitignore                # Git ignore rules
    └── .next/                    # Next.js build output (created on build)
```

## File Descriptions

### Root Level Files

| File | Purpose |
|------|---------|
| README.md | Main project documentation with overview and setup |
| QUICKSTART.md | Fast setup guide for getting started quickly |
| API_DOCUMENTATION.md | Complete API endpoint reference |
| PROJECT_OVERVIEW.md | Detailed architecture and design decisions |
| TESTING_GUIDE.md | Manual and automated testing procedures |
| DEPLOYMENT.md | Production deployment instructions |
| CONTRIBUTING.md | Guidelines for contributing to the project |
| SUBMISSION_SUMMARY.md | Assignment submission details |
| LICENSE | MIT License |
| setup.sh | Automated setup script for Linux/Mac |
| setup.bat | Automated setup script for Windows |

### Backend Structure

#### config/
Django project configuration directory
- `settings.py`: All Django settings (database, apps, middleware, etc.)
- `urls.py`: Main URL routing
- `wsgi.py`: WSGI server configuration
- `asgi.py`: ASGI server configuration

#### businesses/
User and business management
- `models.py`: Business and User models with role-based permissions
- `serializers.py`: API serializers for registration, login, user management
- `views.py`: Authentication endpoints and user management views
- `urls.py`: Auth-related URL patterns
- `admin.py`: Django admin customization

#### products/
Product management with approval workflow
- `models.py`: Product model with status tracking
- `serializers.py`: Product serializers for CRUD operations
- `views.py`: Product CRUD and approval endpoints
- `permissions.py`: Custom permission classes
- `urls.py`: Product-related URL patterns
- `tests.py`: Unit tests for product functionality
- `admin.py`: Django admin customization

#### chatbot/
AI-powered product assistant
- `models.py`: ChatMessage model for history
- `serializers.py`: Chat serializers
- `views.py`: Chat query and history endpoints
- `ai_service.py`: OpenAI API integration
- `urls.py`: Chatbot URL patterns
- `admin.py`: Django admin customization

### Frontend Structure

#### src/app/
Next.js pages using App Router
- `layout.tsx`: Root layout with AuthProvider
- `page.tsx`: Public homepage with approved products
- `globals.css`: Global styles and TailwindCSS imports
- `login/page.tsx`: Login page
- `register/page.tsx`: Registration page
- `dashboard/page.tsx`: Product management dashboard
- `chatbot/page.tsx`: AI chatbot interface

#### src/contexts/
React Context providers
- `AuthContext.tsx`: Authentication state management

#### src/lib/
Utility functions and configurations
- `api.ts`: Axios instance with interceptors for auth
- `auth.ts`: Authentication utilities (login, register, logout)

## Key Features by Directory

### Backend Features

**businesses/**
- JWT authentication
- User registration and login
- Role-based access control (Admin, Editor, Approver, Viewer)
- Business multi-tenancy
- User management

**products/**
- Product CRUD operations
- Three-state approval workflow
- Permission-based access control
- Public product listing
- Product filtering and pagination

**chatbot/**
- OpenAI GPT-4 integration
- Natural language product queries
- Chat history storage
- Context-aware responses

### Frontend Features

**app/**
- Public product listing (no auth required)
- User authentication (login/register)
- Protected routes
- Product management dashboard
- AI chatbot interface

**contexts/**
- Global authentication state
- Permission checking
- User data management

**lib/**
- API client with automatic token refresh
- Authentication utilities
- Type-safe API calls

## Data Flow

### Authentication Flow
```
User → Frontend (login) → Backend (JWT) → Frontend (store token) → Dashboard
```

### Product Creation Flow
```
User → Dashboard → Create Form → API → Backend (validate permissions) → Database → Response
```

### Product Approval Flow
```
Editor creates → Admin/Approver approves → Status changes → Public listing updates
```

### Chatbot Flow
```
User → Chat Interface → API → Backend → OpenAI → Response → Chat History → User
```

## Database Schema

### Tables
1. **businesses_business**: Business information
2. **businesses_user**: Users with roles
3. **products_product**: Products with approval status
4. **chatbot_chatmessage**: Chat history

### Relationships
- User → Business (Many-to-One)
- Product → Business (Many-to-One)
- Product → User (created_by, approved_by)
- ChatMessage → User (Many-to-One)

## API Endpoints Summary

### Authentication
- POST `/api/auth/register/`
- POST `/api/auth/login/`
- POST `/api/auth/token/refresh/`
- GET `/api/auth/me/`

### Products
- GET/POST `/api/products/`
- GET/PUT/DELETE `/api/products/{id}/`
- POST `/api/products/{id}/approve/`
- POST `/api/products/{id}/submit_for_approval/`

### Chatbot
- POST `/api/chatbot/query/`
- GET `/api/chatbot/history/`

## Environment Variables

### Backend (.env)
```
SECRET_KEY=django-secret-key
DEBUG=True/False
ALLOWED_HOSTS=localhost,127.0.0.1
OPENAI_API_KEY=sk-your-key
DATABASE_URL=sqlite:///db.sqlite3
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Build Artifacts (Not in Git)

### Backend
- `db.sqlite3`: SQLite database
- `__pycache__/`: Python bytecode
- `*.pyc`: Compiled Python files
- `venv/`: Virtual environment

### Frontend
- `node_modules/`: NPM packages
- `.next/`: Next.js build output
- `out/`: Static export output

## Development vs Production

### Development
- SQLite database
- DEBUG=True
- Local file storage
- Development server

### Production
- PostgreSQL database
- DEBUG=False
- Cloud storage (S3)
- Gunicorn/uWSGI server
- Nginx reverse proxy
- SSL/HTTPS

## Getting Started

1. Clone the repository
2. Run setup script (`setup.sh` or `setup.bat`)
3. Configure environment variables
4. Start backend: `python manage.py runserver`
5. Start frontend: `npm run dev`
6. Access at http://localhost:3000

For detailed instructions, see QUICKSTART.md
