#!/usr/bin/env bash
set -euo pipefail

# Build the standard wheel and source dist with the NumPy dependency.
python -m build --sdist --wheel

echo "Wheel and source dist build complete."