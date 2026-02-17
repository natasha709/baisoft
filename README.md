# Product Marketplace with Roles, Approvals & AI Chatbot

## What I Implemented

### Backend (Django)
- JWT authentication with role-based access control
- Business model with user management
- Product CRUD with approval workflow
- Permission system (Admin, Editor, Approver, Viewer)
- RESTful API with Django REST Framework
- Object-level permissions
- Comprehensive test coverage

### Frontend (Next.js)
- Authentication (login/logout)
- Product management dashboard
- Role-based UI rendering
- Public product listing
- Responsive design
- Form validation and error handling

### AI Chatbot
- OpenAI integration for product queries
- Context-aware responses
- Chat history storage
- Only shows approved products to users

## Tech Stack

- **Backend**: Django 5.0, Django REST Framework, PostgreSQL/SQLite
- **Frontend**: Next.js 14, React, TailwindCSS, Axios
- **AI**: OpenAI API (GPT-4)
- **Authentication**: JWT (djangorestframework-simplejwt)

## Project Structure

```
product-marketplace/
├── backend/              # Django backend
│   ├── api/             # Main API app
│   ├── products/        # Products app
│   ├── businesses/      # Business management
│   ├── chatbot/         # AI chatbot
│   └── manage.py
├── frontend/            # Next.js frontend
│   ├── src/
│   │   ├── app/        # App router
│   │   ├── components/ # React components
│   │   └── lib/        # Utilities
│   └── package.json
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (optional, SQLite works too)
- OpenAI API key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
SECRET_KEY=your-secret-key
DEBUG=True
OPENAI_API_KEY=your-openai-api-key
DATABASE_URL=sqlite:///db.sqlite3
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run server:
```bash
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

4. Run development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Products
- `GET /api/products/` - List products (filtered by permissions)
- `POST /api/products/` - Create product
- `GET /api/products/{id}/` - Get product details
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product
- `POST /api/products/{id}/approve/` - Approve product

### Business & Users
- `GET /api/businesses/` - List businesses
- `POST /api/businesses/` - Create business
- `GET /api/users/` - List users in business
- `POST /api/users/` - Create user with role

### Chatbot
- `POST /api/chatbot/query/` - Send message to AI chatbot
- `GET /api/chatbot/history/` - Get chat history

## User Roles & Permissions

| Role | Create Product | Edit Product | Approve Product | Delete Product | View All |
|------|---------------|--------------|-----------------|----------------|----------|
| Admin | Yes | Yes | Yes | Yes | Yes |
| Editor | Yes | Yes | No | No | Yes |
| Approver | No | No | Yes | No | Yes |
| Viewer | No | No | No | No | Yes |

## Tech Decisions & Assumptions

### Backend
- **JWT Authentication**: Chosen for stateless authentication, better for API consumption
- **Role-based permissions**: Implemented using Django's permission system with custom permissions
- **Product approval workflow**: Three states (draft, pending_approval, approved)
- **SQLite default**: Easy setup, can switch to PostgreSQL for production

### Frontend
- **Next.js App Router**: Modern approach with server/client components
- **TailwindCSS**: Rapid UI development with utility classes
- **Axios**: HTTP client with interceptors for auth tokens
- **Context API**: State management for auth

### AI Chatbot
- **OpenAI GPT-4**: Reliable and powerful for natural language queries
- **Context injection**: Product data injected into prompts for accurate responses
- **Permission-aware**: Only shows approved products to regular users

## Known Limitations

1. **File uploads**: Product images not implemented (can be added with django-storages)
2. **Real-time updates**: No WebSocket support (could add Django Channels)
3. **Email notifications**: Not implemented for approval workflows
4. **Rate limiting**: Not implemented for API endpoints
5. **Pagination**: Basic implementation, could be enhanced
6. **AI costs**: OpenAI API calls cost money, consider caching common queries

## Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests (if implemented)
```bash
cd frontend
npm test
```

## Production Considerations

1. Set `DEBUG=False` in Django settings
2. Use PostgreSQL instead of SQLite
3. Configure CORS properly
4. Add rate limiting
5. Use environment variables for all secrets
6. Set up proper logging
7. Add monitoring (Sentry, etc.)
8. Use Redis for caching
9. Deploy backend (Railway, Heroku, AWS)
10. Deploy frontend (Vercel, Netlify)

## Future Enhancements

- Product categories and tags
- Advanced search and filtering
- Product image uploads
- Email notifications
- Audit logs
- Analytics dashboard
- Multi-language support
- Export functionality
- Bulk operations

## License

MIT

## Contact

For questions or issues, please contact: tech@baisoftglobal.com
