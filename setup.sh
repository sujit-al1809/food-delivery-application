#!/bin/bash

# Setup script for Food Delivery Application - Linux/Mac

echo "🍕 Food Delivery App - Setup Script"
echo "===================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python
echo -e "${YELLOW}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install it first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python found: $(python3 --version)${NC}"
echo ""

# Check Node
echo -e "${YELLOW}Checking Node.js installation...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install it first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"
echo ""

# Backend setup
echo -e "${YELLOW}Setting up Backend...${NC}"
cd backend

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Train model
echo "Training ML model..."
python train_model.py

# Initialize database
echo "Initializing database..."
python -c "from app import create_app; app = create_app(); app.cli.invoke('init_db_command')"

echo -e "${GREEN}✓ Backend setup complete!${NC}"
echo ""

# Frontend setup
echo -e "${YELLOW}Setting up Frontend...${NC}"
cd ../frontend

# Install dependencies
echo "Installing Node dependencies..."
npm install

# Create env file
echo "Creating environment file..."
echo "VUE_APP_API_URL=http://localhost:5000/api" > .env.local
echo "VUE_APP_ENV=development" >> .env.local

echo -e "${GREEN}✓ Frontend setup complete!${NC}"
echo ""

echo "===================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "===================================="
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:5173"
echo ""
echo "Demo Credentials:"
echo "  Email: admin@fooddelivery.com"
echo "  Password: admin123456"
echo ""
