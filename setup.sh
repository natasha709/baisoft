#!/bin/bash

echo "🚀 Setting up Product Marketplace..."

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
pip install -r requirements.txt

# Copy env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please update backend/.env with your settings (especially OPENAI_API_KEY)"
fi

# Run migrations
python manage.py migrate

# Create superuser prompt
echo "📝 Create a superuser account:"
python manage.py createsuperuser

cd ..

# Frontend setup
echo "📦 Setting up frontend..."
cd frontend

# Install dependencies
npm install

# Copy env file
if [ ! -f .env.local ]; then
    cp .env.local.example .env.local
fi

cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend: cd backend && python manage.py runserver"
echo "2. Frontend: cd frontend && npm run dev"
echo ""
echo "Then visit http://localhost:3000"
