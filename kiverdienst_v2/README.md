# 🎬 KIVerdienst v2 - Autonomous TikTok Content Generation System

**Production-ready system for automated TikTok content creation with one-command installation and web-based setup wizard.**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [First-Time Setup](#first-time-setup)
- [Usage Guide](#usage-guide)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

---

## 🎯 Overview

KIVerdienst v2 is a complete, autonomous system for generating and managing TikTok content. It combines AI-powered content creation with automated posting, performance analytics, and brand management - all through an intuitive web interface.

### What Makes It Special?

- **🚀 One-Command Installation** - Get up and running in minutes
- **🎨 Web-Based Setup Wizard** - No technical knowledge required
- **📊 Real-Time Dashboard** - Monitor everything in one place
- **🤖 Fully Automated** - From content creation to posting
- **🔧 Debug-Friendly** - Built-in tools for troubleshooting

---

## ✨ Features

### Core Features
- ✅ **Automated Video Generation** - AI-powered content creation
- ✅ **Multi-Brand Management** - Handle multiple brands/channels
- ✅ **Performance Analytics** - Track views, engagement, and growth
- ✅ **Posting Scheduler** - Automatic content distribution
- ✅ **Character System** - Define avatars and personalities
- ✅ **Script Management** - Create and approve video scripts

### Technical Features
- ✅ **Docker-Based** - Fully containerized deployment
- ✅ **PostgreSQL Database** - Robust data storage
- ✅ **FastAPI Backend** - High-performance Python API
- ✅ **Flask Frontend** - Modern, responsive web UI
- ✅ **Real-Time Logs** - Live system monitoring
- ✅ **Health Checks** - Automatic service monitoring
- ✅ **Debug Tools** - Built-in troubleshooting utilities

---

## 🚀 Quick Start

Get KIVerdienst v2 running in just 3 steps:

### Step 1: Clone or Download
```bash
cd /opt
sudo git clone <repository-url> kiverdienst_v2
cd kiverdienst_v2
```

### Step 2: Run Installer
```bash
sudo ./install.sh
```

### Step 3: Open Web Interface
```
http://YOUR-SERVER-IP:5000/setup
```

That's it! The installer will:
- ✅ Check and install Docker if needed
- ✅ Set up all services
- ✅ Initialize the database
- ✅ Start all containers
- ✅ Open your browser to the setup wizard

**Total Installation Time: 2-5 minutes**

---

## 💻 System Requirements

### Minimum Requirements
- **OS:** Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **CPU:** 2 cores
- **RAM:** 4 GB
- **Disk:** 10 GB free space
- **Network:** Internet connection for API access

### Recommended
- **CPU:** 4+ cores
- **RAM:** 8+ GB
- **Disk:** 50+ GB SSD
- **Network:** 100 Mbps+

### Required Software
- Docker 20.10+
- Docker Compose 2.0+
- Git
- OpenSSL (for key generation)

> **Note:** The installer will automatically install missing dependencies.

---

## 📦 Installation

### Automated Installation (Recommended)

1. **Prepare the System**
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade -y
   
   # Install git if not present
   sudo apt install -y git
   ```

2. **Download KIVerdienst v2**
   ```bash
   cd /opt
   sudo git clone <repository-url> kiverdienst_v2
   cd kiverdienst_v2
   ```

3. **Run the Installer**
   ```bash
   sudo ./install.sh
   ```

   The installer will:
   - Check system requirements
   - Install Docker and Docker Compose (if missing)
   - Generate secure passwords
   - Create environment configuration
   - Start all services
   - Initialize the database
   - Display access URLs

4. **Save Your Credentials**
   
   The installer will display generated passwords. **Save these immediately!**
   
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   PostgreSQL Password: [generated]
   Secret Key: [generated]
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

### Manual Installation

If you prefer manual installation:

1. **Install Dependencies**
   ```bash
   ./scripts/check_dependencies.sh
   ```

2. **Configure Environment**
   ```bash
   cp .env.template .env
   nano .env  # Edit with your values
   ```

3. **Start Services**
   ```bash
   docker compose up -d
   ```

4. **Initialize Database**
   ```bash
   docker compose exec backend python scripts/init_db.py
   ```

---

## 🎨 First-Time Setup

After installation, open your browser to start the setup wizard:

```
http://YOUR-SERVER-IP:5000/setup
```

### Setup Wizard Steps

#### Step 1: Welcome
- Introduction to KIVerdienst v2
- Overview of features

#### Step 2: System Check
- Database connection test
- Docker containers status
- Disk space verification

#### Step 3: Configuration
- Enter administrator email
- Add API keys (optional):
  - OpenAI API Key
  - ElevenLabs API Key
  - Replicate API Token

> **Tip:** You can skip API keys during setup and add them later through the dashboard.

#### Step 4: Complete
- Review configuration
- Access the main dashboard

---

## 📖 Usage Guide

### Dashboard Overview

The dashboard provides:
- **System Status** - Health of all services
- **Brand Statistics** - Active brands and content
- **Video Performance** - Total views, engagement
- **Quick Actions** - Common tasks

### Creating Your First Brand

1. **Navigate to Brands**
   ```
   Dashboard → Brands → Create New Brand
   ```

2. **Fill in Details**
   - **Name:** Your brand name
   - **Niche:** Content category (Tech, Fitness, Cooking, etc.)
   - **Tonality:** Voice and style
   - **Target Audience:** Who you're creating for
   - **Social Accounts:** TikTok, Instagram, YouTube handles

3. **Save and Activate**

### Managing Brands

- **View All Brands** - See all your content brands
- **Edit Brand** - Update settings and accounts
- **Pause/Activate** - Control content generation
- **Delete Brand** - Remove with all related data

### Viewing Logs

Real-time system logs are available at:
```
http://YOUR-SERVER-IP:5000/logs
```

Features:
- Filter by log level (Info, Warning, Error)
- Filter by component
- Auto-refresh every 5 seconds
- Search logs

### Debug Tools

Access debug tools at:
```
http://YOUR-SERVER-IP:5000/debug
```

Available tools:
- Service health status
- Docker container status
- Port checker
- Database connection test
- API tests
- Service restart buttons

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────┐
│                    Nginx (Port 80)                  │
│                  Reverse Proxy                      │
└───────────┬─────────────┬───────────────────────────┘
            │             │
    ┌───────▼──────┐ ┌───▼──────────┐
    │   Frontend   │ │   Backend    │
    │  (Flask)     │ │   (FastAPI)  │
    │  Port 5000   │ │   Port 8000  │
    └──────────────┘ └───────┬──────┘
                             │
                      ┌──────▼──────┐
                      │  PostgreSQL │
                      │  Port 5432  │
                      └─────────────┘
```

### Technology Stack

**Backend:**
- FastAPI 0.109.0
- SQLAlchemy 2.0
- PostgreSQL 16
- Uvicorn

**Frontend:**
- Flask 3.0
- Vanilla JavaScript
- Custom CSS (utility-first)
- No build step required

**Infrastructure:**
- Docker & Docker Compose
- Nginx (optional, for production)
- PostgreSQL with connection pooling

### Database Schema

**Main Tables:**
- `brands` - Brand/channel information
- `characters` - Avatar definitions
- `video_scripts` - Generated scripts
- `videos` - Produced videos
- `performance_analytics` - Metrics and stats
- `posting_schedule` - Posting times
- `system_logs` - System events
- `system_config` - Configuration
- `products` - Affiliate products

**Views:**
- `brand_performance` - Aggregated brand stats
- `recent_activity` - Latest system activity

---

## 📚 API Documentation

### Interactive Documentation

Access the interactive API documentation:
- **Swagger UI:** `http://YOUR-SERVER-IP:8000/docs`
- **ReDoc:** `http://YOUR-SERVER-IP:8000/redoc`

### Main Endpoints

#### Health Check
```bash
GET /api/health
```

#### Setup
```bash
GET  /api/setup/status      # Check setup status
POST /api/setup/init        # Initialize system
POST /api/setup/complete    # Mark setup complete
```

#### Brands
```bash
GET    /api/brands              # List all brands
POST   /api/brands              # Create brand
GET    /api/brands/{id}         # Get brand
PUT    /api/brands/{id}         # Update brand
DELETE /api/brands/{id}         # Delete brand
PATCH  /api/brands/{id}/status  # Toggle status
```

#### System
```bash
GET  /api/system/health    # System health
GET  /api/system/stats     # Statistics
GET  /api/system/docker    # Docker status
POST /api/system/restart/{service}  # Restart service
```

#### Debug
```bash
GET    /api/debug/logs        # Get logs
DELETE /api/debug/logs        # Clear logs
GET    /api/debug/database    # Test database
POST   /api/debug/test-api    # Test APIs
GET    /api/debug/ports       # Check ports
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Installation Fails

**Problem:** Installer stops with errors

**Solutions:**
```bash
# Check system requirements
./scripts/check_dependencies.sh

# Check Docker status
sudo systemctl status docker

# View installer logs
sudo journalctl -u docker -n 50
```

#### 2. Can't Access Web Interface

**Problem:** Browser can't connect to port 5000

**Solutions:**
```bash
# Check if services are running
docker compose ps

# Check frontend logs
docker compose logs frontend

# Check firewall
sudo ufw allow 5000
```

#### 3. Database Connection Errors

**Problem:** "Database connection failed"

**Solutions:**
```bash
# Check PostgreSQL status
docker compose logs postgres

# Verify database is ready
docker compose exec postgres pg_isready -U kiverdienst

# Restart database
docker compose restart postgres
```

#### 4. Docker Issues

**Problem:** Containers not starting

**Solutions:**
```bash
# Check Docker daemon
sudo systemctl restart docker

# Rebuild containers
docker compose down
docker compose build --no-cache
docker compose up -d

# Check for port conflicts
./scripts/check_dependencies.sh
```

### Health Check Script

Run the health check to diagnose issues:
```bash
./scripts/health_check.sh
```

This will check:
- ✅ Docker daemon status
- ✅ Container status
- ✅ Database connectivity
- ✅ Web services
- ✅ Resource usage
- ✅ Recent errors

### Getting Help

1. **Check Logs**
   ```bash
   # All services
   docker compose logs -f
   
   # Specific service
   docker compose logs -f backend
   docker compose logs -f frontend
   docker compose logs -f postgres
   ```

2. **Check Service Status**
   ```bash
   docker compose ps
   ```

3. **Restart Services**
   ```bash
   docker compose restart
   ```

4. **Full Reset** (⚠️ Deletes all data)
   ```bash
   docker compose down -v
   ./install.sh --reset
   ```

---

## 🛠️ Development

### Running in Development Mode

1. **Set Debug Mode**
   ```bash
   # Edit .env
   DEBUG=true
   LOG_LEVEL=DEBUG
   ```

2. **Start Services**
   ```bash
   docker compose up
   ```

3. **Access Services**
   - Frontend: http://localhost:5000
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Project Structure

```
kiverdienst_v2/
├── install.sh              # One-command installer
├── docker-compose.yml      # Docker services
├── .env.template           # Environment template
├── README.md               # This file
│
├── backend/                # FastAPI Backend
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   └── routes/
│       ├── setup.py
│       ├── brands.py
│       ├── system.py
│       └── debug.py
│
├── frontend/               # Flask Frontend
│   ├── app.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│
├── sql/
│   ├── schema.sql
│   └── seed.sql
│
└── scripts/
    ├── check_dependencies.sh
    ├── init_db.py
    └── health_check.sh
```

### Making Changes

1. **Backend Changes**
   - Edit files in `backend/`
   - FastAPI auto-reloads in debug mode
   - Test at http://localhost:8000/docs

2. **Frontend Changes**
   - Edit templates in `frontend/templates/`
   - Edit CSS in `frontend/static/css/`
   - Edit JS in `frontend/static/js/`
   - Refresh browser to see changes

3. **Database Changes**
   - Edit `sql/schema.sql`
   - Reset database:
     ```bash
     docker compose exec backend python scripts/init_db.py --reset
     ```

---

## 🚦 Service Management

### Starting Services
```bash
# Start all services
docker compose up -d

# Start specific service
docker compose up -d backend
```

### Stopping Services
```bash
# Stop all services
docker compose stop

# Stop specific service
docker compose stop backend
```

### Restarting Services
```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend
```

### Viewing Logs
```bash
# Follow all logs
docker compose logs -f

# Last 100 lines
docker compose logs --tail=100 backend

# Specific service
docker compose logs -f frontend
```

### Updating Services
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## 📊 Monitoring & Maintenance

### Regular Maintenance Tasks

**Daily:**
- Check system health via dashboard
- Review error logs
- Monitor disk space

**Weekly:**
- Review performance analytics
- Check database size
- Update system packages

**Monthly:**
- Backup database
- Review API usage
- Clean old logs

### Backup & Restore

**Backup Database:**
```bash
docker compose exec -T postgres pg_dump -U kiverdienst kiverdienst_v2 > backup_$(date +%Y%m%d).sql
```

**Restore Database:**
```bash
docker compose exec -T postgres psql -U kiverdienst kiverdienst_v2 < backup_20240101.sql
```

**Backup Volumes:**
```bash
docker run --rm -v kiverdienst_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_data.tar.gz -C /data .
```

---

## 🔒 Security

### Best Practices

1. **Change Default Passwords**
   - Use strong, unique passwords
   - Store securely (password manager)

2. **Enable Firewall**
   ```bash
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS
   sudo ufw allow 5000  # Frontend (if not using nginx)
   sudo ufw enable
   ```

3. **Keep System Updated**
   ```bash
   sudo apt update && sudo apt upgrade -y
   docker compose pull
   docker compose up -d
   ```

4. **Use HTTPS**
   - Configure SSL certificates
   - Use Let's Encrypt for free certificates
   - Enable HTTPS in nginx configuration

5. **Regular Backups**
   - Automated daily backups
   - Store backups off-site
   - Test restore procedures

---

## 📞 Support

### Resources

- **Documentation:** This README
- **API Docs:** http://YOUR-IP:8000/docs
- **Debug Tools:** http://YOUR-IP:5000/debug
- **Logs Viewer:** http://YOUR-IP:5000/logs

### Useful Commands

```bash
# Check system health
./scripts/health_check.sh

# Check dependencies
./scripts/check_dependencies.sh

# View all containers
docker compose ps

# View logs
docker compose logs -f

# Restart everything
docker compose restart

# Full reset
docker compose down -v && ./install.sh
```

---

## 📝 License

[Your License Here]

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Flask](https://flask.palletsprojects.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)

---

## 📈 Changelog

### Version 2.0.0 (Current)
- ✅ Complete system rewrite
- ✅ One-command installation
- ✅ Web-based setup wizard
- ✅ Modern UI with real-time updates
- ✅ Comprehensive debug tools
- ✅ Docker-based deployment
- ✅ Production-ready architecture

---

**KIVerdienst v2** - Built with ❤️ for content creators

Ready to start? Run `./install.sh` and visit http://YOUR-IP:5000/setup 🚀
