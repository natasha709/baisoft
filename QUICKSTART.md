# Quick Start Guide

## Automated Setup (Recommended)

### Windows
```bash
setup.bat
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

## Manual Setup

### Backend

1. Create virtual environment:
```bash
cd backend
python -m venv venv
```

2. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-key-here
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Start server:
```bash
python manage.py runserver
```

### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create `.env.local`:
```bash
cp .env.local.example .env.local
```

3. Start development server:
```bash
npm run dev
```

## Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Django Admin: http://localhost:8000/admin

## Test the Application

1. Register a new account (creates a business and admin user)
2. Login to dashboard
3. Create products
4. Submit products for approval
5. Approve products (if you have permission)
6. View approved products on public homepage
7. Try the AI chatbot to ask about products

## Running Tests

```bash
cd backend
python manage.py test
```

## Default User Roles

When you register, you become an Admin with all permissions:
- Admin: Create, edit, approve, delete products
- Editor: Create and edit products
- Approver: Approve products only
- Viewer: View products only

## Troubleshooting

### Backend won't start
- Make sure virtual environment is activated
- Check all dependencies are installed: `pip install -r requirements.txt`
- Verify migrations are run: `python manage.py migrate`

### Frontend won't start
- Delete `node_modules` and `.next` folders
- Run `npm install` again
- Check `.env.local` exists

### AI Chatbot not working
- Verify `OPENAI_API_KEY` is set in `backend/.env`
- Check you have credits in your OpenAI account
- Look at backend console for error messages

### CORS errors
- Make sure backend is running on port 8000
- Check `CORS_ALLOWED_ORIGINS` in `backend/config/settings.py`
