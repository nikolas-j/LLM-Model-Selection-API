# Smart Model Selection API

An smart LLM routing system that automatically classifies prompt complexity and selects the most cost-effective model, reducing API costs by up to 40-80% while maintaining response quality. Built with FastAPI and designed for easy integration into existing production workflows.

![App Screenshot](screenshot\smart_model_select.png)

## Purpose

LLM API costs can quickly spiral out of control when using premium models for every request. This tool solves that by:

- **Automatic Classification**: Uses GPT-5-nano to instantly classify prompts as low/medium/high complexity
- **Smart Routing**: Routes simple queries to nano, moderate to mini, complex to GPT-5
- **Confidence Thresholds**: Upgrades model selection when classifier confidence is low
- **Real-time Savings**: Track cost savings per 1M tokens vs. using only GPT-5
- **Production Ready**: Rate limiting, CORS support, Docker deployment

## Cost Savings

The classifier adds ~2-8 seconds of extra latency but delivers significant savings:

- **Low complexity prompts** → gpt-5-nano ($0.05/$0.40 per 1M tokens)
- **Medium complexity** → gpt-5-mini ($0.25/$0.60 per 1M tokens)  
- **High complexity** → gpt-5 ($1.25/$10.00 per 1M tokens)

(prices in 22.12.2025)

**Example**: On a typical workload with 60% low, 30% medium, 10% high complexity prompts, you save **~75% on costs** compared to using GPT-5 for everything.

## Easy Integration

Drop this into any existing LLM application:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/select-model",
    json={"prompt": "Your user's prompt here"}
)

result = response.json()
# Returns: model, complexity, confidence, classification_latency, output
```

The API handles everything: classification, model selection, execution, and response.

## 📊 Features

- **FastAPI Backend**: High-performance async API with automatic OpenAPI docs
- **Streamlit Dashboard**: Real-time visualization of model usage and cost savings
- **Rate Limiting**: Built-in protection with configurable limits (SlowAPI)
- **Token Tracking**: Estimates and tracks input/output tokens per model
- **Sticky Savings Panel**: Always-visible cost metrics that follow you as you scroll
- **Docker Ready**: One-command deployment with docker-compose

## 🛠️ Tech Stack

- **Backend**: FastAPI, OpenAI SDK
- **Frontend**: Streamlit (optional dashboard)
- **Deployment**: Docker, uv package manager
- **Models**: OpenAI GPT-5-nano/mini/5

## Quick Start

### Prerequisites

- Docker Desktop installed and running
- OpenAI API key
- Python 3.11+

### 1. Configure Environment

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here

```

### 2. Run with Docker

```bash
# Start backend API (port 8000)
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

The API is now available at `http://localhost:8000`

### 3. Run Streamlit Dashboard (Optional)

```bash
# Install UI dependencies
uv sync --extra ui

# Run dashboard
uv run streamlit run ui.py
```

Dashboard opens at `http://localhost:8501`

## API Endpoints

### POST `/api/select-model`

**Request:**
```json
{
  "prompt": "Explain quantum computing to a 5-year-old"
}
```

**Response:**
```json
{
  "output": "Quantum computers are like...",
  "model": "gpt-5-mini",
  "complexity": "medium",
  "confidence": 0.87,
  "classification_latency": 1.234
}
```

### GET `/docs`

Interactive API documentation (Swagger UI)

## Classification Logic

The system uses a two-stage process:

1. **Classification Stage**: GPT-5-nano analyzes the prompt and returns complexity + confidence
2. **Selection Stage**: Routes to appropriate model, with confidence-based upgrades

**Complexity Criteria:**
- **Low**: Simple questions, basic queries, casual requests
- **Medium**: General information, standard analysis, moderate reasoning
- **High**: Complex reasoning, critical decisions, code generation, creative work


## Security

- API keys managed via environment variables (never committed)
- CORS configuration for frontend access control
- Rate limiting to prevent abuse
- Input validation with Pydantic schemas

## License

MIT

## Contributing

This is a production-ready template. Fork it, customize the classification logic for your use case.

---

**Built for optimizing LLM API usage to save on API costs.**
