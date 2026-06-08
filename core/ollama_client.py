import ollama
import json
import re

MODEL = "Tharusha_Dilhara_Jayadeera/singemma:latest"

# ── Generation parameters ──────────────────────────────────────────
DEFAULT_OPTIONS = {
    "temperature": 0.1,
    "num_predict": 500,   # ← compact JSON fits in ~400 tokens
    "num_ctx":     2048,  # ← halved from 4096
    "top_k":       10,
    "top_p":       0.9,
}

RETRY_OPTIONS = {
    "temperature": 0.1,
    "num_predict": 350,
    "num_ctx":     1536,
    "top_k":       10,
    "top_p":       0.9,
}


def generate(prompt: str, system: str = None, force_json: bool = False) -> str:
    """Generate text from singemma with retry on failure."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    kwargs = {
        "model": MODEL,
        "messages": messages,
        "options": DEFAULT_OPTIONS,
        "keep_alive": "5m",
    }
    if force_json:
        kwargs["format"] = "json"  # ← forces JSON-only output, no preamble

    # First attempt
    try:
        response = ollama.chat(**kwargs)
        return response["message"]["content"].strip()
    except Exception as e:
        print(f"⚠️ First attempt failed ({e}), retrying with reduced params...")

    # Retry with smaller limits
    kwargs["options"] = RETRY_OPTIONS
    try:
        response = ollama.chat(**kwargs)
        return response["message"]["content"].strip()
    except Exception as e:
        print(f"❌ Retry also failed: {e}")
        raise TimeoutError(f"Ollama model did not respond: {e}")


def generate_json(prompt: str, system: str = None) -> dict:
    raw = generate(prompt, system, force_json=True)
    print(f"RAW RESPONSE ({len(raw)} chars):\n{raw[:500]}\n---")
    return _parse_json(raw)


def generate_explanation(prompt: str) -> str:
    return generate(prompt)


def _parse_json(raw: str) -> dict:
    # Try 1: direct parse
    try:
        return json.loads(raw)
    except Exception:
        pass

    # Try 2: strip markdown fences
    cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Try 3: extract first { ... } block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    # Try 4: regex extract criteria manually
    scores = re.findall(
        r'"id"\s*:\s*"(C\d+)".*?"awarded"\s*:\s*(\d+)'
        r'.*?"max"\s*:\s*(\d+).*?"reason"\s*:\s*"([^"]*)"',
        cleaned, re.DOTALL
    )
    if scores:
        criteria_scores = [
            {"id": s[0], "awarded": int(s[1]),
             "max": int(s[2]), "reason": s[3]}
            for s in scores
        ]
        total_match   = re.search(r'"total"\s*:\s*(\d+)', cleaned)
        comment_match = re.search(r'"overall_comment"\s*:\s*"([^"]*)"', cleaned)
        return {
            "criteria_scores": criteria_scores,
            "total": int(total_match.group(1)) if total_match
                     else sum(int(s[1]) for s in scores),
            "overall_comment": comment_match.group(1)
                     if comment_match else "ඇගයීම සම්පූර්ණ විය.",
        }

    return {"error": "JSON parse failed", "raw": raw}