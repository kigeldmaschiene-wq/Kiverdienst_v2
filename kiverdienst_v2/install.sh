#!/bin/bash

###############################################################################
# KIVerdienst v2 - One-Command Installer
# 
# This script installs and configures the complete KIVerdienst v2 system
# Usage: ./install.sh
###############################################################################

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/kiverdienst_v2"
SERVER_IP="${SERVER_IP:-135.181.129.240}"
FRONTEND_PORT=5000
BACKEND_PORT=8000
DB_PORT=5432

###############################################################################
# Helper Functions
###############################################################################

print_banner() {
    echo -e "${CYAN}"
    echo "═══════════════════════════════════════════════════════════════"
    echo "  _  ___     __             _ _                 _    __   ___  "
    echo " | |/ (_)   / _|           | (_)               | |   \ \ / / | "
    echo " | ' / _ _ | |_ ___ _ __ __| |_  ___ _ __  ___| |_   \ V /| | "
    echo " |  < | | | |  _/ _ \ '__/ _\` | |/ _ \ '_ \/ __| __|   \ / | | "
    echo " | . \| | |_| ||  __/ | | (_| | |  __/ | | \__ \ |_    | | |_| "
    echo " |_|\_\_|\__,_| \___|_|  \__,_|_|\___|_| |_|___/\__|   |_| (_) "
    echo "                                                                "
    echo "       Autonomous TikTok Content Generation System             "
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

###############################################################################
# Pre-flight Checks
###############################################################################

check_root() {
    if [ "$EUID" -ne 0 ]; then 
        log_error "Bitte führen Sie dieses Skript mit Root-Rechten aus (sudo ./install.sh)"
        exit 1
    fi
    log_success "Root-Rechte bestätigt"
}

check_system() {
    log_info "Prüfe System-Voraussetzungen..."
    
    # Check OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        log_success "Betriebssystem: $NAME $VERSION"
    else
        log_warning "Betriebssystem konnte nicht erkannt werden"
    fi
    
    # Check available disk space (need at least 10GB)
    available_space=$(df / | tail -1 | awk '{print $4}')
    if [ "$available_space" -lt 10485760 ]; then
        log_error "Nicht genügend Speicherplatz (mindestens 10GB erforderlich)"
        exit 1
    fi
    log_success "Ausreichend Speicherplatz verfügbar"
}

install_docker() {
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d ' ' -f3 | tr -d ',')
        log_success "Docker bereits installiert: v$DOCKER_VERSION"
        return
    fi
    
    log_info "Installiere Docker..."
    
    # Update package index
    apt-get update -qq
    
    # Install prerequisites
    apt-get install -y -qq \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Set up repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Start Docker service
    systemctl start docker
    systemctl enable docker
    
    log_success "Docker erfolgreich installiert"
}

install_docker_compose() {
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null 2>&1; then
        log_success "Docker Compose bereits installiert"
        return
    fi
    
    log_info "Installiere Docker Compose..."
    
    # Docker Compose should be installed with docker-compose-plugin above
    # If not, install standalone version
    curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" \
        -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    log_success "Docker Compose erfolgreich installiert"
}

###############################################################################
# Environment Setup
###############################################################################

setup_environment() {
    log_info "Konfiguriere Umgebungsvariablen..."
    
    if [ -f "$INSTALL_DIR/.env" ]; then
        log_warning ".env-Datei existiert bereits"
        read -p "Möchten Sie die bestehende .env überschreiben? (j/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[JjYy]$ ]]; then
            log_info ".env-Datei wird beibehalten"
            return
        fi
    fi
    
    # Generate secure passwords
    log_info "Generiere sichere Passwörter..."
    POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET_KEY=$(openssl rand -hex 32)
    
    # Create .env file
    cat > "$INSTALL_DIR/.env" <<EOF
# KIVerdienst v2 - Environment Configuration
# Generated: $(date)

# Database Configuration
POSTGRES_USER=kiverdienst
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=kiverdienst_v2
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql://kiverdienst:${POSTGRES_PASSWORD}@postgres:5432/kiverdienst_v2

# Application Configuration
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
DEBUG=false
LOG_LEVEL=INFO

# Server Configuration
BACKEND_PORT=${BACKEND_PORT}
FRONTEND_PORT=${FRONTEND_PORT}
SERVER_IP=${SERVER_IP}

# External APIs (to be configured in setup wizard)
OPENAI_API_KEY=
ELEVENLABS_API_KEY=
REPLICATE_API_TOKEN=
TIKTOK_ACCESS_TOKEN=

# Ollama Configuration
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL_PRIMARY=llama3.1:8b
OLLAMA_MODEL_BACKUP=llama3.1:70b

# Performance Tuning
MAX_WORKERS=4
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Security
ALLOWED_HOSTS=localhost,127.0.0.1,${SERVER_IP}
CORS_ORIGINS=http://localhost:${FRONTEND_PORT},http://${SERVER_IP}:${FRONTEND_PORT}
EOF
    
    chmod 600 "$INSTALL_DIR/.env"
    log_success "Umgebungsvariablen konfiguriert"
    
    # Show generated passwords
    echo ""
    log_warning "WICHTIG: Bitte speichern Sie diese Zugangsdaten:"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}PostgreSQL Passwort:${NC} ${POSTGRES_PASSWORD}"
    echo -e "${CYAN}Secret Key:${NC} ${SECRET_KEY}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    read -p "Drücken Sie Enter, um fortzufahren..."
}

###############################################################################
# Docker Services
###############################################################################

start_services() {
    log_info "Starte Docker-Services..."
    
    cd "$INSTALL_DIR"
    
    # Build and start containers
    docker compose down 2>/dev/null || true
    docker compose build --no-cache
    docker compose up -d
    
    log_success "Docker-Services gestartet"
}

wait_for_postgres() {
    log_info "Warte auf PostgreSQL..."
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker compose exec -T postgres pg_isready -U kiverdienst &> /dev/null; then
            log_success "PostgreSQL ist bereit"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    log_error "PostgreSQL konnte nicht gestartet werden"
    docker compose logs postgres
    exit 1
}

wait_for_backend() {
    log_info "Warte auf Backend..."
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "http://localhost:${BACKEND_PORT}/api/health" &> /dev/null; then
            log_success "Backend ist bereit"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    log_error "Backend konnte nicht gestartet werden"
    docker compose logs backend
    exit 1
}

###############################################################################
# Database Initialization
###############################################################################

initialize_database() {
    log_info "Initialisiere Datenbank..."
    
    cd "$INSTALL_DIR"
    
    # Run database initialization script
    if docker compose exec -T backend python scripts/init_db.py; then
        log_success "Datenbank erfolgreich initialisiert"
    else
        log_error "Datenbankinitialisierung fehlgeschlagen"
        exit 1
    fi
}

###############################################################################
# Health Checks
###############################################################################

perform_health_checks() {
    log_info "Führe Gesundheitsprüfungen durch..."
    
    local all_healthy=true
    
    # Check PostgreSQL
    if docker compose exec -T postgres pg_isready -U kiverdienst &> /dev/null; then
        log_success "PostgreSQL: OK"
    else
        log_error "PostgreSQL: FEHLER"
        all_healthy=false
    fi
    
    # Check Backend
    if curl -s "http://localhost:${BACKEND_PORT}/api/health" | grep -q "ok"; then
        log_success "Backend API: OK"
    else
        log_error "Backend API: FEHLER"
        all_healthy=false
    fi
    
    # Check Frontend
    if curl -s "http://localhost:${FRONTEND_PORT}/" &> /dev/null; then
        log_success "Frontend: OK"
    else
        log_error "Frontend: FEHLER"
        all_healthy=false
    fi
    
    if [ "$all_healthy" = false ]; then
        log_warning "Einige Services sind nicht gesund. Prüfen Sie die Logs mit: docker compose logs"
    fi
}

###############################################################################
# Main Installation Process
###############################################################################

main() {
    print_banner
    
    log_info "Starte Installation von KIVerdienst v2..."
    echo ""
    
    # Step 1: Pre-flight checks
    log_info "Schritt 1/8: Systemprüfungen"
    check_root
    check_system
    echo ""
    
    # Step 2: Install Docker
    log_info "Schritt 2/8: Docker Installation"
    install_docker
    install_docker_compose
    echo ""
    
    # Step 3: Setup environment
    log_info "Schritt 3/8: Umgebungskonfiguration"
    setup_environment
    echo ""
    
    # Step 4: Start services
    log_info "Schritt 4/8: Docker-Services starten"
    start_services
    echo ""
    
    # Step 5: Wait for PostgreSQL
    log_info "Schritt 5/8: Warte auf PostgreSQL"
    wait_for_postgres
    echo ""
    
    # Step 6: Initialize database
    log_info "Schritt 6/8: Datenbank initialisieren"
    initialize_database
    echo ""
    
    # Step 7: Wait for backend
    log_info "Schritt 7/8: Warte auf Backend"
    wait_for_backend
    echo ""
    
    # Step 8: Health checks
    log_info "Schritt 8/8: Gesundheitsprüfungen"
    perform_health_checks
    echo ""
    
    # Success message
    echo -e "${GREEN}"
    echo "═══════════════════════════════════════════════════════════════"
    echo "           Installation erfolgreich abgeschlossen!            "
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${NC}"
    echo ""
    echo -e "${CYAN}📱 Setup-Wizard:${NC} http://${SERVER_IP}:${FRONTEND_PORT}/setup"
    echo -e "${CYAN}📊 Dashboard:${NC}     http://${SERVER_IP}:${FRONTEND_PORT}/dashboard"
    echo -e "${CYAN}🔧 Debug-Tools:${NC}   http://${SERVER_IP}:${FRONTEND_PORT}/debug"
    echo -e "${CYAN}📚 API-Docs:${NC}      http://${SERVER_IP}:${BACKEND_PORT}/docs"
    echo ""
    echo -e "${YELLOW}Nächste Schritte:${NC}"
    echo "  1. Öffnen Sie den Setup-Wizard in Ihrem Browser"
    echo "  2. Folgen Sie den Anweisungen zur Erstkonfiguration"
    echo "  3. Fügen Sie Ihre API-Keys hinzu"
    echo "  4. Erstellen Sie Ihre erste Brand"
    echo ""
    echo -e "${CYAN}Nützliche Befehle:${NC}"
    echo "  docker compose logs -f              # Logs anzeigen"
    echo "  docker compose ps                   # Status prüfen"
    echo "  docker compose restart              # Services neu starten"
    echo "  docker compose down                 # Services stoppen"
    echo ""
    
    log_success "Installation abgeschlossen! Viel Erfolg! 🚀"
}

# Run main installation
main "$@"
