# 🇩🇪 Smart German Grammar Bot

> A web-based German grammar tutor chatbot powered by a large language model.
> Chat freely about grammar, vocabulary, and cases — or launch guided drills
> like *der/die/das* quizzes with instant feedback.

🔗 **Live demo:** https://smart-german-grammar-bot.onrender.com

> ⏱️ *First load may take ~30–60 seconds — the free-tier host sleeps after inactivity.*

---

## ✨ Features

- 💬 **Free chat mode** — ask anything about German grammar, vocabulary, or usage
- 🎯 **Guided drill modes** — structured practice for:
  - `der / die / das` (noun articles)
  - Nominativ, Akkusativ, Dativ, Genitiv
  - Vocabulary building
- ⚡ **Streaming responses** — answers appear word-by-word, like ChatGPT
- 🧠 **Session memory** — the bot remembers the current conversation
- 🔁 **Automatic model fallback** — if a free model is retired or rate-limited, the bot switches to another free model
- 🎨 **Custom web UI** — dark-themed, modern, no framework bloat
- 🔒 **Secure by design** — API keys stay server-side, never in the browser

> 🚀 **Roadmap:** this is the foundation of what will grow into a full
> German learning bot — with spaced repetition, progress tracking,
> pronunciation, and more.

---

## 🛠️ Tech Stack

| Layer      | Technology                                       |
|------------|--------------------------------------------------|
| Backend    | Python 3.12+ · FastAPI · Uvicorn                 |
| AI Model   | LLM via OpenRouter (OpenAI-compatible API)       |
| Frontend   | Vanilla HTML · CSS · JavaScript (SSE streaming)  |
| Config     | python-dotenv                                    |
| Testing    | Plain Python (pytest-compatible)                 |
| Deployment | Render (free tier) · auto-deploy on `git push`   |

---

## 📁 Project Structure

```text
smart-german-grammar-bot/
├── config/
│   └── settings.py        # Settings loaded from .env
├── src/
│   ├── api/               # FastAPI routes + SSE streaming
│   ├── bot/               # Prompts and drill logic
│   ├── models/            # Domain models (GermanNoun, ChatSession, ...)
│   ├── services/          # LLM client + grammar service
│   ├── utils/             # Shared logger
│   └── static/            # HTML / CSS / JS chat UI
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
DEEPSEEK_API_KEY=your_openrouter_key_here
DEEPSEEK_BASE_URL=https://openrouter.ai/api/v1
DEEPSEEK_MODEL=openrouter/free
```

> 💡 **Get a free API key:** [OpenRouter](https://openrouter.ai/keys) offers free
> access to many capable models. Browse the current free catalog at
> [openrouter.ai/models?max_price=0](https://openrouter.ai/models?max_price=0).
>
> `openrouter/free` automatically routes to an available free model. Free models
> come and go, so the bot also falls back to other free models if one fails.

### 5. Run the app

```bash
python main.py
```

Then open http://localhost:8000 in your browser.

---

## 🧪 Running Tests

```bash
python tests/test_models.py
```

---

## ☁️ Deployment

The app is deployed on [Render](https://render.com) (free tier) and
auto-deploys on every push to `main`.

Configuration lives in `render.yaml`:

- **Build:** `pip install -e .`
- **Start:** `python main.py`
- **Environment:** `DEEPSEEK_API_KEY` is set as a secret in the Render dashboard

> ⚠️ **Note:** Free-tier services spin down after 15 minutes of inactivity.
> The first request after that takes 30–60 seconds to wake the server.

> ⚠️ **Note:** Environment variables set in the Render dashboard override
> `render.yaml`. If you change the model, update `DEEPSEEK_MODEL` in the
> dashboard's **Environment** tab too.

---

## 🗺️ Roadmap

- [x] Project skeleton + configuration
- [x] Domain models (German nouns, cases, chat sessions)
- [x] Streaming LLM client
- [x] Prompt engineering + grammar service
- [x] FastAPI backend with SSE streaming
- [x] Custom web chat UI
- [x] Deployed live (Render free tier)
- [x] Automatic fallback between free models
- [ ] Persistent sessions (survive restarts)
- [ ] Spaced repetition and progress tracking
- [ ] Pronunciation support (browser TTS)
- [ ] User accounts & saved history

---

## 🤝 Contributing

This is a personal learning project, but suggestions and issues are welcome.
Feel free to open an issue or submit a pull request.

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Med Dhia Hasni**
Full Stack Developer
[GitHub](https://github.com/MedDhiaHasni)
