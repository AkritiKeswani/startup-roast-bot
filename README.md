# 🔥 Startup Roast Agent

> **"Anyone can write this loop in Python, but only Cerebrium lets you run 100 of them at once, reliably, with 2-second cold starts and clean teardown."**

An **AI Agent** that roasts startup websites using Cerebrium orchestration. This demonstrates how Cerebrium transforms a simple Python script into a production-grade AI agent platform.

**What makes this an AI Agent:**
- 🧠 **Reasoning** - Analyzes websites with AI vision
- 🎯 **Planning** - Decides what actions to take
- 🤖 **Acting** - Takes screenshots and generates content
- 📊 **Learning** - Adapts based on website content

## 🏗️ Architecture

This project demonstrates how Cerebrium transforms a simple Python script into a scalable, observable, multi-session agent platform:

```
Pure Python Loop ↔ Cerebrium Orchestration ↔ Production-Ready Agent
```

### Core Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Runtime** | Cerebrium Serverless Container | Persistent, autoscaling host for long-running loops |
| **Language** | Python 3.11 + FastAPI | Simple REST + WebSocket API |
| **Orchestration** | Cerebrium Platform | Handles scaling, monitoring, and reliability |
| **Storage** | Cerebrium Storage | Built-in file storage and artifact management |
| **Deployment** | cerebrium.toml | One-file configuration for everything |

## 🚀 Why Cerebrium?

### The Problem
Building production-grade AI agents is hard. You need:
- **Long-running processes** (30-90s per roast)
- **Parallel execution** (dozens of startups simultaneously)
- **Graceful shutdown** (finish browser sessions before scaling down)
- **Observability** (track every screenshot and decision)
- **Global scaling** (handle YC batch drops)

### The Solution
Cerebrium provides the orchestration layer that makes agents reliable and scalable:

| Capability | Why It Matters |
|------------|----------------|
| **Serverless containers** (not functions) | Each RoastBot needs 30-90s to open sites, take screenshots, call Gemini CU and Grok — Cerebrium keeps the container alive |
| **Parallel replicas** | Run dozens of Browserbase sessions (one per startup) in parallel with `replicas = N` |
| **Graceful shutdown** | `SIGTERM + response_grace_period` lets each Browserbase session finish before scaling down |
| **Autoscaling** | Handle YC batch drops or run close to users for low latency |
| **Observability** | Real-time monitoring and logging via Cerebrium dashboard |
| **GPU toggle** | Flip `gpu = "A10G"` for on-device vision models — no infra rebuild |

## 🛠️ Quick Start

### 1. Prerequisites

```bash
# Install Cerebrium CLI
pip install cerebrium

# Install Playwright browsers
playwright install chromium
```

### 2. Deploy to Cerebrium

**That's it! No environment variables, no API keys, no external dependencies.**

```bash
# Deploy the application
cerebrium deploy
```

### 3. Test the API

```bash
# Health check
curl "https://api.aws.us-east-1.cerebrium.ai/v4/YOUR-PROJECT-ID/startup-roast-bot/"

# Start a roast session
curl -X POST "https://api.aws.us-east-1.cerebrium.ai/v4/YOUR-PROJECT-ID/startup-roast-bot/run" \
  -H "Content-Type: application/json" \
  -d '{"startup_url": "https://example.com"}'

# Get session status
curl "https://api.aws.us-east-1.cerebrium.ai/v4/YOUR-PROJECT-ID/startup-roast-bot/runs/{session_id}"

# Stream real-time updates (WebSocket)
wscat -c "wss://api.aws.us-east-1.cerebrium.ai/v4/YOUR-PROJECT-ID/startup-roast-bot/stream/{session_id}"
```

## 📡 API Endpoints

### `POST /run`
Start a new roast session for a startup website.

**Request:**
```json
{
  "startup_url": "https://example.com",
  "roast_style": "savage",
  "focus_areas": ["design", "copy", "ux", "value_prop"]
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "status": "started",
  "message": "Roast session started successfully"
}
```

### `GET /runs/{session_id}`
Get the status and results of a specific roast session.

**Response:**
```json
{
  "id": "uuid",
  "startup_url": "https://example.com",
  "status": "completed",
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:02:30Z",
  "steps": [...],
  "final_roast": "🔥 ROAST ALERT 🔥...",
  "s3_screenshot_url": "https://bucket.s3.amazonaws.com/..."
}
```

### `WebSocket /stream/{session_id}`
Real-time updates for roast progress.

**Message Format:**
```json
{
  "type": "step",
  "step": {
    "timestamp": "2024-01-01T00:00:00Z",
    "message": "Analyzing website with Gemini...",
    "step_type": "info"
  }
}
```

## 🔄 How It Works

1. **Screenshot Capture**: Playwright + Browserbase captures the startup website
2. **Vision Analysis**: Gemini Computer Use analyzes the screenshot and identifies issues
3. **Action Planning**: Gemini determines if additional screenshots are needed
4. **Roast Generation**: Grok LLM creates engaging, constructive roast commentary
5. **Artifact Storage**: Screenshots and traces are persisted to S3
6. **Real-time Updates**: WebSocket streams progress to connected clients

## 🎯 Demo Scenarios

### Scenario 1: YC Batch Drop
When a new YC batch drops, you can instantly scale to roast 100+ startups:

```bash
# Deploy with high replica count
cerebrium deploy --replicas 50

# Batch roast multiple startups
for url in $(cat yc_batch_urls.txt); do
  curl -X POST "https://your-deployment.cerebrium.ai/run" \
    -d "{\"startup_url\": \"$url\"}"
done
```

### Scenario 2: Real-time Dashboard
Build a live dashboard that shows roasts streaming in:

```javascript
// Connect to WebSocket
const ws = new WebSocket('wss://your-deployment.cerebrium.ai/stream/session-id');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'step') {
    updateDashboard(data.step);
  }
};
```

## 🔧 Configuration

### cerebrium.toml
```toml
[project]
name = "startup-roast-bot"

[deployment]
replicas = 3
min_replicas = 1
max_replicas = 10
response_grace_period = 30
timeout = 300
memory = "2Gi"
cpu = "1"

[env]
BROWSERBASE_API_KEY = ""
GEMINI_API_KEY = ""
GROK_API_KEY = ""
AWS_S3_BUCKET = "startup-roast-screenshots"
```

## 🎨 Frontend Options

While the FastAPI backend is the main deliverable, you can add a frontend for demos:

### Option 1: Next.js + Tailwind
```bash
npx create-next-app@latest roast-dashboard
cd roast-dashboard
npm install tailwindcss
```

### Option 2: Streamlit (Python)
```python
import streamlit as st
import requests

st.title("🔥 Startup Roast Bot")
url = st.text_input("Enter startup URL")
if st.button("Start Roast"):
    response = requests.post("https://your-deployment.cerebrium.ai/run", 
                           json={"startup_url": url})
    st.json(response.json())
```

### Option 3: React + WebSocket
```jsx
function RoastDashboard() {
  const [sessions, setSessions] = useState([]);
  
  useEffect(() => {
    const ws = new WebSocket('wss://your-deployment.cerebrium.ai/stream/session-id');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setSessions(prev => [...prev, data]);
    };
  }, []);
  
  return <div>{/* Render sessions */}</div>;
}
```

## 🚀 Production Considerations

### Monitoring
- **Cerebrium Dashboard**: Real-time metrics and logs
- **S3 Artifacts**: Every screenshot and trace persisted
- **WebSocket Connections**: Track active sessions

### Scaling
- **Auto-scaling**: Handles traffic spikes automatically
- **Global Regions**: Deploy close to users for low latency
- **Resource Limits**: Configure memory/CPU based on workload

### Security
- **API Keys**: Stored securely in Cerebrium environment
- **S3 Access**: Proper IAM roles and bucket policies
- **CORS**: Configured for your frontend domain

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `cerebrium deploy`
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Cerebrium** for the orchestration platform
- **Browserbase** for cloud browser infrastructure
- **Google DeepMind** for Gemini Computer Use
- **xAI** for Grok LLM
- **Playwright** for browser automation

---

**Built with ❤️ to showcase the power of Cerebrium for production AI agents.**
