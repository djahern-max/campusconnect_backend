# 🎓 CampusConnect Backend

**B2B SaaS platform connecting institutions with students through premium directory listings and customizable admin dashboards.**

[![Tests](https://img.shields.io/badge/tests-24%2F24%20passing-brightgreen)]()
[![Status](https://img.shields.io/badge/status-production%20ready-blue)]()
[![Python](https://img.shields.io/badge/python-3.11-blue)]()
[![FastAPI](https://img.shields.io/badge/fastapi-0.104-green)]()

---

## ✨ Features

### Core Features
- ✅ **Authentication** - JWT-based admin authentication
- ✅ **Subscriptions** - Stripe integration with 30-day free trials ($39.99/month)
- ✅ **Image Hosting** - DigitalOcean Spaces CDN
- ✅ **Webhooks** - Real-time Stripe event handling
- ✅ **Rate Limiting** - API abuse protection
- ✅ **Logging** - Comprehensive request/error logging
- ✅ **Docker Ready** - Production deployment with Docker Compose

### Phase 1 Features (NEW!) ⭐
- ✅ **Gallery Management** - Upload, caption, reorder multiple images
- ✅ **Video Management** - Embed YouTube/Vimeo videos
- ✅ **Extended Info** - 15+ rich text fields + custom sections
- ✅ **Complete Customization** - Admins control what displays

### Testing
- ✅ **24/24 Integration Tests Passing** - 100% coverage on critical paths

---

## 🎯 What Makes This Special

**Institutions can create rich, customizable profile pages with:**
- 📸 Unlimited image galleries with captions
- 🎥 Embedded videos (campus tours, testimonials)
- 📝 Detailed content (15+ sections)
- 🎨 Custom branding (colors, layouts, taglines)
- 🔧 Complete control (show/hide any section)

**Students discover:**
- Visual campus tours
- Detailed program information
- Student life insights
- Financial aid details
- Custom institutional content

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
- **[Phase 1 Complete](PHASE_1_COMPLETE.md)** - Gallery, videos & extended info features
- **[Start Here](START_HERE.md)** - Quick reference guide

---

## 🧪 Testing
```bash
# Run all tests (24 tests)
pytest tests/test_integration.py -v

# Generate API documentation
python tests/generate_api_docs.py
```

**Test Coverage:** 24/24 tests passing (100%)

**Test Categories:**
- Public endpoints (7 tests)
- Authentication (3 tests)
- Admin profile (3 tests)
- Subscriptions (2 tests)
- Gallery management (2 tests) ⭐
- Video management (2 tests) ⭐
- Extended info (2 tests) ⭐
- Error handling (3 tests)

---

## 🏗️ Tech Stack

- **Framework:** FastAPI (async Python)
- **Database:** PostgreSQL with asyncpg
- **ORM:** SQLAlchemy
- **Auth:** JWT tokens (30-min expiry)
- **Payments:** Stripe API
- **Images:** DigitalOcean Spaces CDN
- **Deployment:** Docker + Docker Compose
- **Proxy:** nginx

---

## 📊 Database

### Core Tables
- **609 Institutions** - US post-secondary institutions
- **126 Scholarships** - Verified scholarships
- **Admin Users** - Institution/scholarship administrators
- **Subscriptions** - Stripe subscription management
- **Display Settings** - Customization controls

### Phase 1 Tables (NEW!) ⭐
- **Institution Images** - Gallery management
- **Institution Videos** - Video embeds
- **Institution Extended Info** - Rich content

**Total:** 9 tables with complete relationships

---

## 🔒 Security

- JWT authentication (30-min tokens)
- Password hashing (PBKDF2)
- Rate limiting (5/min auth, 100/min public)
- CORS protection
- Input validation (Pydantic)
- Comprehensive error handling
- Request logging

---

## 📝 API Endpoints

### Public Endpoints (No Auth)
```
GET  /api/v1/institutions              - List institutions
GET  /api/v1/institutions/{ipeds_id}   - Get institution
GET  /api/v1/scholarships              - List scholarships
GET  /api/v1/scholarships/{id}         - Get scholarship
```

### Admin Auth
```
POST /api/v1/admin/auth/register       - Register admin
POST /api/v1/admin/auth/login          - Login (get JWT)
GET  /api/v1/admin/auth/me             - Get current user
```

### Admin Profile
```
GET  /api/v1/admin/profile/entity      - Get institution/scholarship
GET  /api/v1/admin/profile/display-settings  - Get settings
PUT  /api/v1/admin/profile/display-settings  - Update settings
```

### Gallery Management (NEW!) ⭐
```
GET    /api/v1/admin/gallery           - List all images
POST   /api/v1/admin/gallery           - Upload image
PUT    /api/v1/admin/gallery/{id}      - Update image
DELETE /api/v1/admin/gallery/{id}      - Delete image
PUT    /api/v1/admin/gallery/reorder   - Reorder images
```

### Video Management (NEW!) ⭐
```
GET    /api/v1/admin/videos            - List all videos
POST   /api/v1/admin/videos            - Add video
PUT    /api/v1/admin/videos/{id}       - Update video
DELETE /api/v1/admin/videos/{id}       - Delete video
PUT    /api/v1/admin/videos/reorder    - Reorder videos
```

### Extended Info (NEW!) ⭐
```
GET    /api/v1/admin/extended-info     - Get extended info
PUT    /api/v1/admin/extended-info     - Update info
DELETE /api/v1/admin/extended-info     - Clear info
```

### Subscriptions
```
POST /api/v1/admin/subscriptions/create-checkout  - Create Stripe checkout
GET  /api/v1/admin/subscriptions/current          - Get subscription
POST /api/v1/admin/subscriptions/cancel           - Cancel subscription
GET  /api/v1/admin/subscriptions/portal           - Customer portal
```

Full API documentation: http://localhost:8000/docs

---

## 🎨 Frontend Integration

### Quick Example - Gallery Upload
```typescript
const formData = new FormData();
formData.append('file', imageFile);
formData.append('caption', 'Beautiful campus view');
formData.append('image_type', 'campus');

const response = await fetch('/api/v1/admin/gallery', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});

const image = await response.json();
// Use image.cdn_url to display
```

### Quick Example - Add Video
```typescript
await fetch('/api/v1/admin/videos', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    video_url: 'https://youtube.com/watch?v=...',
    title: 'Campus Tour 2025',
    video_type: 'tour'
  })
});
```

### TypeScript Types Available

All TypeScript interfaces are available in `api_docs/types.ts`:
- Institution
- Scholarship
- AdminUser
- DisplaySettings
- **InstitutionImage** ⭐
- **InstitutionVideo** ⭐
- **InstitutionExtendedInfo** ⭐

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
# Database
DATABASE_URL=postgresql://postgres:PASSWORD@localhost:5432/campusconnect_db

# Security
SECRET_KEY=your-secret-key-here

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# DigitalOcean Spaces
DIGITAL_OCEAN_SPACES_ACCESS_KEY=...
DIGITAL_OCEAN_SPACES_SECRET_KEY=...
DIGITAL_OCEAN_SPACES_BUCKET=your-bucket-name
IMAGE_CDN_BASE_URL=https://your-bucket.cdn.digitaloceanspaces.com

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
- [ ] Enable rate limiting
- [ ] Configure monitoring

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete guide.

---

## 📈 What This Enables

### For Institutions - Simple Pages
- Add 2-3 images
- Embed 1 campus tour video
- Write basic campus description
- Toggle off unused sections
- **Result:** Clean, minimal page

### For Institutions - Rich Pages
- Upload 20+ images (full gallery)
- Add 5+ videos (tours, testimonials)
- Write detailed content (all 15+ fields)
- Add unlimited custom sections
- **Result:** Comprehensive showcase

### For Students
- Visual campus exploration
- Detailed program information
- Student life insights
- Financial aid guidance
- Authentic institutional content

---

## 🎯 Project Status

- **Backend:** ✅ 100% Complete (including Phase 1)
- **Tests:** ✅ 24/24 Passing
- **Documentation:** ✅ Complete
- **Deployment:** ✅ Docker Ready
- **Status:** ✅ Production Ready

### Feature Completion
- ✅ Core API (institutions, scholarships)
- ✅ Authentication & authorization
- ✅ Subscription management (Stripe)
- ✅ Image hosting (CDN)
- ✅ Display settings
- ✅ **Gallery management** ⭐
- ✅ **Video management** ⭐
- ✅ **Extended info** ⭐
- ✅ Rate limiting & logging
- ✅ Error handling
- ✅ Docker deployment

---

## 🤝 Contributing

This is a private repository. For questions or issues, contact the project maintainer.

---

## 📄 License

Proprietary - All rights reserved

---

## 📧 Contact

**Developer:** Danny Ahern  
**GitHub:** [@djahern-max](https://github.com/djahern-max)

---

**Built with ❤️ for students and institutions**

*Empowering students to find their perfect college match with rich, authentic institutional content.*

---

## 🎉 Recent Updates

### Phase 1 Complete (November 15, 2025)
- ✅ Gallery management system
- ✅ Video embed system
- ✅ Extended information system
- ✅ Complete customization controls
- ✅ 6 new API endpoints
- ✅ 3 new database tables
- ✅ TypeScript interfaces updated
- ✅ Tests updated (24/24 passing)

**The backend now fully supports the vision of customizable, rich institutional profile pages!** 🚀
