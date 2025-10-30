import os, requests, json

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def refine_prompt_and_captions(topic: str, style: str) -> dict:
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("LLAMA_MODEL", "meta-llama/llama-3.1-70b-instruct")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    messages = [{
        "role": "user",
        "content": (
            "You are a bilingual marketing assistant. Return JSON only.\n"
            "Keys: prompt, caption_en, caption_ht, caption_es.\n"
            f"Topic: {topic}\nStyle: {style}\n"
            "Constraints:\n- image prompt: 1–2 sentences, brand-safe, no trademark misuse\n"
            "- each caption 120–180 chars, 1 CTA, 2–3 hashtags; upbeat tone"
        )
    }]
    body = {"model": model, "messages": messages, "response_format": {"type": "json_object"}}
    r = requests.post(OPENROUTER_URL, headers=headers, json=body, timeout=60)
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    obj = json.loads(content)
    return {
        "prompt": obj.get("prompt", f"{topic}, {style}, clean marketing visual"),
        "caption_en": obj.get("caption_en", f"{topic} — learn more today. #promo #marketing"),
        "caption_ht": obj.get("caption_ht", f"{topic} — Jwenn plis jodi a. #promo #maketing"),
        "caption_es": obj.get("caption_es", f"{topic} — Conoce más hoy. #promoción #marketing"),
    }
