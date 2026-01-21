#!/bin/bash

# Exit on error
set -e

echo "Running Flutter Tests..."
flutter test

echo "All tests passed!"
