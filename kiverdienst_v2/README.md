# KIVerdienst v2 - Docker Setup

A complete, production-ready Docker setup for KIVerdienst v2 with PostgreSQL, Ollama LLM, FastAPI backend, and Nginx reverse proxy.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Service Management](#service-management)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)
- [Backup & Recovery](#backup--recovery)
- [Performance Tuning](#performance-tuning)

## ✨ Features

- **PostgreSQL 16** - Robust relational database with advanced features
- **Ollama** - Local LLM inference with llama3.1:70b and llama3.1:8b models
- **FastAPI** - High-performance Python backend
- **Nginx** - Reverse proxy with load balancing and SSL support
- **WebUI** - Modern frontend interface
- **Health Checks** - Automatic service health monitoring
- **Persistent Volumes** - Data persistence across container restarts
- **Logging** - Centralized logging with rotation
- **Security** - Secure defaults and CORS configuration

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Nginx (Port 80)                     │
│                   Reverse Proxy                         │
└─────────┬─────────────┬─────────────┬──────────────────┘
          │             │             │
          │             │             │
    ┌─────▼─────┐ ┌────▼─────┐ ┌────▼─────┐
    │  WebUI    │ │ FastAPI  │ │  Ollama  │
    │  (3000)   │ │  (8000)  │ │ (11434)  │
    └───────────┘ └─────┬────┘ └──────────┘
                        │
                  ┌─────▼─────┐
                  │ PostgreSQL│
                  │  (5432)   │
                  └───────────┘
```

## 📦 Prerequisites

### Required Software

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Git**
- **OpenSSL** (for generating secrets)

### Hardware Requirements

**Minimum:**
- 8 GB RAM
- 4 CPU cores
- 50 GB disk space

**Recommended (for llama3.1:70b):**
- 64 GB RAM
- 16 CPU cores
- 500 GB disk space
- NVIDIA GPU with 48GB+ VRAM (for optimal performance)

### Check Versions

```bash
docker --version
docker-compose --version
git --version
```

## 🚀 Quick Start

### 1. Clone or Copy Files

```bash
# If in a git repository
git clone <repository-url>
cd kiverdienst_v2

# Or copy all files to /opt/kiverdienst_v2/
sudo mkdir -p /opt/kiverdienst_v2
sudo cp -r . /opt/kiverdienst_v2/
cd /opt/kiverdienst_v2
```

### 2. Configure Environment

```bash
# Copy template to .env
cp .env.template .env

# Generate secure passwords and keys
export POSTGRES_PASSWORD=$(openssl rand -base64 48)
export SECRET_KEY=$(openssl rand -hex 64)
export JWT_SECRET_KEY=$(openssl rand -hex 64)

# Update .env file (Linux/Mac)
sed -i "s/CHANGE_ME_secure_random_password_here_min_32_chars/$POSTGRES_PASSWORD/g" .env
sed -i "s/CHANGE_ME_generate_random_secret_key_min_64_chars_hexadecimal/$SECRET_KEY/g" .env
sed -i "s/CHANGE_ME_another_random_secret_for_jwt_tokens/$JWT_SECRET_KEY/g" .env

# Or edit manually
nano .env
```

### 3. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Initialize Database

```bash
# Run database initialization script
docker-compose exec fastapi python /opt/kiverdienst_v2/scripts/init_db.py

# Or with sample data
docker-compose exec fastapi python /opt/kiverdienst_v2/scripts/init_db.py --samples
```

### 5. Verify Installation

```bash
# Check all services are healthy
docker-compose ps

# Test API
curl http://localhost/api/health

# Test Ollama
curl http://localhost/ollama/api/tags

# Access WebUI
# Open browser: http://localhost
```

## ⚙️ Environment Configuration

### Critical Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `POSTGRES_PASSWORD` | Database password | - | ✅ |
| `POSTGRES_USER` | Database username | kiverdienst | ✅ |
| `POSTGRES_DB` | Database name | kiverdienst_v2 | ✅ |
| `SECRET_KEY` | Application secret key | - | ✅ |
| `OLLAMA_HOST` | Ollama API endpoint | http://ollama:11434 | ✅ |
| `API_PORT` | FastAPI port | 8000 | ✅ |

### Generating Secrets

```bash
# PostgreSQL password (48 bytes, base64)
openssl rand -base64 48

# Application secret key (64 bytes, hex)
openssl rand -hex 64

# JWT secret key (64 bytes, hex)
openssl rand -hex 64
```

## 🗄️ Database Setup

### Schema Information

The database includes:
- **9 tables**: brands, characters, character_clips, video_scripts, videos, performance_analytics, products, posting_schedule, system_config
- **35+ indexes** for optimal query performance
- **8 triggers** for automatic timestamp updates
- **2 views** for analytics
- **Foreign keys** with cascade rules

### Manual Schema Execution

```bash
# Connect to database
docker-compose exec postgres psql -U kiverdienst -d kiverdienst_v2

# Run schema
\i /docker-entrypoint-initdb.d/schema.sql

# Verify tables
\dt

# Check table structure
\d brands
```

### Database Backup

```bash
# Backup database
docker-compose exec postgres pg_dump -U kiverdienst kiverdienst_v2 > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
docker-compose exec -T postgres psql -U kiverdienst kiverdienst_v2 < backup_20240101_120000.sql
```

## 🔧 Service Management

### Docker Compose Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Stop and remove containers
docker-compose down

# Remove everything (including volumes)
docker-compose down -v

# View logs
docker-compose logs -f [service_name]

# Execute commands in containers
docker-compose exec [service_name] [command]

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

### Individual Service Management

```bash
# Restart specific service
docker-compose restart postgres
docker-compose restart fastapi
docker-compose restart ollama
docker-compose restart nginx

# View service logs
docker-compose logs -f postgres
docker-compose logs -f fastapi --tail=100

# Check service health
docker-compose exec postgres pg_isready -U kiverdienst
docker-compose exec ollama ollama list
```

### Ollama Model Management

```bash
# List installed models
docker-compose exec ollama ollama list

# Pull a new model
docker-compose exec ollama ollama pull llama3.1:8b

# Remove a model
docker-compose exec ollama ollama rm llama3.1:8b

# Test model
docker-compose exec ollama ollama run llama3.1:8b "Hello, how are you?"
```

## 📚 API Documentation

### Endpoints

#### Health Check
```bash
GET /health
curl http://localhost/health
```

#### API Routes
```bash
# All API endpoints are prefixed with /api/
GET /api/brands
POST /api/videos
GET /api/analytics
```

#### Ollama Routes
```bash
# All Ollama endpoints are prefixed with /ollama/
GET /ollama/api/tags
POST /ollama/api/generate
```

### FastAPI Swagger Docs

Access interactive API documentation:
- Swagger UI: `http://localhost/api/docs`
- ReDoc: `http://localhost/api/redoc`

## 🔍 Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**Symptoms:** FastAPI can't connect to PostgreSQL

**Solutions:**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Verify credentials in .env
cat .env | grep POSTGRES

# Test connection manually
docker-compose exec postgres psql -U kiverdienst -d kiverdienst_v2 -c "SELECT 1"

# Restart PostgreSQL
docker-compose restart postgres
```

#### 2. Ollama Models Not Loading

**Symptoms:** Ollama returns empty model list

**Solutions:**
```bash
# Check Ollama logs
docker-compose logs ollama

# Manually pull models
docker-compose exec ollama ollama pull llama3.1:8b
docker-compose exec ollama ollama pull llama3.1:70b

# Check disk space
docker-compose exec ollama df -h

# Restart Ollama
docker-compose restart ollama
```

#### 3. Nginx 502 Bad Gateway

**Symptoms:** Cannot access services through Nginx

**Solutions:**
```bash
# Check Nginx logs
docker-compose logs nginx

# Verify backend services are running
docker-compose ps

# Test FastAPI directly
curl http://localhost:8000/health

# Check Nginx configuration
docker-compose exec nginx nginx -t

# Restart Nginx
docker-compose restart nginx
```

#### 4. Permission Denied

**Symptoms:** Cannot create volumes or mount directories

**Solutions:**
```bash
# Check directory permissions
ls -la /opt/kiverdienst_v2

# Fix permissions
sudo chown -R $USER:$USER /opt/kiverdienst_v2
sudo chmod -R 755 /opt/kiverdienst_v2

# Check Docker socket permissions
sudo chmod 666 /var/run/docker.sock
```

#### 5. Out of Memory

**Symptoms:** Services crashing, slow performance

**Solutions:**
```bash
# Check memory usage
docker stats

# Increase Docker memory limit
# Edit Docker Desktop settings or /etc/docker/daemon.json

# Use smaller Ollama model
docker-compose exec ollama ollama pull llama3.1:8b

# Stop unused containers
docker stop $(docker ps -q)
```

### Debug Mode

Enable debug logging:

```bash
# Edit .env
DEBUG=true
LOG_LEVEL=DEBUG

# Restart services
docker-compose restart
```

### View Container Stats

```bash
# Real-time stats
docker stats

# Disk usage
docker system df

# Volume inspection
docker volume inspect kiverdienst_postgres_data
```

## 🚀 Production Deployment

### Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Enable SSL/TLS (configure Nginx HTTPS)
- [ ] Set `DEBUG=false` in .env
- [ ] Configure firewall rules
- [ ] Use Docker secrets for sensitive data
- [ ] Enable log rotation
- [ ] Set up monitoring and alerts
- [ ] Configure automated backups
- [ ] Use non-root users in containers

### SSL/TLS Setup

```bash
# Generate self-signed certificate (development)
mkdir -p docker/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/ssl/key.pem \
  -out docker/ssl/cert.pem

# For production, use Let's Encrypt
# Uncomment HTTPS block in docker/nginx.conf
```

### Monitoring

```bash
# Install monitoring tools
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Access Prometheus: http://localhost:9090
# Access Grafana: http://localhost:3001
```

## 💾 Backup & Recovery

### Automated Backups

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U kiverdienst kiverdienst_v2 | gzip > $BACKUP_DIR/db_$DATE.sql.gz
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
EOF

chmod +x backup.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /opt/kiverdienst_v2/backup.sh" | crontab -
```

### Volume Backup

```bash
# Backup all volumes
docker run --rm -v kiverdienst_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
docker run --rm -v kiverdienst_ollama_data:/data -v $(pwd):/backup alpine tar czf /backup/ollama_data.tar.gz -C /data .
```

### Recovery

```bash
# Restore database
gunzip < db_20240101_120000.sql.gz | docker-compose exec -T postgres psql -U kiverdienst kiverdienst_v2

# Restore volumes
docker run --rm -v kiverdienst_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_data.tar.gz -C /data
```

## ⚡ Performance Tuning

### PostgreSQL Optimization

```bash
# Edit PostgreSQL config
docker-compose exec postgres bash -c "cat >> /var/lib/postgresql/data/postgresql.conf << EOF
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 8MB
EOF"

# Restart PostgreSQL
docker-compose restart postgres
```

### Nginx Optimization

- Already configured with:
  - Gzip compression
  - Connection pooling (keepalive)
  - Rate limiting
  - Caching headers
  - Buffer tuning

### Ollama Optimization

```bash
# Use GPU acceleration (if available)
# Edit docker-compose.yml to ensure GPU is enabled

# Use smaller model for faster inference
OLLAMA_MODEL_PRIMARY=llama3.1:8b
```

## 📞 Support

### Getting Help

1. Check logs: `docker-compose logs -f`
2. Review this README
3. Check [Troubleshooting](#troubleshooting) section
4. Review individual service documentation

### Useful Links

- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Nginx Documentation](https://nginx.org/en/docs/)

## 📝 License

[Your License Here]

## 🤝 Contributing

[Your Contributing Guidelines Here]

---

**KIVerdienst v2** - Built with ❤️ for content creators
