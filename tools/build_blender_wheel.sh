#!/usr/bin/env bash
set -euo pipefail

# Build the Blender-specific wheel without NumPy dependency metadata.
BLENDER_BUILD=1 python -m build --wheel

echo "Blender wheel build complete."