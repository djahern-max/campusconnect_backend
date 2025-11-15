# 🎨 CampusConnect Frontend Development Guide

**Backend Version:** 1.0.0  
**Status:** Production Ready  
**All Tests:** ✅ 18/18 Passing

---

## 📦 What You're Getting

This backend provides a complete API for the CampusConnect platform with:
- ✅ **609 Institutions** - Real US college data
- ✅ **126 Scholarships** - Verified scholarship data
- ✅ **Authentication** - JWT-based admin auth
- ✅ **Payments** - Stripe integration ($39.99/month with 30-day trials)
- ✅ **Image Hosting** - DigitalOcean Spaces CDN
- ✅ **Real-time Webhooks** - Subscription sync

---

## 🚀 Quick Start

### 1. Backend Setup

The backend developer will run:
```bash
cd campusconnect-backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend available at: **http://localhost:8000**

### 2. Explore the API

- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** `api_docs/openapi.json`

### 3. Test Credentials

Contact backend developer for test credentials.

---

## 📚 Documentation Files

### Available for You:

1. **`api_docs/openapi.json`** - Full OpenAPI 3.0 specification
2. **`api_docs/types.ts`** - TypeScript interfaces for all data models
3. **`api_docs/example_requests.json`** - Example API calls
4. **`tests/sample_institution.json`** - Sample institution data
5. **`tests/sample_scholarship.json`** - Sample scholarship data
6. **`tests/sample_display_settings.json`** - Sample display settings

---

## 🔑 Authentication Flow

### 1. Register Admin
```typescript
const response = await fetch('http://localhost:8000/api/v1/admin/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'admin@example.com',
    password: 'securepassword',
    entity_type: 'institution',  // or 'scholarship'
    entity_id: 1
  })
});
```

### 2. Login
```typescript
const formData = new FormData();
formData.append('username', 'admin@example.com');
formData.append('password', 'securepassword');

const response = await fetch('http://localhost:8000/api/v1/admin/auth/login', {
  method: 'POST',
  body: formData
});

const { access_token } = await response.json();
localStorage.setItem('auth_token', access_token);
```

### 3. Make Authenticated Requests
```typescript
const token = localStorage.getItem('auth_token');

const response = await fetch('http://localhost:8000/api/v1/admin/profile/entity', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

---

## 🏗️ Key Endpoints

### Public Endpoints (No Auth Required)
```typescript
// Get all institutions
GET /api/v1/institutions?limit=100&offset=0

// Filter by state
GET /api/v1/institutions?state=NH

// Get single institution
GET /api/v1/institutions/{ipeds_id}

// Get all scholarships
GET /api/v1/scholarships?limit=100&offset=0

// Get single scholarship
GET /api/v1/scholarships/{id}
```

### Admin Endpoints (Auth Required)
```typescript
// Get my institution/scholarship
GET /api/v1/admin/profile/entity

// Get display settings
GET /api/v1/admin/profile/display-settings

// Update display settings
PUT /api/v1/admin/profile/display-settings

// Upload image
POST /api/v1/admin/images/upload

// Create subscription checkout
POST /api/v1/admin/subscriptions/create-checkout

// Get current subscription
GET /api/v1/admin/subscriptions/current
```

---

## 📊 Data Models

See `api_docs/types.ts` for complete TypeScript definitions!

### Institution (Preview)
```typescript
interface Institution {
  id: number;
  ipeds_id: number;
  name: string;
  city: string;
  state: string;
  control_type: 'PUBLIC' | 'PRIVATE_NONPROFIT' | 'PRIVATE_FOR_PROFIT';
  primary_image_url: string | null;
  student_faculty_ratio: number | null;
  size_category: string | null;
  locale: string | null;
  created_at: string;
  updated_at: string;
}
```

---

## 💳 Stripe Integration

### Create Checkout Session
```typescript
const token = localStorage.getItem('auth_token');

const response = await fetch('http://localhost:8000/api/v1/admin/subscriptions/create-checkout', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const { checkout_url } = await response.json();
window.location.href = checkout_url;
```

### Success/Cancel URLs

Set these in your frontend router:
- Success: `/admin/subscription/success`
- Cancel: `/admin/subscription/cancel`

---

## 🖼️ Image Upload
```typescript
const token = localStorage.getItem('auth_token');
const formData = new FormData();
formData.append('file', imageFile);

const response = await fetch('http://localhost:8000/api/v1/admin/images/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const { cdn_url } = await response.json();
// Use cdn_url to display the image
```

---

## ⚠️ Error Handling

All errors return consistent JSON format:
```typescript
{
  "error": "Human-readable error message",
  "type": "ErrorType"  // Optional
}
```

### Status Codes

- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized (invalid/missing token)
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Server Error

### Example Error Handling
```typescript
try {
  const response = await fetch(url, options);
  
  if (!response.ok) {
    const error = await response.json();
    
    if (response.status === 401) {
      localStorage.removeItem('auth_token');
      router.push('/login');
    } else {
      alert(error.error || 'An error occurred');
    }
    return;
  }
  
  const data = await response.json();
  // Success!
  
} catch (error) {
  console.error('Network error:', error);
}
```

---

## 🎨 Frontend Pages to Build

### Public Pages

1. **Homepage** - `/`
   - Directory of institutions
   - State filter
   - Search bar

2. **Institution Profile** - `/institution/:ipeds_id`
   - Display institution data
   - Show images from CDN
   - Stats, tuition, etc.

3. **Scholarships** - `/scholarships`
   - List of scholarships
   - Filter by type, amount

4. **Pricing** - `/pricing`
   - Show $39.99/month plan
   - 30-day free trial
   - Feature comparison

### Admin Pages

5. **Admin Login** - `/admin/login`
6. **Admin Dashboard** - `/admin/dashboard`
7. **Profile Editor** - `/admin/profile`
8. **Subscription** - `/admin/subscription`

---

## 🧪 Testing Your Frontend

### Use These Test Scenarios:

1. **Browse Institutions**
   - Visit homepage
   - Filter by state (NH has 12)
   - Click on an institution
   - View profile page

2. **Admin Flow**
   - Login with test credentials
   - View dashboard
   - Edit display settings
   - Upload an image
   - Create checkout session

3. **Error Cases**
   - Access admin without login → Should redirect
   - Invalid credentials → Should show error
   - Non-existent institution → Should show 404

---

## 🔒 Security Checklist

- ✅ Store JWT tokens in localStorage
- ✅ Send `Authorization: Bearer {token}` header
- ✅ Clear token on logout
- ✅ Redirect to login if 401
- ✅ Never expose token in URLs
- ✅ Use HTTPS in production

---

## 🚀 Deployment

### Environment Variables
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # or production URL
```

### Production API

When deployed, the API will be at production URL (provided by backend team).

---

## 📞 Support & Questions

### Need Help?

1. Check **Swagger docs:** http://localhost:8000/docs
2. Look at **example requests:** `api_docs/example_requests.json`
3. Review **TypeScript types:** `api_docs/types.ts`
4. Contact backend developer

---

## ✅ Frontend Developer Checklist

Before you start:
- [ ] Backend running at http://localhost:8000
- [ ] Can access http://localhost:8000/docs
- [ ] Have test credentials
- [ ] Reviewed `api_docs/types.ts`
- [ ] Read this document

While building:
- [ ] Test authentication flow
- [ ] Implement error handling
- [ ] Test subscription flow
- [ ] Test image upload
- [ ] Handle loading states
- [ ] Handle error states

Before deployment:
- [ ] Update API_URL to production
- [ ] Test with production API
- [ ] Verify Stripe works
- [ ] Test on mobile

---

**Ready to build! The backend is 100% complete and tested.** 🚀

**Questions? Contact the backend developer.**

---

**Last Updated:** November 15, 2025  
**Backend Version:** 1.0.0  
**Test Status:** ✅ 18/18 Passing
