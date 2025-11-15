# CampusConnect Deployment Guide

## 🚀 Quick Start (Production)

### Prerequisites
- Docker & Docker Compose installed
- Domain name configured (campusconnect.com)
- SSL certificates (Let's Encrypt)

### Deploy to Production

1. **Clone repository:**
```bash
git clone <your-repo-url>
cd campusconnect-backend
```

2. **Configure environment:**
```bash
cp .env.production.example .env.production
# Edit .env.production with your production values
```

3. **Deploy:**
```bash
./deploy.sh
```

4. **Verify:**
```bash
curl https://campusconnect.com/health
```

---

## 🛠️ Local Development

### Setup

1. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your development values
```

4. **Run database migrations:**
```bash
alembic upgrade head
```

5. **Start server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access API:**
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📊 Database Management

### Run Migrations
```bash
# Development
alembic upgrade head

# Production (Docker)
docker-compose run --rm api alembic upgrade head
```

### Create New Migration
```bash
alembic revision --autogenerate -m "description"
```

### Rollback
```bash
alembic downgrade -1  # Rollback one migration
```

### Backup Database
```bash
# Development
pg_dump campusconnect_db > backup_$(date +%Y%m%d).sql

# Production (Docker)
docker-compose exec db pg_dump -U postgres campusconnect_db > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
# Development
psql campusconnect_db < backup_20251115.sql

# Production (Docker)
docker-compose exec -T db psql -U postgres campusconnect_db < backup_20251115.sql
```

---

## 🔒 SSL/HTTPS Setup

### Using Let's Encrypt (Certbot)

1. **Install Certbot:**
```bash
sudo apt-get install certbot python3-certbot-nginx
```

2. **Get certificate:**
```bash
sudo certbot --nginx -d campusconnect.com -d www.campusconnect.com
```

3. **Auto-renewal:**
```bash
sudo certbot renew --dry-run
```

4. **Update nginx.conf:**
- Uncomment the HTTPS server block
- Update certificate paths

---

## 📝 Logs

### View Logs

**Development:**
```bash
tail -f logs/campusconnect_$(date +%Y%m%d).log
tail -f logs/errors_$(date +%Y%m%d).log
```

**Production (Docker):**
```bash
docker-compose logs -f api
docker-compose logs -f db
docker-compose logs -f nginx
```

### Log Rotation

Logs rotate daily automatically. Old logs are kept for 30 days.

---

## 🧪 Testing

### Test Admin Flow
```bash
# Register
curl -X POST http://localhost:8000/api/v1/admin/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","entity_type":"institution","entity_id":1}'

# Login
curl -X POST http://localhost:8000/api/v1/admin/auth/login \
  -F "username=test@test.com" \
  -F "password=test123"
```

### Test Stripe Webhooks (Development)
```bash
stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe
```

---

## 🔧 Troubleshooting

### API won't start
```bash
# Check logs
docker-compose logs api

# Check database connection
docker-compose exec api python -c "from app.core.database import engine; print('DB OK')"
```

### Database connection issues
```bash
# Restart database
docker-compose restart db

# Check if database is running
docker-compose exec db psql -U postgres -c "SELECT 1"
```

### Rate limiting too strict
Edit `app/core/rate_limit.py` and adjust limits

---

## 📈 Monitoring

### Health Check
```bash
curl https://campusconnect.com/health
```

### Database Size
```bash
docker-compose exec db psql -U postgres -d campusconnect_db -c "
  SELECT pg_size_pretty(pg_database_size('campusconnect_db'));"
```

### API Performance
Check logs for request timing (shown in milliseconds)

---

## 🔄 Updates

### Deploy New Version
```bash
git pull origin main
./deploy.sh
```

### Rollback
```bash
git checkout previous-version-tag
./deploy.sh
```

---

## 💾 Backup Strategy

### Automated Daily Backups

Create a cron job:
```bash
0 2 * * * cd /path/to/campusconnect && docker-compose exec -T db pg_dump -U postgres campusconnect_db | gzip > backups/db_$(date +\%Y\%m\%d).sql.gz
```

### Backup to DigitalOcean Spaces
```bash
aws s3 cp backup.sql.gz s3://your-backup-bucket/ --endpoint-url=https://nyc3.digitaloceanspaces.com
```

---

## 🆘 Support

For issues, check:
1. Logs (`logs/` directory)
2. Database connection
3. Environment variables
4. Docker container status

