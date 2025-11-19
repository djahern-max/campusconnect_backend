#!/bin/bash

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 CampusConnect Test Suite${NC}"
echo "======================================"

# Load test environment if exists
if [ -f ".env.test" ]; then
    echo -e "${YELLOW}Loading test environment...${NC}"
    export $(cat .env.test | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}No .env.test found, using defaults...${NC}"
    export TEST_DATABASE_URL="postgresql+asyncpg://postgres:your_password@localhost:5432/campusconnect_test"
fi

# Check backend health (for integration tests)
if [ "$1" != "unit" ]; then
    echo -e "\n${YELLOW}Checking backend...${NC}"
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo -e "${GREEN}✅ Backend is running${NC}"
    else
        echo -e "${RED}❌ Backend not running${NC}"
        echo -e "${YELLOW}Tip: Start with: uvicorn app.main:app --reload${NC}"
        echo -e "${YELLOW}(Unit tests will still run)${NC}"
    fi
fi

case "$1" in
    "unit")
        echo -e "\n${YELLOW}Running unit tests...${NC}"
        pytest tests/unit/ -v -m unit
        ;;
    "integration")
        echo -e "\n${YELLOW}Running integration tests...${NC}"
        pytest tests/integration/ -v -m integration
        ;;
    "auth")
        echo -e "\n${YELLOW}Running auth tests...${NC}"
        pytest tests/ -v -m auth
        ;;
    "gallery")
        echo -e "\n${YELLOW}Running gallery tests...${NC}"
        pytest tests/ -v -m gallery
        ;;
    "quick")
        echo -e "\n${YELLOW}Running quick tests (unit only)...${NC}"
        pytest tests/unit/ -v -x --tb=line
        ;;
    "coverage")
        echo -e "\n${YELLOW}Running with coverage...${NC}"
        pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing
        echo -e "\n${GREEN}📊 Coverage report: htmlcov/index.html${NC}"
        ;;
    *)
        echo -e "\n${YELLOW}Running all tests...${NC}"
        pytest tests/ -v
        ;;
esac

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Tests completed successfully!${NC}"
else
    echo -e "\n${RED}❌ Some tests failed${NC}"
    exit 1
fi
