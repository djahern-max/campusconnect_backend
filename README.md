# 🎓 CampusConnect Backend

**B2B SaaS platform connecting institutions with students through premium directory listings and admin dashboards.**

[![Tests](https://img.shields.io/badge/tests-18%2F18%20passing-brightgreen)]()
[![Status](https://img.shields.io/badge/status-production%20ready-blue)]()
[![Python](https://img.shields.io/badge/python-3.11-blue)]()
[![FastAPI](https://img.shields.io/badge/fastapi-0.104-green)]()

---

## ✨ Features

- ✅ **Authentication** - JWT-based admin authentication
- ✅ **Subscriptions** - Stripe integration with 30-day free trials ($39.99/month)
- ✅ **Image Hosting** - DigitalOcean Spaces CDN
- ✅ **Webhooks** - Real-time Stripe event handling
- ✅ **Rate Limiting** - API abuse protection
- ✅ **Logging** - Comprehensive request/error logging
- ✅ **Docker Ready** - Production deployment with Docker Compose
- ✅ **Tested** - 18/18 integration tests passing

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Stripe account (test mode)
- DigitalOcean Spaces (or compatible S3)

### Local Development
```bash
# Clone repository
git clone https://github.com/djahern-max/campusconnect_backend.git
cd campusconnect_backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your values

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API Documentation:** http://localhost:8000/docs

---

## 📚 Documentation

- **[Frontend Handoff Guide](FRONTEND_HANDOFF.md)** - Complete integration guide for frontend developers
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment instructions
- **[API Contract](API_CONTRACT.md)** - Detailed API specification
- **[Project Complete](🎉_BACKEND_COMPLETE_🎉.md)** - Completion summary

---

## 🧪 Testing
```bash
# Run all tests
pytest tests/test_integration.py -v

# Generate API documentation
python tests/generate_api_docs.py
```

**Test Coverage:** 18/18 tests passing (100%)

---

## 🏗️ Tech Stack

- **Framework:** FastAPI (async Python)
- **Database:** PostgreSQL with asyncpg
- **ORM:** SQLAlchemy
- **Auth:** JWT tokens
- **Payments:** Stripe API
- **Images:** DigitalOcean Spaces
- **Deployment:** Docker + Docker Compose
- **Proxy:** nginx

---

## 📊 Database

- **609 Institutions** - US post-secondary institutions
- **126 Scholarships** - Verified scholarships
- **Polymorphic Design** - Flexible entity management

---

## 🔒 Security

- JWT authentication
- Password hashing (PBKDF2)
- Rate limiting (5/min auth, 100/min public)
- CORS protection
- Input validation (Pydantic)
- Comprehensive error handling

---

## 🐳 Docker Deployment
```bash
# Deploy full stack
docker-compose up -d

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head
```

---

## 📝 Environment Variables

See `.env.example` for required variables:
```bash
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
STRIPE_SECRET_KEY=sk_test_...
DIGITAL_OCEAN_SPACES_ACCESS_KEY=...
# ... and more
```

---

## 🚀 Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Generate secure `SECRET_KEY`
- [ ] Switch to Stripe live keys
- [ ] Configure SSL certificates
- [ ] Set up database backups
- [ ] Update `ALLOWED_ORIGINS`

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete guide.

---

## 📞 API Endpoints

### Public (No Auth)
- `GET /api/v1/institutions` - List institutions
- `GET /api/v1/institutions/{ipeds_id}` - Get institution
- `GET /api/v1/scholarships` - List scholarships
- `GET /api/v1/scholarships/{id}` - Get scholarship

### Admin (Auth Required)
- `POST /api/v1/admin/auth/login` - Login
- `GET /api/v1/admin/profile/entity` - Get entity
- `PUT /api/v1/admin/profile/display-settings` - Update settings
- `POST /api/v1/admin/images/upload` - Upload image
- `POST /api/v1/admin/subscriptions/create-checkout` - Create checkout

Full API documentation: http://localhost:8000/docs

---

## 🤝 Contributing

This is a private repository. For questions or issues, contact the project maintainer.

---

## 📄 License

Proprietary - All rights reserved

---

## 🎯 Project Status

- **Backend:** ✅ 100% Complete
- **Tests:** ✅ 18/18 Passing
- **Documentation:** ✅ Complete
- **Deployment:** ✅ Docker Ready
- **Status:** ✅ Production Ready

---

**Built with ❤️ for students and institutions**

*Ready to change how students find colleges and scholarships.*

---

## 📧 Contact

**Developer:** Danny Ahern  
**GitHub:** [@djahern-max](https://github.com/djahern-max)
