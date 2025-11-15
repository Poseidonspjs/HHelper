#!/bin/bash

# HoosHelper Setup Script
# Automated setup for development environment

set -e  # Exit on error

echo "🎓 HoosHelper Setup Script"
echo "=========================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    echo -e "${RED}❌ Unsupported operating system${NC}"
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."
echo ""

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js: $NODE_VERSION"
else
    echo -e "${RED}✗${NC} Node.js not found. Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓${NC} npm: $NPM_VERSION"
else
    echo -e "${RED}✗${NC} npm not found"
    exit 1
fi

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.10+ from https://python.org"
    exit 1
fi

# Check pip
if command_exists pip3; then
    PIP_VERSION=$(pip3 --version)
    echo -e "${GREEN}✓${NC} pip3: installed"
else
    echo -e "${RED}✗${NC} pip3 not found"
    exit 1
fi

echo ""
echo "=========================="
echo ""

# Setup Frontend
echo "🎨 Setting up Frontend..."
echo ""

cd frontend

# Install dependencies
echo "Installing npm packages..."
npm install

# Check if .env exists
if [ ! -f .env.local ]; then
    echo -e "${YELLOW}⚠${NC}  Creating .env.local template..."
    cat > .env.local << 'EOF'
# Database Connection
DATABASE_URL="postgresql://user:password@localhost:5432/hooshelper?schema=public"
DIRECT_URL="postgresql://user:password@localhost:5432/hooshelper"

# Backend API
NEXT_PUBLIC_API_URL="http://localhost:8000"
EOF
    echo -e "${YELLOW}⚠${NC}  Please update .env.local with your database credentials"
fi

# Generate Prisma client
echo "Generating Prisma client..."
npx prisma generate

echo -e "${GREEN}✓${NC} Frontend setup complete!"
echo ""

cd ..

# Setup Backend
echo "🔧 Setting up Backend..."
echo ""

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
if [ "$OS" = "macos" ]; then
    source venv/bin/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠${NC}  Creating .env template..."
    cat > .env << 'EOF'
# Database Connection
DATABASE_URL="postgresql://user:password@localhost:5432/hooshelper"
DIRECT_URL="postgresql://user:password@localhost:5432/hooshelper"

# OpenAI API Key
OPENAI_API_KEY="sk-..."

# Anthropic API Key
ANTHROPIC_API_KEY="sk-ant-..."

# Supabase (optional)
SUPABASE_URL=""
SUPABASE_ANON_KEY=""

# Backend Config
BACKEND_PORT=8000
FRONTEND_URL="http://localhost:3000"
EOF
    echo -e "${YELLOW}⚠${NC}  Please update .env with your API keys"
fi

echo -e "${GREEN}✓${NC} Backend setup complete!"
echo ""

cd ..

# Database setup instructions
echo "=========================="
echo ""
echo "📊 Database Setup"
echo ""
echo "You need PostgreSQL with the pgvector extension."
echo ""
echo "Option 1: Use Supabase (Easiest)"
echo "  1. Go to https://supabase.com"
echo "  2. Create a new project"
echo "  3. Copy the connection string"
echo "  4. Update DATABASE_URL in frontend/.env.local and backend/.env"
echo ""
echo "Option 2: Local PostgreSQL"
echo "  1. Install PostgreSQL: https://www.postgresql.org/download/"
echo "  2. Install pgvector: https://github.com/pgvector/pgvector"
echo "  3. Create database:"
echo "     $ createdb hooshelper"
echo "     $ psql hooshelper -c 'CREATE EXTENSION vector;'"
echo "  4. Update DATABASE_URL in .env files"
echo ""
echo "After setting up the database, run:"
echo "  $ cd frontend"
echo "  $ npx prisma db push"
echo ""
echo "=========================="
echo ""

# Final instructions
echo "🎉 Setup Complete!"
echo ""
echo "Next steps:"
echo ""
echo "1. Update environment variables:"
echo "   - frontend/.env.local"
echo "   - backend/.env"
echo ""
echo "2. Set up database and run migrations:"
echo "   $ cd frontend"
echo "   $ npx prisma db push"
echo ""
echo "3. (Optional) Populate with sample data:"
echo "   $ cd backend"
echo "   $ source venv/bin/activate"
echo "   $ python -c \"from scrapers import scrape_courses, scrape_clubs; scrape_courses(); scrape_clubs()\""
echo ""
echo "4. Start the application:"
echo ""
echo "   Terminal 1 (Backend):"
echo "   $ cd backend"
echo "   $ source venv/bin/activate"
echo "   $ python main.py"
echo ""
echo "   Terminal 2 (Frontend):"
echo "   $ cd frontend"
echo "   $ npm run dev"
echo ""
echo "5. Open http://localhost:3000 in your browser"
echo ""
echo "=========================="
echo ""
echo "For more information, see README.md"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"

