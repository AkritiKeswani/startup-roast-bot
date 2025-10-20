# 🍖 Startup Roast Bot

A full-stack application that scrapes startup landing pages and generates witty roasts using AI. Built with FastAPI backend and React frontend.

## Features

- **YC Company Scraping**: Automatically discovers companies from Y Combinator's directory
- **Custom URL Support**: Roast any website by providing custom URLs
- **Browser Automation**: Uses Browserbase + Playwright for reliable web scraping
- **AI Roasting**: Generates witty, constructive roasts using Grok AI
- **Real-time Updates**: WebSocket streaming for live progress updates
- **Screenshot Capture**: Takes screenshots of each landing page
- **Real-time Processing**: Live scraping and AI generation

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+

### One-Command Setup

```bash
# 1. Clone and setup
git clone <your-repo>
cd startup-roast-bot

# 2. Configure API keys
cp .env.example .env
# Edit .env with your actual API keys

# 3. Install dependencies
pip install -r app/requirements.txt
cd ui && npm install && cd ..

# 4. Start everything
./start.sh
```

That's it! The app will be running at http://localhost:5173

### Debug Mode

If something goes wrong:

```bash
./debug.sh  # Check what's missing
```

### Manual Mode (if needed)

```bash
# Backend only
source venv/bin/activate
uvicorn app.main:app --reload --port 5000

# Frontend only (in another terminal)
cd ui && npm run dev
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Backend - Required for real API usage
BROWSERBASE_API_KEY=your_browserbase_api_key_here
BROWSERBASE_PROJECT_ID=your_browserbase_project_id_here
GROK_API_KEY=your_grok_api_key_here
GROK_MODEL=grok-2
GROK_BASE_URL=https://api.x.ai/v1
```

### Frontend Environment

Create a `.env` file in the `ui/` directory:

```env
VITE_API_BASE=http://localhost:5000
```

## Usage

1. **Start the backend**: `uvicorn app.main:app --reload --port 5000`
2. **Start the frontend**: `cd ui && npm run dev`
3. **Open browser**: Navigate to `http://localhost:5173`
4. **Configure your roast**:
   - Choose source: YC Companies or Custom URLs
   - Set batch filter (for YC) or add custom URLs
   - Select roast style: Spicy, Kind, or Deadpan
5. **Click "Roast Landing Pages"** and watch the magic happen!

## API Endpoints

- `POST /run` - Start a new roast session
- `GET /runs/{id}` - Get results for a specific run
- `WS /stream/{id}` - WebSocket stream for real-time updates
- `GET /health` - Health check
- `GET /ready` - Readiness check

## Deployment

### Cerebrium

1. Set up your Cerebrium account
2. Configure secrets in the Cerebrium dashboard
3. Deploy: `cerebrium deploy`

### Docker

```bash
docker build -t startup-roast-bot .
docker run -p 5000:5000 startup-roast-bot
```

## Development

### Required API Keys

This application requires real API keys to function:
1. **Browserbase**: Get an API key and project ID from [browserbase.com](https://browserbase.com)
2. **Grok**: Get an API key from [x.ai](https://x.ai)

### Screenshots

Screenshots are automatically converted to base64 data URLs and embedded directly in the response, making them immediately viewable in the frontend without requiring external storage.

## Architecture

- **Backend**: FastAPI with WebSocket support
- **Frontend**: React + Vite + Tailwind CSS
- **Browser Automation**: Playwright via Browserbase
- **AI**: Grok API for roast generation
- **Storage**: Base64 data URLs for immediate screenshot display
- **Deployment**: Cerebrium for serverless backend

## License

MIT