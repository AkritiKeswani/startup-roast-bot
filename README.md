# 🔥 Startup Roast Bot

An AI-powered agent that roasts startup landing pages using Browserbase + Playwright + Grok, deployed on Cerebrium.

## 🚀 Quick Demo

1. **YC Mode**: Scrapes YC directory (optionally filter by batch like "F25") → visits each company's website → generates witty roasts
2. **Custom Mode**: Enter any URLs → get instant landing page critiques
3. **Real-time**: WebSocket streaming shows results as they're processed
4. **Screenshots**: Each roast includes a screenshot of the landing page

## 🏗️ Architecture

```
Frontend (Vite + React + Tailwind) 
    ↓ HTTP/WebSocket
Cerebrium FastAPI Backend
    ↓ CDP
Browserbase + Playwright
    ↓ HTTP
Grok API (X.AI)
    ↓ S3
AWS S3 (screenshots + traces)
```

## 🛠️ Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Browserbase account
- Grok API access (X.AI)
- AWS S3 bucket (optional for local dev)

### Backend Setup

1. **Clone and setup**:
   ```bash
   git clone <repo>
   cd startup-roast-bot
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install -r app/requirements.txt
   python -m playwright install --with-deps chromium
   ```

3. **Environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Run locally**:
   ```bash
   cd app
   uvicorn main:app --host 0.0.0.0 --port 5000 --reload
   ```

### Frontend Setup

1. **Install and run**:
   ```bash
   cd ui
   npm install
   npm run dev
   ```

2. **Environment**:
   ```bash
   cp env.local.example .env.local
   # Set VITE_API_BASE=http://localhost:5000
   ```

## 🚀 Cerebrium Deployment

### 1. Install Cerebrium CLI

```bash
pip install cerebrium
```

### 2. Configure Environment

Set these environment variables in Cerebrium dashboard:
- `BROWSERBASE_API_KEY`
- `BROWSERBASE_PROJECT_ID` 
- `GROK_API_KEY`
- `S3_BUCKET`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### 3. Deploy

```bash
cerebrium deploy
```

### 4. Update Frontend

Set `VITE_API_BASE` to your Cerebrium URL:
```bash
# In ui/.env.local
VITE_API_BASE=https://your-deployment.cerebrium.app
```

## 📋 API Endpoints

### POST /run
Start a new roast run.

**Request**:
```json
{
  "source": "yc" | "custom",
  "yc": { "batch": "F25", "limit": 24 },
  "custom": { "urls": ["https://example.com"] },
  "style": "spicy" | "kind" | "deadpan",
  "max_steps": 6
}
```

**Response**:
```json
{
  "run_id": "uuid",
  "status": "running", 
  "stream_url": "/stream/{run_id}"
}
```

### GET /runs/{run_id}
Get final results for a completed run.

### WebSocket /stream/{run_id}
Real-time updates as companies are processed:

```json
{
  "company": {"name": "Acme", "website": "https://acme.com"},
  "roast": "Your hero says 'AI' but your CTA says 'Get Started'...",
  "screenshot_url": "https://s3.../screenshot.png",
  "status": "done"
}
```

## 🎯 Features

- **YC Integration**: Scrapes YC directory with batch filtering
- **Smart Extraction**: DOM-first extraction of title, hero, CTA
- **AI Roasts**: Grok-powered witty critiques (3 tone styles)
- **Real-time UI**: WebSocket streaming with live updates
- **Screenshots**: Viewport screenshots for each landing page
- **Error Handling**: Graceful failures with detailed logging
- **Scalable**: Cerebrium's serverless architecture

## 🔧 Configuration

### Roast Styles

- **Spicy** 🌶️: Playful jabs with edge
- **Kind** 😊: Gentle, encouraging feedback  
- **Deadpan** 😐: Dry, minimal, ironic

### YC Batch Filtering

Supports YC batch codes like:
- `F25` (Fall 2025)
- `S24` (Summer 2024)
- `W24` (Winter 2024)

## 🐛 Troubleshooting

### Common Issues

1. **Browserbase connection fails**:
   - Check `BROWSERBASE_API_KEY` and `BROWSERBASE_PROJECT_ID`
   - Verify project has active sessions

2. **Grok API errors**:
   - Verify `GROK_API_KEY` is valid
   - Check rate limits and quotas

3. **S3 upload fails**:
   - Verify AWS credentials and bucket permissions
   - App falls back to data URLs for local dev

4. **WebSocket disconnects**:
   - Check Cerebrium deployment logs
   - Verify CORS settings

### Logs

Backend logs are available in Cerebrium dashboard. Frontend logs appear in browser console and the logs panel.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally and on Cerebrium
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [Cerebrium](https://cerebrium.ai) for serverless ML hosting
- [Browserbase](https://browserbase.com) for browser automation
- [X.AI](https://x.ai) for Grok API
- [Playwright](https://playwright.dev) for web automation