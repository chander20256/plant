from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

app = Flask(__name__)
CORS(app)


@app.get("/health")
def health() -> tuple[Any, int]:
    return jsonify({"ok": True, "model": OPENROUTER_MODEL}), 200


@app.post("/api/chat")
def chat() -> tuple[Any, int]:
    if not OPENROUTER_API_KEY:
        return (
            jsonify(
                {
                    "error": "Missing OPENROUTER_API_KEY in .env. Add key and restart backend."
                }
            ),
            500,
        )

    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    image_base64 = data.get("image_base64")
    image_mime = data.get("image_mime") or "image/jpeg"

    if not message and not image_base64:
        return jsonify({"error": "Please send text or image."}), 400

    system_prompt = (
        "You are a plant disease detection and care assistant. "
        "If image is provided, inspect visible symptoms and provide: probable issue, confidence, "
        "possible causes, immediate steps, and prevention tips. "
        "If uncertain, clearly say it and ask follow-up details. Keep response concise and practical."
    )

    user_content: list[dict[str, Any]] = []
    if message:
        user_content.append({"type": "text", "text": message})
    else:
        user_content.append(
            {
                "type": "text",
                "text": "Analyze this plant image and suggest diagnosis and treatment.",
            }
        )

    if image_base64:
        user_content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{image_mime};base64,{image_base64}",
                },
            }
        )

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.3,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5500",
        "X-Title": "Plant Disease Chat",
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        body = response.json()
        text = body["choices"][0]["message"]["content"]
        return jsonify({"reply": text}), 200
    except requests.HTTPError:
        details = ""
        try:
            details = response.text
        except Exception:
            pass
        return jsonify({"error": f"OpenRouter API error: {details}"}), 502
    except Exception as exc:
        return jsonify({"error": f"Server error: {exc}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
