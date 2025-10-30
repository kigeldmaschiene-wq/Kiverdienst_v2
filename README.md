# KIVerdienst v2 - Autonomous AI Content Generation System

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Complete multi-brand AI content generation system for TikTok, Instagram, and YouTube Shorts. Built with Flask, PostgreSQL, and Docker.

## 🎯 Features

- **Multi-Brand Management** - Manage multiple content brands simultaneously
- **AI Characters** - Create unique AI personalities for each brand
- **Content Strategy** - AI-powered content idea generation
- **Video Library** - Organize and track all generated videos
- **Debug Dashboard** - Advanced system monitoring and debugging
- **Setup Wizard** - Easy first-time configuration
- **RESTful API** - Complete backend API for integration

## 🏗️ Architecture

```
KIVerdienst v2
├── Backend (Flask API - Port 8000)
│   ├── Database Management (PostgreSQL)
│   ├── RESTful API Endpoints
│   └── AI Agents (Content, Script, Strategy)
├── Frontend (Flask Web UI - Port 5000)
│   ├── Dashboard
│   ├── Brand Management
│   ├── Video Library
│   └── Debug Interface
└── Database (PostgreSQL - Port 5432)
    └── Data Storage
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- 4GB RAM minimum
- 10GB free disk space

### Installation

1. **Clone the repository:**
```bash
git clone git@github.com:kigeldmaschiene-wq/Kiverdienst_v2.git
cd Kiverdienst_v2
```

2. **Create environment file:**
```bash
cp .env.example .env
```

3. **Edit `.env` and update your secrets:**
```bash
# Required: Change these!
SECRET_KEY=your-secret-key-here
POSTGRES_PASSWORD=your-secure-password
```

4. **Start the system:**
```bash
docker-compose up -d
```

5. **Access the application:**
- Frontend: http://localhost:5000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/

6. **Complete the setup wizard:**
- Navigate to http://localhost:5000
- Follow the setup wizard to configure your system

## 📊 System Components

### Backend API (Port 8000)

#### Core Endpoints

**System:**
- `GET /api/health` - Health check
- `GET /api/system/stats` - System statistics
- `GET /api/system/info` - System information

**Setup:**
- `GET /api/setup/status` - Check setup status
- `POST /api/setup/init` - Initialize system
- `POST /api/setup/complete` - Complete setup

**Brands:**
- `GET /api/brands` - List all brands
- `POST /api/brands` - Create brand
- `GET /api/brands/<id>` - Get brand details
- `PUT /api/brands/<id>` - Update brand
- `DELETE /api/brands/<id>` - Delete brand

**Videos:**
- `GET /api/videos` - List videos (filterable)
- `POST /api/videos` - Create video
- `GET /api/videos/<id>` - Get video details
- `PUT /api/videos/<id>` - Update video
- `DELETE /api/videos/<id>` - Delete video

**Characters:**
- `GET /api/characters` - List characters
- `POST /api/characters` - Create character
- `GET /api/characters/<id>` - Get character details
- `PUT /api/characters/<id>` - Update character
- `DELETE /api/characters/<id>` - Delete character

**Content:**
- `GET /api/content/ideas` - List content ideas
- `POST /api/content/ideas` - Create content idea
- `PUT /api/content/ideas/<id>` - Update idea
- `POST /api/content/generate` - Generate ideas with AI

### Frontend (Port 5000)

- **Dashboard** - System overview and statistics
- **Brands** - Manage content brands
- **Characters** - Manage AI characters
- **Videos** - Video library and management
- **Content** - Content strategy and ideas
- **Debug** - System monitoring and debugging

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Rebuild after code changes
docker-compose up -d --build

# Reset database (WARNING: Deletes all data!)
docker-compose down -v
docker-compose up -d
```

## 🔧 Development

### Project Structure

```
kiverdienst_v2/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── database.py         # Database connection
│   ├── models.py           # SQLAlchemy models
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile
│   ├── routes/            # API route handlers
│   │   ├── setup.py
│   │   ├── brands.py
│   │   ├── videos.py
│   │   ├── characters.py
│   │   ├── system.py
│   │   └── content.py
│   └── agents/            # AI agents
│       ├── content_agent.py
│       ├── script_agent.py
│       └── strategy_agent.py
├── frontend/
│   ├── app.py              # Frontend Flask app
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── templates/          # HTML templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── brands.html
│   │   ├── videos.html
│   │   ├── characters.html
│   │   ├── content.html
│   │   ├── debug.html
│   │   └── setup/
│   └── static/            # CSS, JS, images
│       ├── css/main.css
│       └── js/app.js
├── docker-compose.yml
├── .env.example
└── README.md
```

### Database Schema

**Tables:**
- `system_config` - System configuration
- `brands` - Content brands
- `characters` - AI characters
- `videos` - Generated videos
- `content_ideas` - Content ideas

### Running Locally (Development)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://kiverdienst:secure123kiverdienst@localhost:5432/kiverdienst_v2
python app.py
```

**Frontend:**
```bash
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export BACKEND_URL=http://localhost:8000
python app.py
```

## 🧪 Testing

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# Get system stats
curl http://localhost:8000/api/system/stats

# List brands
curl http://localhost:8000/api/brands

# Create a brand
curl -X POST http://localhost:8000/api/brands \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Brand","niche":"Tech","active":true}'
```

### Access Debug Interface

Navigate to http://localhost:5000/debug for:
- System health monitoring
- API endpoint testing
- Live logs
- Database connection status
- Environment information

## 📈 Monitoring

### Health Checks

**Backend:**
```bash
curl http://localhost:8000/api/health
```

**Database:**
```bash
docker exec kiverdienst_v2_postgres pg_isready -U kiverdienst
```

### Logs

```bash
# All logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# Database only
docker-compose logs -f postgres
```

## 🔒 Security

- Change default passwords in `.env`
- Use strong SECRET_KEY values
- Enable HTTPS in production
- Restrict database access
- Keep dependencies updated

## 🚨 Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Test connection
docker exec kiverdienst_v2_postgres psql -U kiverdienst -d kiverdienst_v2 -c "SELECT 1"
```

### Backend Not Starting

```bash
# Check backend logs
docker-compose logs backend

# Rebuild backend
docker-compose up -d --build backend
```

### Frontend Not Loading

```bash
# Check frontend logs
docker-compose logs frontend

# Verify backend is accessible
curl http://localhost:8000/api/health
```

### Reset Everything

```bash
# WARNING: This deletes all data!
docker-compose down -v
docker-compose up -d --build
```

## 📝 Configuration

### Environment Variables

See `.env.example` for all available configuration options.

**Required:**
- `POSTGRES_USER` - Database username
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DB` - Database name
- `SECRET_KEY` - Flask secret key

**Optional:**
- `DEBUG` - Enable debug mode (default: false)
- `LOG_LEVEL` - Logging level (default: INFO)
- `OLLAMA_URL` - Ollama API URL for AI features
- `ELEVENLABS_API_KEY` - For voice generation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

For issues and questions:
- Create an issue on GitHub
- Check existing issues for solutions
- Review the debug dashboard at http://localhost:5000/debug

## 🎯 Roadmap

- [ ] AI-powered video generation
- [ ] Automated posting to social media
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Voice synthesis integration
- [ ] Video editing automation
- [ ] Trend analysis
- [ ] Content calendar
- [ ] Performance optimization
- [ ] Mobile app

## 📊 System Requirements

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 10GB storage
- Docker 20.10+

**Recommended:**
- 4+ CPU cores
- 8GB+ RAM
- 50GB+ storage
- SSD storage

## 🌟 Features in Detail

### Brand Management
- Create unlimited brands
- Define niche and target audience
- Set content strategy
- Track performance per brand

### Character Management
- Create AI personalities
- Assign characters to brands
- Configure voice settings
- Define character traits

### Video Library
- Organize all videos
- Filter by brand, status, platform
- Track views and engagement
- Manage video metadata

### Content Strategy
- Generate content ideas
- Track trending topics
- Organize by category
- Mark ideas as used/unused

### Debug Dashboard
- Real-time system health
- API endpoint testing
- Live log viewing
- Database connection status
- Environment information

---

**Built with ❤️ for content creators**

Version: 2.0.0 | Last Updated: 2025-10-30
