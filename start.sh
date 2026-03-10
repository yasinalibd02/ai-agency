#!/bin/bash
# Virtual Agency — Start Script
# Launches both the FastAPI backend and Next.js frontend

set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "🚀 Starting Virtual Agency..."

# ── Backend ──────────────────────────────────────────────
echo ""
echo "📦 Setting up Python backend..."
cd "$ROOT/backend"

if [ ! -d ".venv" ]; then
  echo "  Creating virtual environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt -q

echo "✅ Backend dependencies installed."
echo "🔧 Starting FastAPI server on http://localhost:8000 ..."
cd "$ROOT"
uvicorn backend.main:app --reload --port 8000 --host 0.0.0.0 &
BACKEND_PID=$!

# ── Frontend ─────────────────────────────────────────────
echo ""
echo "📦 Setting up Next.js frontend..."
cd "$ROOT"

if [ ! -d "node_modules" ]; then
  npm install
fi

echo "⚛️  Starting Next.js on http://localhost:3000 ..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "═══════════════════════════════════════════════"
echo "  ✅ Virtual Agency is running!"
echo "  🌐 Dashboard:  http://localhost:3000"
echo "  🔌 API:        http://localhost:8000"
echo "  📖 API Docs:   http://localhost:8000/docs"
echo "═══════════════════════════════════════════════"
echo ""
echo "Press Ctrl+C to stop all services."

# Wait and cleanup
cleanup() {
  echo ""
  echo "🔴 Shutting down..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  exit 0
}
trap cleanup SIGINT SIGTERM
wait
