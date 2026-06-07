import ollama
import json
import re

MODEL = "Tharusha_Dilhara_Jayadeera/singemma:latest"


def generate(prompt: str, system: str = None) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = ollama.chat(
        model=MODEL,
        messages=messages,
        options={"temperature": 0.1, "num_predict": 1200}
    )
    return response["message"]["content"].strip()


def generate_json(prompt: str, system: str = None) -> dict:
    raw = generate(prompt, system)

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
        r'"id"\s*:\s*"(C\d+)".*?"awarded"\s*:\s*(\d+).*?"max"\s*:\s*(\d+).*?"reason"\s*:\s*"([^"]*)"',
        cleaned, re.DOTALL
    )
    if scores:
        criteria_scores = [
            {"id": s[0], "awarded": int(s[1]), "max": int(s[2]), "reason": s[3]}
            for s in scores
        ]
        total_match = re.search(r'"total"\s*:\s*(\d+)', cleaned)
        comment_match = re.search(r'"overall_comment"\s*:\s*"([^"]*)"', cleaned)
        return {
            "criteria_scores": criteria_scores,
            "total": int(total_match.group(1)) if total_match else sum(int(s[1]) for s in scores),
            "overall_comment": comment_match.group(1) if comment_match else "ඇගයීම සම්පූර්ථ විය."
        }

    return {"error": "JSON parse failed", "raw": raw}