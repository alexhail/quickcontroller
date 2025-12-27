#!/bin/bash
set -e

echo "=== Quick Controller E2E Test Runner ==="

# Check if services are running
echo "Checking services..."
if ! docker compose ps --format json | grep -q "qc-api"; then
    echo "Error: Services not running. Start with: docker compose up -d"
    exit 1
fi

# Build and run E2E tests
echo "Building E2E test container..."
docker compose build e2e

echo "Running E2E tests..."
docker compose run --rm e2e

echo "=== Tests Complete ==="
