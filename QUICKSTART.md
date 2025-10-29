# KIVerdienst v2 - Quick Start Guide

## 📦 What You Have

A complete, production-ready autonomous content generation system with:
- ✅ Flask Backend API (Python)
- ✅ Flask Frontend Web UI
- ✅ PostgreSQL Database
- ✅ Docker Configuration
- ✅ AI Content Agents
- ✅ Complete CRUD Operations
- ✅ Setup Wizard
- ✅ Debug Dashboard

## 🚀 Getting Started (3 Steps)

### Step 1: Extract and Configure

```bash
# Extract the ZIP file
unzip kiverdienst_v2_complete.zip
cd kiverdienst_v2_complete

# Create environment file
cp .env.example .env

# Optional: Edit .env to customize ports, passwords, etc.
nano .env
```

### Step 2: Start the System

```bash
# Start all services with Docker
docker-compose up -d

# Wait 10-15 seconds for services to start, then initialize database
docker-compose exec backend python /workspace/init_db.py
```

### Step 3: Access the Application

Open your browser to:
- **Frontend**: http://localhost:5000
- **Backend API**: http://localhost:8000/api/health

Follow the setup wizard to complete configuration!

## 📁 Project Structure

```
kiverdienst_v2_complete/
├── backend/                 # Backend API (Port 8000)
│   ├── app.py              # Main Flask app
│   ├── database.py         # DB connection
│   ├── models.py           # Database models
│   ├── routes/             # API endpoints
│   │   ├── setup.py        # Setup wizard
│   │   ├── brands.py       # Brand management
│   │   ├── videos.py       # Video management
│   │   ├── characters.py   # Character management
│   │   └── system.py       # System stats
│   ├── agents/             # AI agents
│   │   ├── content_agent.py   # Content ideas
│   │   ├── script_agent.py    # Script writing
│   │   └── strategy_agent.py  # Strategy planning
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/               # Frontend UI (Port 5000)
│   ├── app.py             # Frontend Flask app
│   ├── templates/         # HTML templates
│   │   ├── base.html      # Base layout with sidebar
│   │   ├── dashboard.html # Main dashboard
│   │   ├── brands.html    # Brand management
│   │   ├── videos.html    # Video library
│   │   ├── characters.html # Character management
│   │   ├── content.html   # Content strategy
│   │   ├── debug.html     # Debug & monitoring
│   │   └── setup/         # Setup wizard pages
│   ├── static/
│   │   ├── css/main.css   # Complete styling
│   │   └── js/app.js      # Frontend JavaScript
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml      # Docker orchestration
├── .env.example           # Environment template
├── init_db.py            # Database initialization
└── README.md             # Full documentation
```

## 🔧 Common Commands

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Stop and remove all data (fresh start)
docker-compose down -v

# Access database directly
docker-compose exec postgres psql -U kiverdienst -d kiverdienst_v2
```

## 📊 Features Overview

### 1. Brand Management
- Create multiple brands/channels
- Define niche and target audience
- Set content strategy
- Multi-platform support (TikTok, Instagram, YouTube)

### 2. Video Management
- Create and organize videos
- AI script generation ready
- Track status (draft → posted)
- Engagement metrics

### 3. Character Management
- AI characters with personalities
- Voice configuration
- Speaking style customization

### 4. Content Strategy
- Content calendar generation
- Posting time optimization
- AI content ideas
- Performance analytics

### 5. Debug Dashboard
- System health monitoring
- Database statistics
- API endpoint testing
- Live logs

## 🌐 API Endpoints

All endpoints return JSON: `{"success": true/false, "data": {...}, "error": "..."}`

### System
- `GET /api/health` - Health check
- `GET /api/system/stats` - System statistics

### Brands
- `GET /api/brands` - List brands
- `POST /api/brands` - Create brand
- `PUT /api/brands/<id>` - Update brand
- `DELETE /api/brands/<id>` - Delete brand

### Videos
- `GET /api/videos?brand_id=1&status=draft` - List videos (with filters)
- `POST /api/videos` - Create video
- `PUT /api/videos/<id>` - Update video

### Characters
- `GET /api/characters?brand_id=1` - List characters
- `POST /api/characters` - Create character
- `PUT /api/characters/<id>` - Update character

## 🔐 Default Credentials

Database:
- User: `kiverdienst`
- Password: `secure123kiverdienst`
- Database: `kiverdienst_v2`

**Change these in production!**

## ⚡ Next Steps

1. ✅ Start the system (done above)
2. 🌐 Complete setup wizard at http://localhost:5000
3. 🏢 Create your first brand
4. 🎭 Add characters with personalities
5. 🎬 Start generating video content
6. 📊 Monitor performance in dashboard

## 🐛 Troubleshooting

**Port already in use:**
```bash
# Edit .env and change ports
FRONTEND_PORT=5001
BACKEND_PORT=8001
```

**Database connection failed:**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres
```

**Reset everything:**
```bash
docker-compose down -v
docker-compose up -d
docker-compose exec backend python /workspace/init_db.py
```

## 📚 Full Documentation

See `README.md` for complete documentation including:
- Detailed architecture
- Development guide
- Environment variables
- Database schema
- Roadmap

## 🎯 Production Deployment

Before deploying to production:

1. Change all secrets in `.env`:
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `POSTGRES_PASSWORD`

2. Set `DEBUG=false`

3. Use proper reverse proxy (nginx)

4. Enable HTTPS

5. Set up backups for PostgreSQL

6. Configure proper logging

---

**Ready to automate your content creation! 🚀**
