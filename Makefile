.PHONY: help install install-frontend install-backend setup-frontend setup-backend dev build start lint type-check clean check-env test test-backend test-all test-ethereum test-polygon test-base test-unit

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Python and pip detection
PYTHON := python3
PIP := pip3
PYTEST := pytest

##@ General

help: ## Display this help message
	@echo "$(BLUE)Available commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

##@ Setup & Installation

install: install-frontend install-backend ## Install all dependencies (frontend + backend)
	@echo "$(GREEN)✓ All dependencies installed successfully$(NC)"

install-frontend: ## Install frontend dependencies (Next.js)
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	@if [ -d frontend ]; then \
		cd frontend && npm install && echo "$(GREEN)✓ Frontend dependencies installed$(NC)"; \
	else \
		echo "$(RED)✗ frontend/ directory not found$(NC)"; \
		exit 1; \
	fi

install-backend: ## Install backend dependencies (Python)
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	@if [ -d backend ]; then \
		if [ -f backend/requirements.txt ]; then \
			cd backend && $(PIP) install -r requirements.txt && echo "$(GREEN)✓ Backend dependencies installed$(NC)"; \
		else \
			echo "$(YELLOW)⚠ backend/requirements.txt not found$(NC)"; \
		fi; \
	else \
		echo "$(RED)✗ backend/ directory not found$(NC)"; \
		exit 1; \
	fi

setup-frontend: ## Create frontend .env.local from template
	@echo "$(BLUE)Setting up frontend environment...$(NC)"
	@if [ -d frontend ]; then \
		if [ ! -f frontend/.env.local ]; then \
			echo "# The Graph API Token (JWT)" > frontend/.env.local; \
			echo "NEXT_PUBLIC_THEGRAPH_API_KEY=your_jwt_token_here" >> frontend/.env.local; \
			echo "" >> frontend/.env.local; \
			echo "# Reown Project ID" >> frontend/.env.local; \
			echo "NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=your_project_id_here" >> frontend/.env.local; \
			echo "$(GREEN)✓ Created frontend/.env.local$(NC)"; \
			echo "$(YELLOW)⚠ Please edit frontend/.env.local with your API keys$(NC)"; \
		else \
			echo "$(YELLOW)⚠ frontend/.env.local already exists$(NC)"; \
		fi; \
	else \
		echo "$(RED)✗ frontend/ directory not found$(NC)"; \
	fi

setup-backend: ## Create backend .env from template
	@echo "$(BLUE)Setting up backend environment...$(NC)"
	@if [ -d backend ]; then \
		if [ ! -f backend/.env ]; then \
			echo "# The Graph API Token (JWT)" > backend/.env; \
			echo "THEGRAPH_API_KEY=your_jwt_token_here" >> backend/.env; \
			echo "$(GREEN)✓ Created backend/.env$(NC)"; \
			echo "$(YELLOW)⚠ Please edit backend/.env with your API key$(NC)"; \
		else \
			echo "$(YELLOW)⚠ backend/.env already exists$(NC)"; \
		fi; \
	else \
		echo "$(RED)✗ backend/ directory not found$(NC)"; \
	fi

setup: setup-frontend setup-backend ## Setup both frontend and backend environments

##@ Frontend Development

dev: ## Run frontend development server
	@echo "$(BLUE)Starting frontend development server...$(NC)"
	@if [ -d frontend ]; then \
		cd frontend && npm run dev; \
	else \
		echo "$(RED)✗ frontend/ directory not found$(NC)"; \
		exit 1; \
	fi

build: ## Build frontend for production
	@echo "$(BLUE)Building frontend...$(NC)"
	@if [ -d frontend ]; then \
		cd frontend && npm run build; \
	else \
		echo "$(RED)✗ frontend/ directory not found$(NC)"; \
		exit 1; \
	fi

start: ## Start frontend production server
	@echo "$(BLUE)Starting frontend production server...$(NC)"
	@if [ -d frontend ]; then \
		cd frontend && npm run start; \
	else \
		echo "$(RED)✗ frontend/ directory not found$(NC)"; \
		exit 1; \
	fi

lint: ## Run ESLint on frontend
	@echo "$(BLUE)Running linter...$(NC)"
	@if [ -d frontend ]; then \
		cd frontend && npm run lint; \
	else \
		echo "$(RED)✗ frontend/ directory not found$(NC)"; \
		exit 1; \
	fi

type-check: ## Run TypeScript type checking on frontend
	@echo "$(BLUE)Running TypeScript type check...$(NC)"
	@if [ -d frontend ]; then \
		cd frontend && npx tsc --noEmit; \
		echo "$(GREEN)✓ Type check passed$(NC)"; \
	else \
		echo "$(RED)✗ frontend/ directory not found$(NC)"; \
		exit 1; \
	fi

check: lint type-check ## Run all frontend code quality checks

##@ Backend Testing

test: test-backend ## Run all backend tests
	@echo "$(GREEN)✓ All tests completed$(NC)"

test-backend: ## Run all backend tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	@if [ -d backend ]; then \
		cd backend && $(PYTEST) tests/ -v --tb=short; \
	else \
		echo "$(RED)✗ backend/ directory not found$(NC)"; \
		exit 1; \
	fi

test-unit: ## Run backend unit tests only
	@echo "$(BLUE)Running backend unit tests...$(NC)"
	@if [ -d backend ]; then \
		cd backend && $(PYTEST) tests/unit/ -v --tb=short; \
	else \
		echo "$(RED)✗ backend/ directory not found$(NC)"; \
		exit 1; \
	fi

test-ethereum: ## Run Ethereum balance client tests (real API calls)
	@echo "$(BLUE)Running Ethereum balance tests (real API calls)...$(NC)"
	@if [ -z "$$THEGRAPH_API_KEY" ]; then \
		if [ -f backend/.env ] || [ -f backend/.env.local ]; then \
			echo "$(BLUE)ℹ️  THEGRAPH_API_KEY not set in environment.$(NC)"; \
			echo "$(BLUE)  Tests will load from .env file automatically.$(NC)"; \
		else \
			echo "$(YELLOW)⚠ THEGRAPH_API_KEY not set. Tests will be skipped.$(NC)"; \
			echo "$(YELLOW)  Set it in backend/.env file or export: export THEGRAPH_API_KEY=your_jwt_token$(NC)"; \
		fi; \
	fi
	@if [ -d backend ]; then \
		if [ -d backend/tests/ethereum ]; then \
			cd backend && $(PYTEST) tests/ethereum/ -v -s --tb=short; \
		else \
			echo "$(YELLOW)⚠ Ethereum tests not found$(NC)"; \
		fi; \
	else \
		echo "$(RED)✗ backend/ directory not found$(NC)"; \
		exit 1; \
	fi

test-polygon: ## Run Polygon balance client tests (real API calls)
	@echo "$(BLUE)Running Polygon balance tests (real API calls)...$(NC)"
	@if [ -z "$$THEGRAPH_API_KEY" ]; then \
		if [ -f backend/.env ] || [ -f backend/.env.local ]; then \
			echo "$(BLUE)ℹ️  THEGRAPH_API_KEY not set in environment.$(NC)"; \
			echo "$(BLUE)  Tests will load from .env file automatically.$(NC)"; \
		else \
			echo "$(YELLOW)⚠ THEGRAPH_API_KEY not set. Tests will be skipped.$(NC)"; \
			echo "$(YELLOW)  Set it in backend/.env file or export: export THEGRAPH_API_KEY=your_jwt_token$(NC)"; \
		fi; \
	fi
	@if [ -d backend ]; then \
		if [ -d backend/tests/polygon ]; then \
			cd backend && $(PYTEST) tests/polygon/ -v -s --tb=short; \
		else \
			echo "$(YELLOW)⚠ Polygon tests not found$(NC)"; \
		fi; \
	else \
		echo "$(RED)✗ backend/ directory not found$(NC)"; \
		exit 1; \
	fi

test-base: ## Run Base balance client tests (real API calls)
	@echo "$(BLUE)Running Base balance tests (real API calls)...$(NC)"
	@if [ -z "$$THEGRAPH_API_KEY" ]; then \
		if [ -f backend/.env ] || [ -f backend/.env.local ]; then \
			echo "$(BLUE)ℹ️  THEGRAPH_API_KEY not set in environment.$(NC)"; \
			echo "$(BLUE)  Tests will load from .env file automatically.$(NC)"; \
		else \
			echo "$(YELLOW)⚠ THEGRAPH_API_KEY not set. Tests will be skipped.$(NC)"; \
			echo "$(YELLOW)  Set it in backend/.env file or export: export THEGRAPH_API_KEY=your_jwt_token$(NC)"; \
		fi; \
	fi
	@if [ -d backend ]; then \
		if [ -d backend/tests/base ]; then \
			cd backend && $(PYTEST) tests/base/ -v -s --tb=short; \
		else \
			echo "$(YELLOW)⚠ Base tests not found$(NC)"; \
		fi; \
	else \
		echo "$(RED)✗ backend/ directory not found$(NC)"; \
		exit 1; \
	fi

test-chains: test-ethereum test-polygon test-base ## Run all chain-specific tests
	@echo "$(GREEN)✓ All chain-specific tests passed$(NC)"

test-all: test-chains test-unit ## Run all backend tests (chain tests + unit tests)
	@echo "$(GREEN)✓ All backend tests completed$(NC)"

test-api: ## Test balance fetching with real API (usage: make test-api NETWORK=ethereum ADDRESS=0x...)
	@echo "$(BLUE)Testing balance fetching with The Graph API...$(NC)"
	@if [ -z "$(NETWORK)" ] || [ -z "$(ADDRESS)" ]; then \
		echo "$(RED)✗ Usage: make test-api NETWORK=ethereum ADDRESS=0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb$(NC)"; \
		echo "$(YELLOW)  Supported networks: ethereum, polygon, base$(NC)"; \
		echo "$(YELLOW)  Optional: TOKEN=USDC (to test specific token)$(NC)"; \
		exit 1; \
	fi
	@if [ -d backend ]; then \
		if [ -n "$(TOKEN)" ]; then \
			cd backend && $(PYTHON) test_balance_cli.py $(NETWORK) $(ADDRESS) --token $(TOKEN); \
		elif [ "$(ALL_TOKENS)" = "true" ]; then \
			cd backend && $(PYTHON) test_balance_cli.py $(NETWORK) $(ADDRESS) --all-tokens; \
		else \
			cd backend && $(PYTHON) test_balance_cli.py $(NETWORK) $(ADDRESS); \
		fi; \
	else \
		echo "$(RED)✗ backend/ directory not found$(NC)"; \
		exit 1; \
	fi

##@ Utilities

clean: ## Remove build artifacts, node_modules, and Python cache
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	@if [ -d frontend ]; then \
		rm -rf frontend/.next; \
		rm -rf frontend/node_modules; \
		echo "$(GREEN)✓ Frontend cleaned$(NC)"; \
	fi
	@if [ -d backend ]; then \
		rm -rf backend/__pycache__; \
		rm -rf backend/.pytest_cache; \
		find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true; \
		find backend -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true; \
		echo "$(GREEN)✓ Backend cleaned$(NC)"; \
	fi
	@echo "$(GREEN)✓ Clean complete$(NC)"

check-env: ## Check environment variables
	@echo "$(BLUE)Checking environment variables...$(NC)"
	@if [ -f frontend/.env.local ]; then \
		echo "$(GREEN)✓ frontend/.env.local exists$(NC)"; \
	else \
		echo "$(YELLOW)⚠ frontend/.env.local not found$(NC)"; \
	fi
	@if [ -f backend/.env ]; then \
		echo "$(GREEN)✓ backend/.env exists$(NC)"; \
	else \
		echo "$(YELLOW)⚠ backend/.env not found$(NC)"; \
	fi

##@ Information

info: ## Display project information
	@echo "$(BLUE)Project Information:$(NC)"
	@if [ -f frontend/package.json ]; then \
		echo "  Frontend Name: $$(cd frontend && node -p "require('./package.json').name")"; \
		echo "  Frontend Version: $$(cd frontend && node -p "require('./package.json').version")"; \
	fi
	@echo "  Node: $$(node --version 2>/dev/null || echo 'Not installed')"
	@echo "  npm: $$(npm --version 2>/dev/null || echo 'Not installed')"
	@echo "  Python: $$($(PYTHON) --version 2>/dev/null || echo 'Not installed')"
	@if [ -f frontend/package.json ]; then \
		echo "  Next.js: $$(cd frontend && node -p "require('./package.json').dependencies.next")"; \
	fi
	@echo ""

deps: ## Show dependency information
	@echo "$(BLUE)Frontend Dependencies:$(NC)"
	@if [ -d frontend ]; then \
		cd frontend && npm list --depth=0 2>/dev/null || echo "$(YELLOW)Run 'make install-frontend' first$(NC)"; \
	else \
		echo "$(YELLOW)frontend/ directory not found$(NC)"; \
	fi
	@echo "$(BLUE)Backend Dependencies:$(NC)"
	@if [ -d backend ]; then \
		if command -v $(PIP) &> /dev/null; then \
			$(PIP) freeze | grep -E 'httpx|pydantic|pytest|pytest-asyncio|pytest-mock|python-dotenv' || echo "$(YELLOW)Run 'make install-backend' first$(NC)"; \
		else \
			echo "$(YELLOW)pip not found. Run 'make install-backend' first$(NC)"; \
		fi; \
	else \
		echo "$(YELLOW)backend/ directory not found$(NC)"; \
	fi
	@echo ""

quick-start: install setup ## Complete setup (install + setup + info)
	@echo "$(GREEN)✓ Quick start complete!$(NC)"
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  1. Edit frontend/.env.local with your API keys"
	@echo "  2. Edit backend/.env with your API key"
	@echo "  3. Run 'make dev' to start the frontend"
	@echo "  4. Run 'make test-backend' to test the backend"

##@ Docker

# Detect docker compose command (V2 uses 'docker compose', V1 uses 'docker-compose')
DOCKER_COMPOSE := $(shell command -v docker-compose 2>/dev/null || echo "docker compose")

docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	@$(DOCKER_COMPOSE) -f docker-compose.test.yml build
	@echo "$(GREEN)✓ Docker images built$(NC)"

docker-test: docker-build ## Run all tests in Docker
	@echo "$(BLUE)Running all tests in Docker...$(NC)"
	@$(DOCKER_COMPOSE) -f docker-compose.test.yml run --rm test-all

docker-test-ethereum: docker-build ## Run Ethereum tests in Docker
	@echo "$(BLUE)Running Ethereum tests in Docker...$(NC)"
	@$(DOCKER_COMPOSE) -f docker-compose.test.yml run --rm test-ethereum

docker-test-polygon: docker-build ## Run Polygon tests in Docker
	@echo "$(BLUE)Running Polygon tests in Docker...$(NC)"
	@$(DOCKER_COMPOSE) -f docker-compose.test.yml run --rm test-polygon

docker-test-base: docker-build ## Run Base tests in Docker
	@echo "$(BLUE)Running Base tests in Docker...$(NC)"
	@$(DOCKER_COMPOSE) -f docker-compose.test.yml run --rm test-base

docker-test-unit: docker-build ## Run unit tests in Docker
	@echo "$(BLUE)Running unit tests in Docker...$(NC)"
	@$(DOCKER_COMPOSE) -f docker-compose.test.yml run --rm test-unit

docker-test-integration: docker-build ## Run integration tests in Docker (disabled - tests removed)
	@echo "$(YELLOW)Integration tests have been removed for now.$(NC)"
	@echo "$(YELLOW)See backend/tests/integration/README.md for details.$(NC)"
	@# @$(DOCKER_COMPOSE) -f docker-compose.test.yml run --rm test-integration

docker-dev: ## Start frontend in Docker
	@echo "$(BLUE)Starting frontend in Docker...$(NC)"
	@$(DOCKER_COMPOSE) up frontend

docker-clean: ## Clean Docker containers and volumes
	@echo "$(BLUE)Cleaning Docker containers and volumes...$(NC)"
	@$(DOCKER_COMPOSE) down -v 2>/dev/null || true
	@$(DOCKER_COMPOSE) -f docker-compose.test.yml down -v 2>/dev/null || true
	@echo "$(GREEN)✓ Docker cleanup complete$(NC)"

docker-shell: docker-build ## Open shell in Docker container
	@echo "$(BLUE)Opening shell in Docker container...$(NC)"
	@$(DOCKER_COMPOSE) -f docker-compose.test.yml run --rm backend-test /bin/bash
