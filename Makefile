PC_API_KEY ?=
PYTHON ?= $(shell which python3 2>/dev/null || which python 2>/dev/null || echo python3)

# Run all tests
test:
	@PC_API_KEY=$(PC_API_KEY) $(PYTHON) -m unittest discover -s . -p "test_*.py" -v

# Run tests with coverage
test-coverage:
	@PC_API_KEY=$(PC_API_KEY) $(PYTHON) -m coverage run -m unittest discover -s . -p "test_*.py"
	@$(PYTHON) -m coverage report -m

# Install package in development mode
install:
	pip install -e .

# Install development dependencies
install-dev:
	pip install -e .
	pip install coverage pylint black

# Format code
format:
	black private_captcha/ test_*.py

# Lint code
lint:
	pylint private_captcha/ test_*.py

# Clean up build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build package
build: clean
	$(PYTHON) setup.py sdist bdist_wheel

# Run a single test file
test-client:
	@PC_API_KEY=$(PC_API_KEY) $(PYTHON) -m unittest test_client.py -v

.PHONY: test test-coverage install install-dev format lint clean build test-client
