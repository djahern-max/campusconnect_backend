.PHONY: help test test-unit test-integration test-auth test-gallery test-quick test-cov clean

help:
	@echo "CampusConnect Test Commands:"
	@echo "  make test              - Run all tests"
	@echo "  make test-unit         - Unit tests only"
	@echo "  make test-integration  - Integration tests only"
	@echo "  make test-auth         - Auth flow tests"
	@echo "  make test-gallery      - Gallery/image tests"
	@echo "  make test-quick        - Quick unit tests"
	@echo "  make test-cov          - Tests with coverage"
	@echo "  make clean             - Clean artifacts"

test:
	@./tests/run_tests.sh

test-unit:
	@./tests/run_tests.sh unit

test-integration:
	@./tests/run_tests.sh integration

test-auth:
	@./tests/run_tests.sh auth

test-gallery:
	@./tests/run_tests.sh gallery

test-quick:
	@./tests/run_tests.sh quick

test-cov:
	@./tests/run_tests.sh coverage

clean:
	@echo "🧹 Cleaning..."
	rm -rf .pytest_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
