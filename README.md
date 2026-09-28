# 🇩🇪 Smart German Grammar Bot

> A web-based German grammar tutor chatbot powered by DeepSeek.
> Chat freely about grammar, vocabulary, and cases — or launch guided drills
> like *der/die/das* quizzes with instant feedback.

---

## ✨ Features

- 💬 **Free chat mode** — ask anything about German grammar, vocabulary, or usage
- 🎯 **Guided drill modes** — structured practice for:
  - `der / die / das` (noun articles)
  - Nominativ, Akkusativ, Dativ, Genitiv
  - Vocabulary building
- ⚡ **Streaming responses** — answers appear word-by-word, like ChatGPT
- 🧠 **Session memory** — the bot remembers the current conversation
- 🎨 **Custom web UI** — dark-themed, modern, no framework bloat
- 🔒 **Secure by design** — API keys stay server-side, never in the browser

> 🚀 **Roadmap:** this is the foundation of what will grow into a full
> German learning bot — with spaced repetition, progress tracking,
> pronunciation, and more.

---

## 🛠️ Tech Stack

| Layer      | Technology                            |
|------------|----------------------------------------|
| Backend    | Python 3.11+ · FastAPI · Uvicorn      |
| AI Model   | DeepSeek (`deepseek-chat`) via HTTPX  |
| Frontend   | Vanilla HTML · CSS · JavaScript (SSE) |
| Config     | python-dotenv                         |
| Testing    | Plain Python (pytest-compatible)      |

---

## 📁 Project Structure

```
smart-german-grammar-bot/
config/
    settings.py            # Settings loaded from .env
src/
    api/                    # FastAPI routes
    bot/                    # Prompts and drill logic
    models/                 # Domain models (GermanNoun, ChatSession, ...)
    services/               # DeepSeek client + grammar service
    utils/                  # Shared logger
    static/                 # HTML / CSS / JS chat UI
tests/                      # Unit tests
scripts/                    # One-off dev scripts
data/                       # Runtime data (gitignored)
logs/                       # Log files (gitignored)
.env.example                 # Template for environment variables
pyproject.toml
README.md
```


---

## 🚀 Getting Started

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

Copy the template and fill in your API key:

```bash
cp .env.example .env
```

Then edit `.env`:

```dotenv
DEEPSEEK_API_KEY=your_real_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```

> 💡 Get a free API key: OpenRouter offers free access to DeepSeek models. See the docs for details.

### 5. Run the app

```bash
python main.py
```

Then open `http://localhost:8000` in your browser.

---

## 🧪 Running Tests

```bash
python tests/test_models.py
```

---

## 🗺️ Roadmap

- [x] Project skeleton + configuration
- [x] Domain models (German nouns, cases, chat sessions)
- [x] DeepSeek streaming client
- [x] Prompt engineering + grammar service
- [x] FastAPI backend with SSE streaming
- [x] Custom web chat UI
- [ ] Deployment guide
- [ ] Spaced repetition and progress tracking
- [ ] Pronunciation support
- [ ] User accounts & saved history

---

## 🤝 Contributing

This is a personal learning project, but suggestions and issues are welcome.

---

## 📜 License

MIT License — see `LICENSE` for details (to be added).

---

## 👤 Author

**Med Dhia Hasni**
Full Stack Developer
[GitHub](https://github.com/MedDhiaHasni)
