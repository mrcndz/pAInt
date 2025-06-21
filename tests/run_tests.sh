#!/bin/bash

# Test runner script for Integration Tests
# This script runs pytest for integration tests in the root tests directory

echo "Running Integration Tests..."
echo "============================"

cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/libs:$(pwd)/libs/shared:$(pwd)/libs/api:$(pwd)/libs/ai_service"
cd tests

pytest . -v --tb=short

echo ""
echo "Integration test run completed."
