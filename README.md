# ChatGuard 🛡️

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/package%20manager-uv-orange.svg)](https://docs.astral.sh/uv/)
[![HuggingFace](https://img.shields.io/badge/model-Qwen2.5--Coder-yellow.svg)](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct)
[![TrustGuard](https://img.shields.io/badge/safety-TrustGuard-green.svg)](https://pypi.org/project/trustguard/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Gradio](https://img.shields.io/badge/UI-Gradio-orange.svg)](https://gradio.app/)

A production-ready safe LLM chatbot powered by **Qwen2.5-Coder-7B-Instruct** via the HuggingFace Inference API, with real-time output validation using **TrustGuard** and an intelligent **LLM-as-Judge** safety pipeline.

---

## 📋 Overview

ChatGuard demonstrates how to build a safe, production-grade conversational AI system. Every response the model generates is automatically validated through a 4-step pipeline before reaching the user:

```
User Input → LLM (Qwen2.5-Coder) → JSON Extraction → Schema Validation → Rules → LLM Judge → Reply or 🛑 Blocked
```

The project is designed as a learning resource and portfolio showcase covering clean architecture, safety engineering, REST APIs, and web UI development.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 LLM-as-Judge | Uses the same model to evaluate its own responses for safety |
| 🛡️ TrustGuard | 4-step validation pipeline: JSON → Schema → Rules → Judge |
| 💬 Conversation Memory | Full multi-turn chat history per session |
| 🔄 Follow-up Shortcuts | Type `more`, `yes`, `continue` to expand the last reply |
| 🌐 Gradio Web UI | Professional dark/light theme chat interface with streaming |
| ⚡ FastAPI REST API | Multi-session REST API with Swagger docs |
| 📊 Live Stats | Real-time TrustGuard validation metrics |
| 🔌 Modular Architecture | Clean separation of concerns — UI-agnostic core logic |

---

## 🏗️ Architecture

```mermaid
flowchart TD
    A([INPUT SOURCE]):::start --> B
    B[Schema Ingestion]:::ingest --> C{Format Check}:::decision
    C -->|Invalid| ERR1[Format Error]:::error
    C -->|Valid| D
    D[Sanitization]:::process --> E[Auth Validation]:::auth
    E --> F{Auth Passed?}:::decision
    F -->|Denied| ERR2[Auth Failure]:::error
    F -->|Granted| G
    G[Schema Validation]:::schema --> H{Schema Valid?}:::decision
    H -->|Warning| WARN[Warning Queue]:::warning
    H -->|Error| ERR3[Schema Error]:::error
    H -->|Pass| I
    WARN --> I
    I[Dependency Resolution]:::resolve --> J[Business Rules]:::rules
    J --> K{Rules Engine}:::decision
    K -->|Violation| ERR4[Policy Breach]:::error
    K -->|Compliant| L
    L[Integration Tests]:::test --> M[Performance Check]:::perf
    M --> N{All Checks Passed?}:::decision
    N -->|Fail| ERR5[Test Failure]:::error
    N -->|Pass| O
    O[Audit Log]:::audit --> P[Approval Gate]:::gate
    P --> Q{Approved?}:::decision
    Q -->|Rejected| ERR6[Manual Reject]:::error
    Q -->|Approved| R
    R([DEPLOYED]):::success
    ERR1 & ERR2 & ERR3 & ERR4 & ERR5 & ERR6 --> RETRY
    RETRY{Retry Policy}:::retry
    RETRY -->|Max Retries| DEAD[Dead Letter Queue]:::dead
    RETRY -->|Retry| B

    classDef start fill:#e94560,stroke:#ff6b9d,color:#fff,stroke-width:3px
    classDef success fill:#06d6a0,stroke:#00f5c4,color:#0d1b2a,stroke-width:3px
    classDef ingest fill:#1a1a6e,stroke:#4444ff,color:#aef,stroke-width:2px
    classDef process fill:#0f3460,stroke:#4fc3f7,color:#e0f7fa,stroke-width:2px
    classDef auth fill:#4a0080,stroke:#ce93d8,color:#f3e5f5,stroke-width:2px
    classDef schema fill:#003366,stroke:#64b5f6,color:#e3f2fd,stroke-width:2px
    classDef resolve fill:#004d40,stroke:#4db6ac,color:#e0f2f1,stroke-width:2px
    classDef rules fill:#1b5e20,stroke:#81c784,color:#f1f8e9,stroke-width:2px
    classDef test fill:#e65100,stroke:#ffb74d,color:#fff3e0,stroke-width:2px
    classDef perf fill:#880e4f,stroke:#f48fb1,color:#fce4ec,stroke-width:2px
    classDef audit fill:#37474f,stroke:#90a4ae,color:#eceff1,stroke-width:2px
    classDef gate fill:#f57f17,stroke:#ffd54f,color:#fff8e1,stroke-width:2px
    classDef decision fill:#263238,stroke:#78909c,color:#eceff1,stroke-width:2px
    classDef error fill:#b71c1c,stroke:#ef9a9a,color:#ffcdd2,stroke-width:2px
    classDef warning fill:#f57f17,stroke:#ffcc02,color:#fff,stroke-width:2px
    classDef retry fill:#4a148c,stroke:#ce93d8,color:#f3e5f5,stroke-width:2px
    classDef dead fill:#212121,stroke:#757575,color:#bdbdbd,stroke-width:2px
```  

## 🛡️ ChatGuard's actual pipeline:
```mermaid
flowchart TD
    A([User Input]):::start --> B
    B[LLM Response\nQwen2.5-Coder-7B]:::llm --> C

    C[Step 1 - JSON Extraction\nParse structured response]:::step1
    C --> D{Valid JSON?}:::decision
    D -->|No| ERR1[Extraction Failed\nReturn Error]:::error
    D -->|Yes| E

    E[Step 2 - Schema Validation\nPydantic GenericResponse]:::step2
    E --> F{Schema Valid?}:::decision
    F -->|No| ERR2[Schema Rejected\nReturn Error]:::error
    F -->|Yes| G

    G[Step 3 - Custom Rules\nno-op bypass blocklist]:::step3
    G --> H[Step 4 - LLM-as-Judge\nQwen2.5-Coder evaluates safety]:::step4

    H --> I{Safe?}:::decision
    I -->|Hate / Violence\nExplicit / Malware| ERR3[BLOCKED\nReturn safe fallback]:::blocked
    I -->|Code / Math\nScience / General| J([Reply Delivered to User]):::success

    classDef start fill:#4a90d9,stroke:#2c6fad,color:#fff,stroke-width:3px
    classDef llm fill:#7b4ea6,stroke:#5c3680,color:#fff,stroke-width:2px
    classDef step1 fill:#1a1a6e,stroke:#4444ff,color:#aef,stroke-width:2px
    classDef step2 fill:#004d40,stroke:#4db6ac,color:#e0f2f1,stroke-width:2px
    classDef step3 fill:#37474f,stroke:#90a4ae,color:#eceff1,stroke-width:2px
    classDef step4 fill:#4a148c,stroke:#ce93d8,color:#f3e5f5,stroke-width:2px
    classDef decision fill:#263238,stroke:#78909c,color:#eceff1,stroke-width:2px
    classDef error fill:#b71c1c,stroke:#ef9a9a,color:#ffcdd2,stroke-width:2px
    classDef blocked fill:#e65100,stroke:#ffb74d,color:#fff3e0,stroke-width:3px
    classDef success fill:#06d6a0,stroke:#00f5c4,color:#0d1b2a,stroke-width:3px
```

### Project Structure

```
ChatGuard/
├── main.py          # Terminal chat entry point
├── ui.py            # Gradio Web UI
├── api.py           # FastAPI REST API
│
├── chatbotV2.py     # Core chat logic (UI-agnostic)
├── config.py        # Centralized configuration
├── guard.py         # TrustGuard setup
├── judge.py         # LLM-as-Judge implementation
├── llm.py           # HuggingFace API client
├── memory.py        # Conversation memory
│
├── .env             # API token (never commit)
├── .env.example     # Token template
├── pyproject.toml   # Project dependencies
└── README.md
```

---

## 📦 Installation

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- HuggingFace account with API token

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/chatguard.git
cd chatguard

# 2. Install dependencies
uv sync

# 3. Configure environment
cp .env.example .env
# Edit .env and add your HuggingFace token
```

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
HF_TOKEN=hf_your_token_here
MODEL_ID=Qwen/Qwen2.5-Coder-7B-Instruct
MAX_TOKENS=500
JUDGE_MAX_TOKENS=80
```

Get your free HuggingFace token at → https://huggingface.co/settings/tokens

---

## 🚀 How to Run

### 1. Terminal (CLI)

The simplest way to chat directly in your terminal:

```bash
uv run python main.py
```

```
🤖 ChatGuard | type 'quit' to exit

You: explain what is an LSTM
Bot: An LSTM (Long Short-Term Memory) is a type of recurrent neural network...

You: more
Bot: To expand further, LSTMs use three gates to control information flow...
```

### 2. Gradio Web UI

A professional web interface with streaming, judge verdicts, and live stats:

```bash
uv add gradio
uv run python ui.py
```

Then open → http://localhost:7860

**UI Features:**
- 💬 Chat bubbles with streaming word-by-word responses
- 🛡️ Live judge verdict panel — shows `✅ APPROVED` or `🛑 BLOCKED` with reason
- 📊 Real-time session stats (total / approved / blocked / judge calls)
- ⚡ Validation pipeline panel
- 🌙 Dark / Light theme toggle
- 💬 Follow-up shortcuts reference

### 3. FastAPI REST API

A multi-session REST API with interactive Swagger docs:

```bash
uv add fastapi uvicorn
uv run uvicorn api:app --reload
```

Then open → http://localhost:8000/docs

**Available Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/stats` | TrustGuard validation stats |
| POST | `/chat` | Send a message |
| GET | `/sessions` | List all active sessions |
| GET | `/session/{id}` | Session info |
| GET | `/session/{id}/history` | Full conversation history |
| DELETE | `/session/{id}` | Delete a session |

**Example Request:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "explain what is an LSTM", "session_id": "user-1"}'
```

**Example Response:**

```json
{
  "reply": "An LSTM (Long Short-Term Memory) is a type of recurrent neural network...",
  "session_id": "user-1",
  "is_safe": true
}
```

---

## 🛡️ Safety Pipeline

ChatGuard uses a 4-step validation pipeline powered by TrustGuard:

### Step 1 — JSON Extraction
The LLM is instructed to respond in a structured JSON format. The pipeline extracts and validates the JSON before processing.

### Step 2 — Schema Validation
The extracted JSON is validated against a Pydantic schema (`GenericResponse`) which enforces required fields and value constraints:

```python
{
    "content": "...",           # string
    "sentiment": "positive",    # positive | neutral | negative
    "tone": "helpful",          # helpful | cautious
    "is_helpful": true          # boolean
}
```

### Step 3 — Custom Rules
A `no_op` rule is used to bypass TrustGuard's built-in blocklist (which produces false positives for technical terms like `die`, `kill`, `execute` in coding contexts). The LLM Judge handles all safety decisions instead.

### Step 4 — LLM-as-Judge
The same Qwen2.5-Coder model evaluates its own response for safety. It only blocks content containing:
- Hate speech or discrimination
- Violence or self-harm
- Explicit sexual content
- Real malware or exploits

Coding help, math, science, and general knowledge are always marked as **SAFE**.

---

## 🔧 Configuration

All configuration is managed through `.env` and `config.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `HF_TOKEN` | required | HuggingFace API token |
| `MODEL_ID` | `Qwen/Qwen2.5-Coder-7B-Instruct` | Model to use |
| `MAX_TOKENS` | `500` | Max tokens per response |
| `JUDGE_MAX_TOKENS` | `80` | Max tokens for judge reply |

---

## 🗺️ Roadmap

| Phase | Feature | Status |
|-------|---------|--------|
| ✅ Phase 1 | Clean modular architecture | Done |
| ✅ Phase 2 | Gradio Web UI with streaming | Done |
| ✅ Phase 3 | FastAPI REST API | Done |
| ⏳ Phase 4 | Persistent memory (SQLite) | Planned |
| ⏳ Phase 5 | Multiple judges (Ensemble) | Planned |
| ⏳ Phase 6 | Deploy on HuggingFace Spaces | Planned |

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

- 🐛 Open an issue for bugs or suggestions
- 💡 Submit a pull request with improvements
- ⭐ Star the repo if you find it useful

---

## 📄 License

MIT License — free to use, modify, and distribute.