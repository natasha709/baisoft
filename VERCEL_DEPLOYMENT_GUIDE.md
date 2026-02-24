# Vercel Deployment Guide

This guide will help you deploy the Product Marketplace application to Vercel.

## Prerequisites

1. Vercel account (sign up at https://vercel.com)
2. Git repository with your project
3. PostgreSQL database (Vercel doesn't support SQLite)

---

## Architecture Overview

This project has been converted to run on Vercel's Python serverless functions:
- **Backend**: Django API converted to Vercel Python functions (`/api/`)
- **Frontend**: Next.js 14 app
- **Database**: PostgreSQL (required for Vercel)

---

## Step 1: Set Up PostgreSQL Database

Since Vercel doesn't support SQLite, you need PostgreSQL.

### Option A: Vercel Postgres (Recommended)
1. Go to Vercel Dashboard → Your Project → Storage
2. Create a new Vercel Postgres database
3. Copy the connection string

### Option B: Supabase or Neon
1. Create a free PostgreSQL database at https://supabase.com or https://neon.tech
2. Get your connection string

---

## Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```
env
# Django Settings
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False
ALLOWED_HOSTS=your-project.vercel.app,vercel.app

# Database (PostgreSQL)
DATABASE_URL=postgres://username:password@host:5432/dbname

# OpenAI (optional)
OPENAI_API_KEY=your-openai-api-key

# CORS
CORS_ALLOWED_ORIGINS=https://your-project.vercel.app
```

---

## Step 3: Deploy to Vercel

### Option A: Vercel CLI

```
bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel
```

### Option B: Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Click "Add New..." → Project
3. Import your GitHub repository
4. Configure:
   - Framework Preset: Other
   - Build Command: Leave empty
   - Output Directory: Leave empty
5. Add Environment Variables
6. Click Deploy

---

## Step 4: Configure Vercel Environment Variables

In Vercel Dashboard → Your Project → Settings → Environment Variables:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Generate a secure key |
| `DEBUG` | false |
| `ALLOWED_HOSTS` | your-project.vercel.app |
| `DATABASE_URL` | Your PostgreSQL connection string |
| `OPENAI_API_KEY` | Your OpenAI key (optional) |
| `CORS_ALLOWED_ORIGINS` | https://your-project.vercel.app |

---

## Step 5: Run Database Migrations

After deployment, run migrations using Vercel CLI:

```
bash
vercel env pull .env.local
python manage.py migrate
```

Or create a setup endpoint:

```
python
# api/setup.py
from django.core.management import call_command
from django.http import JsonResponse

def handler(request):
    call_command('migrate', '--run-syncdb')
    return JsonResponse({'status': 'migrations complete'})
```

---

## Step 6: Update Frontend API URL

In Vercel Dashboard → Your Project → Settings → Environment Variables:

Add for frontend:
| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | https://your-project.vercel.app/api |

---

## API Endpoints

After deployment, your API will be available at:

| Endpoint | Description |
|----------|-------------|
| `/api/auth/login/` | User login |
| `/api/auth/register/` | User registration |
| `/api/auth/token/refresh/` | Refresh JWT token |
| `/api/auth/me/` | Get current user |
| `/api/products/` | List products |
| `/api/products/{id}/` | Product details |
| `/api/chatbot/query/` | Chat with AI |
| `/api/chatbot/history/` | Chat history |

---

## Testing the Deployment

1. Open your Vercel deployment URL
2. Try logging in or registering
3. Create a product
4. Test the chatbot

---

## Troubleshooting

### CORS Errors
- Ensure `CORS_ALLOWED_ORIGINS` includes your Vercel URL

### Database Connection
- Verify `DATABASE_URL` is correct
- Ensure PostgreSQL allows connections from Vercel

### 500 Errors
- Check Vercel function logs in Dashboard → Functions
- Verify all environment variables are set

### Static Files
- Configure Cloudflare or use Vercel blob storage for media files

---

## Files Created for Vercel

- `vercel.json` - Vercel configuration
- `api/index.py` - Main API handler
- `api/auth.py` - Authentication endpoints
- `api/products.py` - Products endpoints
- `api/chatbot.py` - Chatbot endpoints
- `requirements-vercel.txt` - Python dependencies
- `frontend/.env.local.example` - Frontend env template

---

## Important Notes

1. **Cold Starts**: Vercel serverless functions may have cold starts
2. **Function Timeout**: Maximum 10 seconds (60 seconds on Pro)
3. **Database Connections**: Use connection pooling for better performance
4. **API Rate Limits**: Vercel has rate limits on free tier
5. **Serverless Limitations**: No persistent filesystem, no background tasks

---

## Next Steps

1. Set up a custom domain (optional)
2. Configure SSL certificates
3. Set up monitoring with Sentry
4. Add CI/CD with GitHub Actions
