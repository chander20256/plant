## Plant Disease Chat Backend (OpenRouter)

### 1) Install dependencies
```bash
pip install -r requirements.txt
```

### 2) Add your API key
```bash
cp .env.example .env
```
Then edit `.env` and set:
```env
OPENROUTER_API_KEY=your_real_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
```

### 3) Run Python backend
```bash
python app.py
```
Backend runs at: `http://127.0.0.1:5000`

### 4) Run your HTML with Live Server
Run `chat.html` from VS Code Live Server (usually `http://127.0.0.1:5500/chat.html`).

The frontend calls:
- `POST http://127.0.0.1:5000/api/chat`

### Notes
- Send either text, image, or both.
- CORS is enabled so Live Server can call the backend.
- If you get auth errors, verify `.env` key and restart backend.


### Security
- Never commit your real API key. Keep it only in `.env` (ignored by git).
