# Vercel Deployment TODO List

## Phase 1: Backend Conversion (Django → Vercel Serverless)

- [x] 1.1 Create `vercel.json` configuration
- [x] 1.2 Create `api/index.py` - Python handler
- [x] 1.3 Create `api/auth.py` - Authentication endpoints
- [x] 1.4 Create `api/products.py` - Product endpoints  
- [x] 1.5 Create `api/chatbot.py` - Chatbot endpoints
- [x] 1.6 Create `requirements-vercel.txt` for Python runtime
- [x] 1.7 Set up PostgreSQL database configuration
- [x] 1.8 Fix API handler for Vercel request/response format

## Phase 2: Frontend Configuration

- [x] 2.1 Frontend already has environment variable support
- [x] 2.2 Frontend API already uses NEXT_PUBLIC_API_URL
- [x] 2.3 Create `frontend/.env.local` template

## Phase 3: Environment Configuration

- [x] 3.1 Document required environment variables
- [x] 3.2 Settings support production via environment variables

## Phase 4: Deployment Instructions

- [x] 4.1 Create deployment guide (VERCEL_DEPLOYMENT_GUIDE.md)

## Phase 5: CI/CD Integration

- [x] 5.1 Add Vercel deployment workflow (.github/workflows/vercel.yml)
- [x] 5.2 Configure preview and production deployments

## Phase 6: Configuration Updates

- [x] 6.1 Update vercel.json with proper routing and framework settings
- [x] 6.2 Fix api/index.py for Vercel request handling

---

## Deployment Checklist

Before deploying to Vercel, ensure:

- [ ] Vercel account is set up
- [ ] PostgreSQL database is created (Vercel Postgres or external)
- [ ] Environment variables are configured in Vercel dashboard:
  - [ ] SECRET_KEY
  - [ ] DEBUG=false
  - [ ] ALLOWED_HOSTS
  - [ ] DATABASE_URL
  - [ ] OPENAI_API_KEY (optional)
  - [ ] CORS_ALLOWED_ORIGINS
- [ ] GitHub repository is connected to Vercel
- [ ] VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID secrets are set in GitHub

## Post-Deployment

- [ ] Run database migrations
- [ ] Test all API endpoints
- [ ] Verify frontend loads correctly
- [ ] Test authentication flow
- [ ] Test product creation and listing
- [ ] Test chatbot functionality
