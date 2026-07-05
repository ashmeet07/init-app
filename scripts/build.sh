#!/bin/bash

echo ""
echo "📦 Building py-create package..."
echo ""

rm -rf build/ dist/ *.egg-info

PYTHON_BIN="${PYTHON:-python3}"

"$PYTHON_BIN" scripts/build_compiler.py
"$PYTHON_BIN" -m build

echo ""
echo "✔ Build complete 😌🔥"
echo ""
