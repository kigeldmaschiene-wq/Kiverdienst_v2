# KIVerdienst v2

Autonomous multi-brand AI content generation system for TikTok, Instagram, and YouTube.

## 🎯 Overview

KIVerdienst v2 is a complete content automation platform that helps you:
- Manage multiple content brands/channels
- Generate AI-powered video scripts and content ideas
- Create and manage AI characters with unique personalities
- Plan and optimize content strategy
- Track video performance and engagement

**Target:** 5,000-20,000€/month through automated content creation

## 🏗️ Architecture

```
KIVerdienst v2/
├── backend/          # Flask API (Port 8000)
│   ├── app.py       # Main Flask app
│   ├── database.py  # Database connection
│   ├── models.py    # SQLAlchemy models
│   ├── routes/      # API endpoints
│   └── agents/      # AI agents (content, script, strategy)
│
├── frontend/        # Flask Web UI (Port 5000)
│   ├── app.py      # Frontend Flask app
│   ├── templates/  # Jinja2 templates
│   └── static/     # CSS, JS, images
│
└── docker-compose.yml
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- 4GB+ RAM
- Port 5000, 8000, 5432 available

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd kiverdienst_v2
```

2. **Create environment file:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start the services:**
```bash
docker-compose up -d
```

4. **Initialize database:**
```bash
docker-compose exec backend python /workspace/init_db.py
```

5. **Access the application:**
- Frontend: http://localhost:5000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/health

### First Run Setup

1. Navigate to http://localhost:5000
2. Complete the setup wizard:
   - Database connection test
   - System initialization
   - Optional Ollama configuration
3. Create your first brand
4. Add characters and start generating content!

## 📋 Features

### Brand Management
- Create and manage multiple brands/channels
- Define niche, target audience, and content strategy
- Multi-platform support (TikTok, Instagram, YouTube)
- Performance tracking per brand

### Video Management
- Create and organize video content
- AI-powered script generation
- Hook optimization (first 3 seconds)
- Status tracking (draft → script ready → generated → posted)
- Engagement metrics (views, likes, comments)

### Character Management
- Create AI characters with unique personalities
- Voice configuration (ElevenLabs integration ready)
- Speaking style customization
- Character performance analytics

### Content Strategy
- Content calendar generation
- AI content idea generator
- Optimal posting time recommendations
- Platform-specific best practices
- Performance insights and recommendations

### Debug & Monitoring
- System health dashboard
- Database statistics
- API endpoint tester
- Real-time logs viewer
- Configuration management

## 🔧 API Endpoints

### System
- `GET /api/health` - Health check
- `GET /api/system/stats` - System statistics
- `GET /api/system/health` - Detailed health status

### Setup
- `GET /api/setup/status` - Setup completion status
- `POST /api/setup/init` - Initialize system
- `POST /api/setup/complete` - Mark setup complete

### Brands
- `GET /api/brands` - List all brands
- `POST /api/brands` - Create brand
- `GET /api/brands/<id>` - Get brand details
- `PUT /api/brands/<id>` - Update brand
- `DELETE /api/brands/<id>` - Delete brand
- `GET /api/brands/<id>/stats` - Brand statistics

### Videos
- `GET /api/videos` - List videos (with filters)
- `POST /api/videos` - Create video
- `GET /api/videos/<id>` - Get video details
- `PUT /api/videos/<id>` - Update video
- `DELETE /api/videos/<id>` - Delete video

### Characters
- `GET /api/characters` - List characters
- `POST /api/characters` - Create character
- `GET /api/characters/<id>` - Get character details
- `PUT /api/characters/<id>` - Update character
- `DELETE /api/characters/<id>` - Delete character

## 🗄️ Database Schema

### Tables

**brands**
- id, name, niche, target_audience
- content_strategy, platforms, posting_schedule
- active, created_at

**characters**
- id, brand_id, name, gender, voice_id
- personality, speaking_style
- active, created_at

**videos**
- id, brand_id, character_id
- title, script, hook, content_type
- status, platform, video_path
- posted, views, likes, comments
- metadata, created_at

**system_config**
- id, key, value, description
- updated_at, created_at

## 🛠️ Development

### Running Locally (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
export DATABASE_URL=postgresql://user:pass@localhost:5432/kiverdienst_v2
python app.py
```

**Frontend:**
```bash
cd frontend
pip install -r requirements.txt
export BACKEND_URL=http://localhost:8000
python app.py
```

### Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask secret key
- `BACKEND_URL` - Backend API URL (for frontend)
- `OLLAMA_URL` - Ollama LLM service URL
- `DEBUG` - Enable debug mode

## 📦 Tech Stack

**Backend:**
- Flask 3.0 - Web framework
- SQLAlchemy 2.0 - ORM
- PostgreSQL 16 - Database
- Requests - HTTP client

**Frontend:**
- Flask - Template rendering
- Jinja2 - Templates
- Modern CSS - Responsive design
- Vanilla JavaScript - Interactivity

**Infrastructure:**
- Docker & Docker Compose
- Gunicorn - WSGI server
- PostgreSQL - Data persistence

## 🔮 Roadmap

- [ ] Ollama LLM integration for content generation
- [ ] ElevenLabs voice synthesis
- [ ] Automated video generation
- [ ] TikTok/Instagram API integration
- [ ] Automated posting scheduler
- [ ] Analytics dashboard
- [ ] Multi-language support
- [ ] Export/Import functionality

## 🐛 Troubleshooting

### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker-compose ps

# View logs
docker-compose logs postgres

# Restart services
docker-compose restart
```

### Port Already in Use
```bash
# Change ports in .env
FRONTEND_PORT=5001
BACKEND_PORT=8001
POSTGRES_PORT=5433
```

### Reset Database
```bash
docker-compose down -v
docker-compose up -d
docker-compose exec backend python /workspace/init_db.py
```

## 📝 License

Proprietary - All rights reserved

## 🤝 Support

For issues and questions, check the Debug page at http://localhost:5000/debug

---

**Built with ❤️ for automated content creation**
