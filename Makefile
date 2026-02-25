# OmniTrader Makefile
# ====================

.PHONY: install run live test clean logs help db-stats dev check

# Default target
help:
	@echo "OmniTrader Commands:"
	@echo "  make install    - Create venv and install dependencies"
	@echo "  make run        - Run in paper trading mode"
	@echo "  make live       - Run in live trading mode"
	@echo "  make test       - Run tests"
	@echo "  make logs       - Tail trade logs"
	@echo "  make clean      - Remove venv and cache"
	@echo "  make db-stats   - Show database statistics"

# Install dependencies
install:
	@echo "Creating virtual environment..."
	cd backend && uv venv
	@echo "Installing backend dependencies..."
	cd backend && . .venv/bin/activate && uv pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Creating data directory..."
	mkdir -p backend/data
	@echo "Installation complete! Run 'make run' to start."

# Run in paper trading mode (default)
run:
	@echo "Starting OmniTrader Backend & Frontend in PAPER mode..."
	@(cd backend && . .venv/bin/activate && python -m src.main) & \
	(cd frontend && bun dev) & \
	wait

# Run in live trading mode
live:
	@echo "⚠️  Starting OmniTrader in LIVE mode!"
	@echo "Press Ctrl+C within 5 seconds to cancel..."
	@sleep 5
	@(cd backend && . .venv/bin/activate && OMNITRADER_LIVE=1 python -m src.main) & \
	(cd frontend && npm run dev) & \
	wait

# Run tests
test:
	cd backend && . .venv/bin/activate && python -m pytest tests/ -v

# Show recent logs
logs:
	@echo "Recent trade activity:"
	@sqlite3 backend/data/trades.db "SELECT * FROM trades ORDER BY opened_at DESC LIMIT 10;" 2>/dev/null || echo "No trades yet"

# Database statistics
db-stats:
	@echo "=== Trade Statistics ==="
	@sqlite3 backend/data/trades.db "\
		SELECT \
			COUNT(*) as total_trades, \
			SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins, \
			SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses, \
			ROUND(SUM(pnl), 2) as total_pnl \
		FROM trades WHERE pnl IS NOT NULL;" 2>/dev/null || echo "No closed trades yet"

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf backend/.venv backend/__pycache__ backend/src/__pycache__
	rm -f backend/data/trades.db
	rm -rf frontend/node_modules
	@echo "Clean complete"

# Development: watch and run
dev:
	@mkdir -p logs
	@(cd backend && . .venv/bin/activate && python -m src.main 2>&1 | tee -a ../logs/omnitrader.log) & \
	(cd frontend && npm run dev) & \
	wait

# Check config
check:
	@echo "=== Configuration Check ==="
	@cat backend/config/config.yaml
	@echo ""
	@echo "=== Environment Check ==="
	@test -f .env && echo ".env file: ✓" || echo ".env file: ✗ (copy from .env.example)"
	@test -f backend/.venv/bin/activate && echo "Backend Virtual env: ✓" || echo "Backend Virtual env: ✗ (run 'make install')"
	@test -d frontend/node_modules && echo "Frontend Modules: ✓" || echo "Frontend Modules: ✗ (run 'make install')"
