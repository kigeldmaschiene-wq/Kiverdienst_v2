#!/bin/bash

###############################################################################
# KIVerdienst v2 - Health Check Script
# 
# This script checks the health of all system components
# Usage: ./health_check.sh
###############################################################################

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:5000}"
TIMEOUT=10

# Counters
HEALTHY=0
UNHEALTHY=0

###############################################################################
# Helper Functions
###############################################################################

check_service() {
    local name=$1
    local url=$2
    
    if curl -sf --max-time "$TIMEOUT" "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}[✓]${NC} $name: ${GREEN}Healthy${NC}"
        ((HEALTHY++))
        return 0
    else
        echo -e "${RED}[✗]${NC} $name: ${RED}Unhealthy${NC}"
        ((UNHEALTHY++))
        return 1
    fi
}

check_database() {
    if docker compose exec -T postgres pg_isready -U kiverdienst &> /dev/null; then
        echo -e "${GREEN}[✓]${NC} PostgreSQL: ${GREEN}Healthy${NC}"
        ((HEALTHY++))
        return 0
    else
        echo -e "${RED}[✗]${NC} PostgreSQL: ${RED}Unhealthy${NC}"
        ((UNHEALTHY++))
        return 1
    fi
}

check_docker_container() {
    local container=$1
    local name=$2
    
    if docker ps --filter "name=$container" --filter "status=running" | grep -q "$container"; then
        local uptime=$(docker ps --filter "name=$container" --format "{{.Status}}")
        echo -e "${GREEN}[✓]${NC} $name: ${GREEN}Running${NC} ($uptime)"
        ((HEALTHY++))
        return 0
    else
        echo -e "${RED}[✗]${NC} $name: ${RED}Not running${NC}"
        ((UNHEALTHY++))
        return 1
    fi
}

get_container_logs() {
    local container=$1
    local lines=${2:-10}
    
    echo ""
    echo -e "${BLUE}Last $lines log lines from $container:${NC}"
    docker logs --tail "$lines" "$container" 2>&1 | sed 's/^/  /'
    echo ""
}

###############################################################################
# Main Health Checks
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  KIVerdienst v2 - Health Check${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Check Docker
echo -e "${BLUE}Docker Status:${NC}"
if docker info &> /dev/null; then
    echo -e "${GREEN}[✓]${NC} Docker daemon: ${GREEN}Running${NC}"
    ((HEALTHY++))
else
    echo -e "${RED}[✗]${NC} Docker daemon: ${RED}Not running${NC}"
    echo -e "${RED}  Cannot proceed with health checks${NC}"
    exit 1
fi
echo ""

# Check Docker Containers
echo -e "${BLUE}Docker Containers:${NC}"
check_docker_container "kiverdienst_postgres" "PostgreSQL"
check_docker_container "kiverdienst_backend" "Backend API"
check_docker_container "kiverdienst_frontend" "Frontend"
echo ""

# Check Database Connection
echo -e "${BLUE}Database Connection:${NC}"
check_database
echo ""

# Check Web Services
echo -e "${BLUE}Web Services:${NC}"
check_service "Backend API Health" "$BACKEND_URL/api/health"
check_service "Frontend" "$FRONTEND_URL/"
echo ""

# Get resource usage
echo -e "${BLUE}Resource Usage:${NC}"
if command -v docker &> /dev/null; then
    echo ""
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" | grep kiverdienst
    echo ""
fi

# Check for recent errors
echo -e "${BLUE}Recent Errors (if any):${NC}"
if docker compose exec -T backend python -c "
import psycopg2
import os
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()
cursor.execute(\"SELECT COUNT(*) FROM system_logs WHERE level = 'ERROR' AND created_at > NOW() - INTERVAL '1 hour'\")
count = cursor.fetchone()[0]
print(f'{count} errors in the last hour')
cursor.close()
conn.close()
" 2>/dev/null; then
    :
else
    echo -e "${YELLOW}  Unable to check error logs${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Summary:${NC}"
echo -e "  ${GREEN}Healthy: $HEALTHY${NC}"
echo -e "  ${RED}Unhealthy: $UNHEALTHY${NC}"
echo ""

if [ $UNHEALTHY -eq 0 ]; then
    echo -e "${GREEN}✓ All services are healthy!${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some services are unhealthy.${NC}"
    echo -e "${YELLOW}  Check the logs for more details:${NC}"
    echo -e "    docker compose logs -f"
    echo ""
    
    # Ask if user wants to see logs
    if [ -t 0 ]; then
        read -p "Show detailed logs for unhealthy services? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [ $UNHEALTHY -gt 0 ]; then
                docker ps -a --filter "name=kiverdienst" --format "{{.Names}}" | while read container; do
                    if ! docker ps --filter "name=$container" --filter "status=running" | grep -q "$container"; then
                        get_container_logs "$container"
                    fi
                done
            fi
        fi
    fi
    
    exit 1
fi
