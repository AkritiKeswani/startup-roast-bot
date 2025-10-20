#!/bin/bash
set -e

echo "🚀 Starting Startup Roast Bot..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it with your API keys:"
    echo "BROWSERBASE_API_KEY=your_key_here"
    echo "BROWSERBASE_PROJECT_ID=your_project_id_here"
    echo "GROK_API_KEY=your_grok_key_here"
    exit 1
fi

# Check if API keys are set
if grep -q "your_.*_here" .env; then
    echo "❌ Please update .env with your actual API keys"
    exit 1
fi

echo "✅ Environment configured"

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
lsof -ti:5000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
lsof -ti:5174 | xargs kill -9 2>/dev/null || true
lsof -ti:5175 | xargs kill -9 2>/dev/null || true

# Start backend in background
echo "🔧 Starting backend..."
source venv/bin/activate
uvicorn app.main:app --reload --port 5000 &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Check if backend is running
if ! curl -s http://localhost:5000/health > /dev/null; then
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Backend running on http://localhost:5000"

# Start frontend
echo "🎨 Starting frontend..."
cd ui
npm run dev &
FRONTEND_PID=$!

echo "✅ Frontend starting on http://localhost:5173"
echo ""
echo "🎉 Startup Roast Bot is ready!"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for user to stop
trap "echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit 0" INT
wait
