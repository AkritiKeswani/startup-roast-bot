# Startup Roast Bot

**Showcasing Cerebrium's Platform Capabilities** - AI-powered startup website analyzer and roaster.

## Why Cerebrium?

This project demonstrates Cerebrium's unique capabilities:

- **Custom Runtime with WebSocket Support** - Real-time streaming of results
- **Built-in Storage** - No need for external AWS S3 or complex storage setup
- **AI Model Hosting** - Can host and scale AI models directly on Cerebrium
- **Serverless Scaling** - Handles multiple concurrent scraping sessions
- **Long-running Tasks** - Perfect for 30-90 second scraping workflows
- **Global CDN** - Fast delivery of screenshots and artifacts

## Architecture

This project implements a complete scraping and analysis pipeline:

1. **YC Directory Scraping** → Extract company profile URLs from https://www.ycombinator.com/companies
2. **YC Profile Analysis** → Extract actual website URLs from each company's YC profile  
3. **Website Analysis** → Visit each website, take screenshots, extract page data
4. **AI Roasting** → Generate witty roasts using Grok LLM based on landing page analysis

## Tech Stack

- **Backend**: FastAPI + **Cerebrium** (custom runtime with WebSocket support)
- **Browser Automation**: Browserbase + Playwright (CDP)
- **AI**: Grok LLM for roast generation
- **Storage**: **Cerebrium's built-in storage** (no AWS needed!)
- **Frontend**: Vite + React + Tailwind CSS

## Quick Start

### 1. Environment Setup

Copy the example environment file and fill in your API keys:

```bash
cp env.example .env
```

Required environment variables:
- `BROWSERBASE_API_KEY` - Get from [Browserbase](https://browserbase.com)
- `GROK_API_KEY` - Get from [x.ai](https://x.ai)
- `S3_BUCKET` - Your AWS S3 bucket name
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key

### 2. Test Core Scraping Flow

Test the scraping pipeline locally:

```bash
# Install dependencies
pip install -r app/requirements.txt
python -m playwright install chromium

# Run the test script
python test_scraping.py
```

This will test:
- YC directory scraping (3 companies)
- Website URL extraction from YC profiles
- Website data extraction and screenshots
- Grok roast generation

### 3. Run Backend Locally

```bash
cd app
uvicorn main:app --host 0.0.0.0 --port 5000
```

### 4. Run Frontend

```bash
cd ui
npm install
npm run dev
```

Visit `http://localhost:3000` to use the UI.

## API Endpoints

- `POST /run` - Start a new roast run
- `GET /runs/{run_id}` - Get run status and results
- `WS /stream/{run_id}` - WebSocket for real-time updates
- `GET /health` - Health check
- `GET /ready` - Ready check

## Deployment

### Deploy to Cerebrium

1. Install Cerebrium CLI:
```bash
pip install cerebrium
```

2. Deploy:
```bash
cerebrium deploy
```

3. Set environment variables in Cerebrium dashboard

4. Update frontend `VITE_API_BASE` to your Cerebrium URL

## Project Structure

```
startup-roast-bot/
├── app/                    # FastAPI backend
│   ├── main.py            # Main FastAPI app with WebSocket
│   ├── yc_scraper.py      # YC directory scraping
│   ├── browserbase_client.py # Browserbase integration
│   ├── playwright_bridge.py  # Playwright operations
│   ├── llm_client.py      # Grok LLM client
│   ├── storage.py         # S3 storage
│   └── models.py          # Pydantic models
├── ui/                    # Vite + React frontend
├── test_scraping.py       # Test script
├── Dockerfile            # Container config
├── cerebrium.toml        # Cerebrium deployment config
└── README.md
```

## Testing the Flow

The core scraping flow works as follows:

1. **YC Directory** (https://www.ycombinator.com/companies)
   - Scrapes company profile URLs like `/companies/company-name`
   - Optionally filters by batch (F25, S24, etc.)

2. **YC Profile Pages** (https://www.ycombinator.com/companies/company-name)
   - Extracts the actual website URL from each company's profile
   - Handles various link patterns and UI layouts

3. **Company Websites** (actual startup websites)
   - Takes viewport screenshots
   - Extracts page title, hero text, and CTA button text
   - Saves artifacts to S3

4. **AI Analysis**
   - Sends page summary to Grok LLM
   - Generates witty, constructive roasts
   - Focuses on landing page UX/copy issues

## Troubleshooting

### Common Issues

1. **Browserbase Connection Failed**
   - Check your `BROWSERBASE_API_KEY`
   - Ensure you have an active Browserbase account

2. **Grok API Errors**
   - Verify your `GROK_API_KEY` is valid
   - Check rate limits and usage

3. **S3 Upload Failed**
   - Verify AWS credentials and bucket permissions
   - Ensure the S3 bucket exists

4. **YC Scraping Issues**
   - YC may have changed their UI structure
   - Check the selectors in `yc_scraper.py`
   - Consider adding delays for rate limiting

### Debug Mode

Enable debug logging by setting the log level in your environment:

```bash
export LOG_LEVEL=DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the scraping flow
5. Submit a pull request

## License

MIT License - see LICENSE file for details.