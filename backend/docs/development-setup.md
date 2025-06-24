# Cookify Development Setup Guide

## 🚀 **Quick Start for Development (2-Person Team)**

### **1. Create Environment File:**

```bash
# Create .env.development file
cp .env.example .env.development
```

### **2. Start Development Container:**

```bash
# With Live-Reload and Debug Mode
docker-compose -f docker-compose.dev.yml up -d

# Or with logs in foreground
docker-compose -f docker-compose.dev.yml up
```

### **3. Development URLs:**

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

---

## ⚙️ **Development-Specific Features:**

### **Relaxed Limits for Development:**

- **OCR Requests**: 20 instead of 5 per time window
- **File Size**: 10MB instead of 5MB
- **Processing Timeout**: Longer timeouts
- **CORS**: All local ports allowed

### **Auto-Reload Enabled:**

```yaml
command: [
    'uvicorn',
    'main:app',
    '--host',
    '0.0.0.0',
    '--port',
    '8000',
    '--reload', # 🔄 Auto-reload on code changes
    '--log-level',
    'debug',
  ]
```

### **Source Code Live-Mounting:**

```yaml
volumes:
  - .:/backend:rw # 📁 Live code changes
  - ./logs:/backend/logs:rw # 📋 Live logs
  - ./data:/backend/data:ro # 🧪 Test data
```

---

## 🛠️ **Practical Development Commands:**

### **Container Management:**

```bash
# Start
docker-compose -f docker-compose.dev.yml up -d

# Stop
docker-compose -f docker-compose.dev.yml down

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Login to container
docker exec -it cookify_api_dev bash
```

### **Code Testing:**

```bash
# Run security tests
./scripts/test-ocr-security.sh

# Test OCR with sample image
curl -X POST http://localhost:8000/api/ocr/extract-text \
     -F "image=@data/sample_receipt.png"
```

### **Development Debugging:**

```bash
# Show all container processes
docker exec cookify_api_dev ps aux

# Check Python packages
docker exec cookify_api_dev pip list

# Memory/CPU Usage
docker stats cookify_api_dev
```

---

## 📋 **Development Environment Variables (.env.development):**

```env
# === DEVELOPMENT SETTINGS ===
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# === SUPABASE (Shared Dev Instance) ===
SUPABASE_URL=your_dev_supabase_url
SUPABASE_KEY=your_dev_supabase_key

# === RELAXED SECURITY FOR DEV ===
SESSION_HTTPS_ONLY=false
REQUIRE_EMAIL_VERIFICATION=false

# === PERMISSIVE OCR SETTINGS ===
OCR_MAX_IMAGE_SIZE_BYTES=10485760  # 10MB
OCR_PROCESSING_TIMEOUT=60          # 60 seconds
RATE_LIMIT_OCR_EXTRACT_ATTEMPTS=20 # 20 requests
RATE_LIMIT_OCR_PROCESS_ATTEMPTS=15 # 15 requests

# === CORS (All local development ports) ===
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://127.0.0.1:3000","http://127.0.0.1:5173","http://localhost:8080"]

# === JWT (Use simple secrets for dev) ===
JWT_SECRET=dev_jwt_secret_minimum_32_characters
SESSION_SECRET_KEY=dev_session_secret_minimum_32_chars
```

---

## 🔄 **Team Development Workflow:**

### **Partner 1 - Backend Focus:**

```bash
# Develop backend
docker-compose -f docker-compose.dev.yml up -d
# Edit code in domains/
# Test with: ./scripts/test-ocr-security.sh
```

### **Partner 2 - Frontend/Integration:**

```bash
# Use same containers
docker-compose -f docker-compose.dev.yml up -d
# Develop frontend against http://localhost:8000
# API tests with: curl or Postman
```

### **Debug Together:**

```bash
# Both can follow logs live
docker-compose -f docker-compose.dev.yml logs -f

# Both can enter container
docker exec -it cookify_api_dev bash
```

---

## 🚨 **What NOT to use for Development:**

❌ **docker-compose.prod.yml** - Too restrictive for development
❌ **docker-compose.yml** - Standard, but not optimized for dev
❌ **./scripts/deploy-docker.sh** - Intended for production

---

## 💡 **Pro Tips for 2-Person Team:**

### **1. Shared Development Database:**

```yaml
# Optional: Add shared dev DB
postgres-dev:
  image: postgres:15-alpine
  environment:
    - POSTGRES_DB=cookify_dev
    - POSTGRES_USER=cookify
    - POSTGRES_PASSWORD=dev_password
  ports:
    - '5432:5432'
```

### **2. Live Code Sync:**

```bash
# Git-based sync
git pull origin develop    # Get changes from partner
# Container keeps running, code updates live
```

### **3. Parallel Development:**

```bash
# Partner 1: Backend APIs
vim domains/ocr/routes.py

# Partner 2: Tests & Integration
vim tests/ocr/test_security.py

# Both: Live-reload works automatically
```

---

## ✅ **Quick Checklist Development Setup:**

- [ ] `.env.development` created and configured
- [ ] `docker-compose -f docker-compose.dev.yml up -d` executed
- [ ] http://localhost:8000/docs accessible
- [ ] OCR test successful: `./scripts/test-ocr-security.sh`
- [ ] Live-reload working (change code → automatic reload)
- [ ] Logs visible: `docker-compose -f docker-compose.dev.yml logs -f`

**Perfect for 2-person development team! 🎯**
