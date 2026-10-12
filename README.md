# Smart German Grammar Bot

A web-based German grammar tutor powered by a large language model. Chat freely about grammar, vocabulary, and cases, or start a guided drill such as an *der / die / das* quiz with instant feedback.

**Live demo:** https://smart-german-grammar-bot.onrender.com

> The demo runs on a free-tier host that sleeps after inactivity. The first load may take 30 to 60 seconds.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## Features

- **Free chat mode:** ask anything about German grammar, vocabulary, or usage.
- **Guided drill modes:** structured practice for:
  - Noun articles (`der / die / das`)
  - The four cases: Nominativ, Akkusativ, Dativ, Genitiv
  - Vocabulary building
- **Streaming responses:** answers appear word by word as they are generated.
- **Session memory:** the bot remembers the current conversation.
- **Automatic model fallback:** if a free model is retired or rate-limited, the bot switches to another free model.
- **Welcome screen:** suggested prompts to start a conversation with one click.
- **Article highlighting:** `der`, `die`, and `das` are color-coded in the bot's replies.
- **Custom web interface:** dark theme, responsive layout, no frontend framework.
- **Server-side secrets:** API keys stay on the server and are never exposed to the browser.

---

## Tech Stack

| Layer      | Technology                                      |
|------------|-------------------------------------------------|
| Backend    | Python 3.12+, FastAPI, Uvicorn                  |
| AI model   | LLM via OpenRouter (OpenAI-compatible API)      |
| Frontend   | Vanilla HTML, CSS, and JavaScript (SSE streaming) |
| Config     | python-dotenv                                   |
| Testing    | Plain Python (pytest-compatible)                |
| Deployment | Render (free tier), auto-deploy on `git push`   |

---

## Project Structure

```text
smart-german-grammar-bot/
├── config/
│   └── settings.py        # Settings loaded from .env
├── src/
│   ├── api/               # FastAPI routes and SSE streaming
│   ├── bot/               # Prompts and drill logic
│   ├── models/            # Domain models (GermanNoun, ChatSession, ...)
│   ├── services/          # LLM client and grammar service
│   ├── utils/             # Shared logger
│   └── static/            # HTML, CSS, and JS chat UI
├── tests/                 # Unit tests
├── scripts/               # One-off dev scripts
├── data/                  # Runtime data (gitignored)
├── logs/                  # Log files (gitignored)
├── .env.example           # Template for environment variables
├── main.py                # Entry point
├── render.yaml            # Render deployment config
├── pyproject.toml
└── README.md
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/MedDhiaHasni/Smart-German-Grammar-Bot.git
cd Smart-German-Grammar-Bot
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -e .
```

### 4. Configure environment variables

Copy the template and add your API key:

```bash
cp .env.example .env
```

Then edit `.env`:

```dotenv
DEEPSEEK_API_KEY=your_openrouter_key_here
DEEPSEEK_BASE_URL=https://openrouter.ai/api/v1
DEEPSEEK_MODEL=openrouter/free
```

A free API key can be created at [openrouter.ai/keys](https://openrouter.ai/keys). See [Configuration](#configuration) for details on each variable.

### 5. Run the application

```bash
python main.py
```

Open http://localhost:8000 in your browser.

---

## Configuration

| Variable            | Description                                                        |
|---------------------|--------------------------------------------------------------------|
| `DEEPSEEK_API_KEY`  | OpenRouter API key (starts with `sk-or-`)                          |
| `DEEPSEEK_BASE_URL` | API base URL. Use `https://openrouter.ai/api/v1`                   |
| `DEEPSEEK_MODEL`    | Model identifier. Use `openrouter/free` to route to a free model   |

The variable names retain the `DEEPSEEK_` prefix for historical reasons. They apply to any OpenAI-compatible provider, including OpenRouter.

**About the model setting.** `openrouter/free` routes each request to an available free model. Free models are retired regularly, so a router avoids breakage when a specific model disappears. The client also falls back to other free models automatically if a request fails. The current catalog is available at [openrouter.ai/models?max_price=0](https://openrouter.ai/models?max_price=0).

---

## Running Tests

```bash
python tests/test_models.py
```

---

## Deployment

The application is deployed on [Render](https://render.com) (free tier) and redeploys automatically on every push to `main`.

Configuration lives in `render.yaml`:

- **Build:** `pip install -e .`
- **Start:** `python main.py`
- **Environment:** `DEEPSEEK_API_KEY` is set as a secret in the Render dashboard.

**Notes**

- Free-tier services spin down after 15 minutes of inactivity. The first request after that takes 30 to 60 seconds to wake the server.
- Environment variables set in the Render dashboard override the values in `render.yaml`. To change the model, update `DEEPSEEK_MODEL` in the dashboard's **Environment** tab.

---

## Roadmap

**Completed**

- [x] Project skeleton and configuration
- [x] Domain models (German nouns, cases, chat sessions)
- [x] Streaming LLM client
- [x] Prompt engineering and grammar service
- [x] FastAPI backend with SSE streaming
- [x] Custom web chat UI
- [x] Deployment on Render (free tier)
- [x] Automatic fallback between free models

**Planned**

- [ ] Persistent sessions (survive restarts)
- [ ] Spaced repetition and progress tracking
- [ ] Pronunciation support (browser text-to-speech)
- [ ] User accounts and saved history

---

## Contributing

This is a personal learning project, but suggestions and issues are welcome. Feel free to open an issue or submit a pull request.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Author

**Med Dhia Hasni**
Full Stack Developer

[GitHub](https://github.com/MedDhiaHasni)
