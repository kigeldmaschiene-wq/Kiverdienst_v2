#!/bin/bash

###############################################################################
# KIVerdienst v2 - Dependency Checker
# 
# This script checks if all required dependencies are installed
# Usage: ./check_dependencies.sh
###############################################################################

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0

###############################################################################
# Helper Functions
###############################################################################

check_command() {
    local cmd=$1
    local name=$2
    local required=$3
    
    if command -v "$cmd" &> /dev/null; then
        local version=$($cmd --version 2>&1 | head -n1)
        echo -e "${GREEN}[✓]${NC} $name: ${BLUE}$version${NC}"
        ((CHECKS_PASSED++))
        return 0
    else
        if [ "$required" = "required" ]; then
            echo -e "${RED}[✗]${NC} $name: ${RED}Not installed (required)${NC}"
            ((CHECKS_FAILED++))
        else
            echo -e "${YELLOW}[⚠]${NC} $name: ${YELLOW}Not installed (optional)${NC}"
        fi
        return 1
    fi
}

check_port() {
    local port=$1
    local service=$2
    
    if nc -z localhost "$port" 2>/dev/null; then
        echo -e "${GREEN}[✓]${NC} Port $port ($service): ${GREEN}Available${NC}"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${YELLOW}[⚠]${NC} Port $port ($service): ${YELLOW}In use or not accessible${NC}"
        return 1
    fi
}

check_disk_space() {
    local required_gb=$1
    local available=$(df / | tail -1 | awk '{print $4}')
    local available_gb=$((available / 1024 / 1024))
    
    if [ "$available_gb" -ge "$required_gb" ]; then
        echo -e "${GREEN}[✓]${NC} Disk space: ${BLUE}${available_gb}GB available${NC} (${required_gb}GB required)"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}[✗]${NC} Disk space: ${RED}${available_gb}GB available${NC} (${required_gb}GB required)"
        ((CHECKS_FAILED++))
        return 1
    fi
}

check_memory() {
    local required_gb=$1
    local available=$(free -g | awk '/^Mem:/{print $2}')
    
    if [ "$available" -ge "$required_gb" ]; then
        echo -e "${GREEN}[✓]${NC} Memory: ${BLUE}${available}GB total${NC} (${required_gb}GB required)"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${YELLOW}[⚠]${NC} Memory: ${YELLOW}${available}GB total${NC} (${required_gb}GB required)"
        return 1
    fi
}

###############################################################################
# Main Checks
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  KIVerdienst v2 - Dependency Checker${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# System Information
echo -e "${BLUE}System Information:${NC}"
echo -e "  OS: $(uname -s) $(uname -r)"
echo -e "  Architecture: $(uname -m)"
echo ""

# Required Commands
echo -e "${BLUE}Required Software:${NC}"
check_command "docker" "Docker" "required"
check_command "docker-compose" "Docker Compose" "required" || check_command "docker compose" "Docker Compose (plugin)" "required"
check_command "git" "Git" "required"
check_command "curl" "cURL" "required"
check_command "openssl" "OpenSSL" "required"
echo ""

# Optional Commands
echo -e "${BLUE}Optional Software:${NC}"
check_command "python3" "Python 3" "optional"
check_command "psql" "PostgreSQL Client" "optional"
check_command "nc" "Netcat" "optional"
echo ""

# System Resources
echo -e "${BLUE}System Resources:${NC}"
check_disk_space 10  # 10GB minimum
check_memory 4       # 4GB minimum
echo ""

# Port Availability
echo -e "${BLUE}Port Availability:${NC}"
check_port 5000 "Frontend"
check_port 8000 "Backend API"
check_port 5432 "PostgreSQL"
check_port 80 "Nginx"
echo ""

# Docker Status
echo -e "${BLUE}Docker Status:${NC}"
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        echo -e "${GREEN}[✓]${NC} Docker daemon: ${GREEN}Running${NC}"
        ((CHECKS_PASSED++))
        
        # Docker version details
        DOCKER_VERSION=$(docker version --format '{{.Server.Version}}')
        echo -e "  Docker version: ${BLUE}$DOCKER_VERSION${NC}"
        
        # Check Docker Compose
        if docker compose version &> /dev/null 2>&1; then
            COMPOSE_VERSION=$(docker compose version --short)
            echo -e "  Docker Compose version: ${BLUE}$COMPOSE_VERSION${NC}"
        elif command -v docker-compose &> /dev/null; then
            COMPOSE_VERSION=$(docker-compose --version | awk '{print $4}' | tr -d ',')
            echo -e "  Docker Compose version: ${BLUE}$COMPOSE_VERSION${NC}"
        fi
    else
        echo -e "${RED}[✗]${NC} Docker daemon: ${RED}Not running${NC}"
        ((CHECKS_FAILED++))
    fi
else
    echo -e "${RED}[✗]${NC} Docker: ${RED}Not installed${NC}"
    ((CHECKS_FAILED++))
fi
echo ""

# Environment File
echo -e "${BLUE}Configuration:${NC}"
if [ -f "/opt/kiverdienst_v2/.env" ] || [ -f ".env" ]; then
    echo -e "${GREEN}[✓]${NC} .env file: ${GREEN}Found${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}[⚠]${NC} .env file: ${YELLOW}Not found${NC} (will be created by installer)"
fi
echo ""

# Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Summary:${NC}"
echo -e "  ${GREEN}Passed: $CHECKS_PASSED${NC}"
echo -e "  ${RED}Failed: $CHECKS_FAILED${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All required dependencies are met!${NC}"
    echo -e "${GREEN}  You can proceed with the installation.${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some required dependencies are missing.${NC}"
    echo -e "${YELLOW}  Please install missing dependencies before proceeding.${NC}"
    echo ""
    exit 1
fi
