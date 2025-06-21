#!/bin/bash

# AI Service Test Runner
# This script runs all tests for the AI service

echo "Running AI Service Tests..."
echo "=========================="

# Change to the repository root
cd "$(dirname "$0")/../.."

# Set up Python path to include necessary modules  
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/libs:$(pwd)/libs/shared:$(pwd)/libs/api:$(pwd)/libs/ai_service"

# Run unit tests using module discovery from root
echo "Running unit tests..."
python -m pytest --verbose --tb=short -p no:warnings -x libs/ai_service/tests/unit/

# Run integration tests if they exist
if [ -d "libs/ai_service/tests/integration" ]; then
    echo ""
    echo "Running integration tests..."
    touch libs/ai_service/tests/integration/__init__.py
    python -m pytest --verbose --tb=short -p no:warnings -x libs/ai_service/tests/integration/
fi

# Run all tests if requested
if [ "$1" = "--all" ]; then
    echo ""
    echo "Running all tests..."
    python -m pytest --verbose --tb=short -p no:warnings libs/ai_service/tests/
fi

echo ""
echo "Test run completed!"
