#!/usr/bin/env bash
# Build script for fleet agent - runs inside Codespace
set -euo pipefail

cd "$(dirname "$0")"
echo "📦 Installing Python dependencies..."
python3 -m pip install --user -r requirements.txt
echo ""
echo "🤖 Testing agent help..."
python3 agent.py --help
echo ""
echo "✅ Build complete!"
