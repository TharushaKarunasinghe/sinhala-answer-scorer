import ollama
import json
import re


def generate(prompt: str, system: str = None) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = ollama.chat(
        model="qwen2.5:3b",
        messages=messages,
        options={"temperature": 0.1}
    )
    return response["message"]["content"].strip()


def generate_json(prompt: str, system: str = None) -> dict:
    raw = generate(prompt, system)

    # Strip markdown code fences if model wraps in ```json ... ```
    cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()

    # Extract first JSON object found
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"error": "JSON parse failed", "raw": raw}