# KIVerdienst v2 - Installation Guide

Quick installation guide for KIVerdienst v2 Docker setup.

## 📦 What's Included

This package includes a complete Docker setup with:

```
kiverdienst_v2/
├── docker-compose.yml          # Main Docker Compose configuration
├── .env.template               # Environment variables template
├── .gitignore                  # Git ignore rules
├── README.md                   # Complete documentation
├── INSTALL.md                  # This file
├── docker/
│   └── nginx.conf              # Nginx reverse proxy configuration
├── scripts/
│   ├── setup.sh                # Automated setup script
│   ├── init_db.py              # Database initialization script
│   └── requirements.txt        # Python dependencies
└── sql/
    └── schema.sql              # PostgreSQL database schema
```

## 🚀 Installation Methods

### Method 1: Automated Setup (Recommended)

```bash
# Navigate to project directory
cd /workspace/kiverdienst_v2

# Run setup script
./scripts/setup.sh

# Start services
docker-compose up -d

# Initialize database
docker-compose exec fastapi python /opt/kiverdienst_v2/scripts/init_db.py

# Check status
docker-compose ps
```

### Method 2: Manual Setup

```bash
# 1. Copy environment template
cp .env.template .env

# 2. Generate secrets
export POSTGRES_PASSWORD=$(openssl rand -base64 48)
export SECRET_KEY=$(openssl rand -hex 64)
export JWT_SECRET_KEY=$(openssl rand -hex 64)

# 3. Update .env file (Linux)
sed -i "s/CHANGE_ME_secure_random_password_here_min_32_chars/$POSTGRES_PASSWORD/g" .env
sed -i "s/CHANGE_ME_generate_random_secret_key_min_64_chars_hexadecimal/$SECRET_KEY/g" .env
sed -i "s/CHANGE_ME_another_random_secret_for_jwt_tokens/$JWT_SECRET_KEY/g" .env

# 4. Start services
docker-compose up -d

# 5. Initialize database
docker-compose exec fastapi python /opt/kiverdienst_v2/scripts/init_db.py
```

## ✅ Verification

### Check Services are Running

```bash
docker-compose ps
```

Expected output:
```
NAME                     STATUS    PORTS
kiverdienst_fastapi      Up        0.0.0.0:8000->8000/tcp
kiverdienst_nginx        Up        0.0.0.0:80->80/tcp
kiverdienst_ollama       Up        0.0.0.0:11434->11434/tcp
kiverdienst_postgres     Up        0.0.0.0:5432->5432/tcp
kiverdienst_webui        Up        0.0.0.0:3000->3000/tcp
```

### Test Endpoints

```bash
# Health check
curl http://localhost/health
# Expected: healthy

# API health
curl http://localhost/api/health
# Expected: JSON response

# Ollama models
curl http://localhost/ollama/api/tags
# Expected: JSON with model list

# WebUI
# Open browser: http://localhost
```

### Check Database

```bash
# Connect to database
docker-compose exec postgres psql -U kiverdienst -d kiverdienst_v2

# List tables
\dt

# Expected output: 9 tables including brands, characters, videos, etc.

# Exit
\q
```

## 🔧 Post-Installation

### Configure External Services (Optional)

Edit `.env` and add API keys if needed:

```bash
# Runway AI
RUNWAY_API_KEY=your_key_here

# Gumroad
GUMROAD_API_KEY=your_key_here

# TikTok
TIKTOK_API_KEY=your_key_here

# Instagram
INSTAGRAM_API_KEY=your_key_here
```

Restart services:
```bash
docker-compose restart
```

### Set Up SSL (Production)

```bash
# Generate SSL certificate
mkdir -p docker/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/ssl/key.pem \
  -out docker/ssl/cert.pem

# Edit docker/nginx.conf and uncomment HTTPS server block

# Restart Nginx
docker-compose restart nginx
```

### Enable Automated Backups

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/workspace/kiverdienst_v2/backups"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U kiverdienst kiverdienst_v2 | gzip > $BACKUP_DIR/db_$DATE.sql.gz
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
EOF

chmod +x backup.sh

# Test backup
./backup.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /workspace/kiverdienst_v2/backup.sh" | crontab -
```

## 📊 Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f postgres
docker-compose logs -f fastapi
docker-compose logs -f ollama

# Last 100 lines
docker-compose logs --tail=100 fastapi
```

### Resource Usage

```bash
# Real-time stats
docker stats

# Disk usage
docker system df
```

## 🛑 Stopping Services

```bash
# Stop all services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v
```

## 🔄 Updating

```bash
# Pull latest images
docker-compose pull

# Rebuild containers
docker-compose build --no-cache

# Restart with new images
docker-compose up -d
```

## ⚠️ Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker ps

# Check logs for errors
docker-compose logs

# Remove old containers and try again
docker-compose down
docker-compose up -d
```

### Database Connection Issues

```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U kiverdienst -d kiverdienst_v2 -c "SELECT 1"
```

### Ollama Models Missing

```bash
# Pull models manually
docker-compose exec ollama ollama pull llama3.1:8b
docker-compose exec ollama ollama pull llama3.1:70b

# Verify models
docker-compose exec ollama ollama list
```

### Port Already in Use

```bash
# Check what's using the port
sudo lsof -i :80    # Nginx
sudo lsof -i :5432  # PostgreSQL
sudo lsof -i :8000  # FastAPI

# Kill the process or change ports in docker-compose.yml
```

## 📚 Next Steps

1. Read the complete [README.md](README.md) for detailed documentation
2. Explore the API at http://localhost/api/docs
3. Configure external services in `.env`
4. Set up SSL for production
5. Configure automated backups

## 💡 Tips

- Keep `.env` file secure and never commit it to version control
- Regularly backup your database
- Monitor disk space (Ollama models are large)
- Use `docker-compose logs -f` to watch for errors
- Review Nginx logs at `/var/log/nginx/` in the container

## 🆘 Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs: `docker-compose logs -f`
3. Check README.md for detailed documentation
4. Verify all environment variables in `.env`
5. Ensure Docker and Docker Compose are up to date

---

**Happy coding! 🚀**
