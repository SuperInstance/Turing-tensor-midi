import requests
import json
import time

# ⚠️ Keep your API key private and never share it publicly
OPENROUTER_API_KEY = "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"

API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    # Optional headers (can remove if not using a website)
    "HTTP-Referer": "https://example.com",
    "X-Title": "My DeepSeek Test App",
}


def run_model(model_name: str, prompt: str, retries: int = 3):
    """Send a chat completion request to the given model, retrying on server errors."""
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 512
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
            data = response.json()

            # ✅ Successful response
            if response.status_code == 200 and "choices" in data:
                print(json.dumps(data, indent=2))
                return data["choices"][0]["message"]["content"]

            # ⚠️ Server-side error — retry
            elif response.status_code >= 500:
                print(f"⚠️ Attempt {attempt}/{retries} failed (HTTP {response.status_code}). Retrying...")
                time.sleep(2)
                continue

            # ❌ Client-side error or model unavailable
            else:
                print("❌ API Error:", json.dumps(data, indent=2))
                return None

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Network error on attempt {attempt}/{retries}: {e}")
            time.sleep(2)

    print("❌ Failed after multiple retries.")
    return None


if __name__ == "__main__":
    model = "deepseek/deepseek-chat-v3.1:free"
    prompt = "What is the meaning of life?"

    print(f"🔹 Querying {model} ...")
    answer = run_model(model, prompt)

    # 🧠 Auto-fallback to a backup model if DeepSeek fails
    if not answer:
        print("⚠️ DeepSeek endpoint failed. Falling back to Mistral...")
        answer = run_model("mistralai/mixtral-8x7b:free", prompt)

    if answer:
        print("\nAssistant:", answer)
    else:
        print("\n❌ No valid response received from any model.")
