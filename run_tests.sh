#!/bin/bash

# Task Management API Test Runner
# This script runs all tests (pytest and Gauge) for the Task Management API

echo "🚀 Starting Task Management API Test Suite"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status