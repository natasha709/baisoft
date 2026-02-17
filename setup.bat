@echo off
echo Setting up Product Marketplace...

REM Backend setup
echo Setting up backend...
cd backend

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

REM Copy env file
if not exist .env (
    copy .env.example .env
    echo Please update backend\.env with your settings (especially OPENAI_API_KEY)
)

REM Run migrations
python manage.py migrate

REM Create superuser
echo Create a superuser account:
python manage.py createsuperuser

cd ..

REM Frontend setup
echo Setting up frontend...
cd frontend

REM Install dependencies
call npm install

REM Copy env file
if not exist .env.local (
    copy .env.local.example .env.local
)

cd ..

echo Setup complete!
echo.
echo To start the application:
echo 1. Backend: cd backend ^&^& python manage.py runserver
echo 2. Frontend: cd frontend ^&^& npm run dev
echo.
echo Then visit http://localhost:3000

pause
