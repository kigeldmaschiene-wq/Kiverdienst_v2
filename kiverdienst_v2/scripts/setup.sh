#!/bin/bash
# KIVerdienst v2 - Quick Setup Script
# This script automates the initial setup process

set -e

echo "=================================================="
echo "KIVerdienst v2 - Quick Setup"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}ERROR: Please do not run this script as root${NC}"
    exit 1
fi

# Check prerequisites
echo "Checking prerequisites..."

command -v docker >/dev/null 2>&1 || { 
    echo -e "${RED}ERROR: Docker is not installed. Please install Docker first.${NC}"
    exit 1
}

command -v docker-compose >/dev/null 2>&1 || { 
    echo -e "${RED}ERROR: Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
}

command -v openssl >/dev/null 2>&1 || { 
    echo -e "${RED}ERROR: OpenSSL is not installed. Please install OpenSSL first.${NC}"
    exit 1
}

echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo -e "${YELLOW}WARNING: .env file already exists${NC}"
    read -p "Do you want to overwrite it? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled. Using existing .env file."
        exit 0
    fi
fi

# Copy template
echo "Creating .env file from template..."
cp .env.template .env
echo -e "${GREEN}✓ .env file created${NC}"
echo ""

# Generate secrets
echo "Generating secure random passwords and keys..."

POSTGRES_PASSWORD=$(openssl rand -base64 48 | tr -d '\n')
SECRET_KEY=$(openssl rand -hex 64)
JWT_SECRET_KEY=$(openssl rand -hex 64)

echo -e "${GREEN}✓ Secrets generated${NC}"
echo ""

# Update .env file
echo "Updating .env file with generated secrets..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/CHANGE_ME_secure_random_password_here_min_32_chars/$POSTGRES_PASSWORD/g" .env
    sed -i '' "s/CHANGE_ME_generate_random_secret_key_min_64_chars_hexadecimal/$SECRET_KEY/g" .env
    sed -i '' "s/CHANGE_ME_another_random_secret_for_jwt_tokens/$JWT_SECRET_KEY/g" .env
else
    # Linux
    sed -i "s/CHANGE_ME_secure_random_password_here_min_32_chars/$POSTGRES_PASSWORD/g" .env
    sed -i "s/CHANGE_ME_generate_random_secret_key_min_64_chars_hexadecimal/$SECRET_KEY/g" .env
    sed -i "s/CHANGE_ME_another_random_secret_for_jwt_tokens/$JWT_SECRET_KEY/g" .env
fi

# Also update DATABASE_URL
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|postgresql://kiverdienst:CHANGE_ME_secure_random_password_here_min_32_chars@postgres:5432/kiverdienst_v2|postgresql://kiverdienst:$POSTGRES_PASSWORD@postgres:5432/kiverdienst_v2|g" .env
else
    sed -i "s|postgresql://kiverdienst:CHANGE_ME_secure_random_password_here_min_32_chars@postgres:5432/kiverdienst_v2|postgresql://kiverdienst:$POSTGRES_PASSWORD@postgres:5432/kiverdienst_v2|g" .env
fi

echo -e "${GREEN}✓ .env file configured${NC}"
echo ""

# Create directories
echo "Creating necessary directories..."
mkdir -p docker/ssl
mkdir -p backups
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Summary
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Your environment is now configured with:"
echo "  - PostgreSQL password (64 chars)"
echo "  - Application secret key (128 chars)"
echo "  - JWT secret key (128 chars)"
echo ""
echo -e "${YELLOW}IMPORTANT: Keep your .env file secure!${NC}"
echo ""
echo "Next steps:"
echo "  1. Review and adjust settings in .env if needed"
echo "  2. Start services: docker-compose up -d"
echo "  3. Check status: docker-compose ps"
echo "  4. View logs: docker-compose logs -f"
echo ""
echo "For more information, see README.md"
echo ""
