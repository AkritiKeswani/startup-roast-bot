#!/bin/bash
set -e

echo "🐛 Debug Mode - Startup Roast Bot"
echo "================================="

# Check environment
echo "📋 Environment Check:"
if [ -f .env ]; then
    echo "✅ .env file exists"
    if grep -q "your_.*_here" .env; then
        echo "❌ .env contains placeholder values"
    else
        echo "✅ .env has real API keys"
    fi
else
    echo "❌ .env file missing"
fi

# Check Python environment
echo ""
echo "🐍 Python Environment:"
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists"
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment missing"
fi

# Check dependencies
echo ""
echo "📦 Dependencies:"
if python -c "import fastapi, playwright, requests" 2>/dev/null; then
    echo "✅ Python dependencies installed"
else
    echo "❌ Missing Python dependencies"
fi

# Check frontend
echo ""
echo "🎨 Frontend:"
if [ -d "ui/node_modules" ]; then
    echo "✅ Frontend dependencies installed"
else
    echo "❌ Frontend dependencies missing"
fi

# Test API keys
echo ""
echo "🔑 API Key Test:"
source .env 2>/dev/null || true
if [ -n "$BROWSERBASE_API_KEY" ] && [ -n "$BROWSERBASE_PROJECT_ID" ]; then
    echo "✅ Browserbase keys set"
else
    echo "❌ Browserbase keys missing"
fi

if [ -n "$GROK_API_KEY" ]; then
    echo "✅ Grok key set"
else
    echo "❌ Grok key missing"
fi

echo ""
echo "🚀 To start the app: ./start.sh"
echo "🐛 To debug: Check the backend terminal for detailed logs"
