import json
from core.ollama_client import generate_json


class ScoringAgent:
    def score(
        self,
        question: dict,
        student_answer: str,
        retrieved_context: str,
        ontology_concepts: str,
        era_warnings: list[str],
    ) -> dict:

        criteria_lines = ""
        for c in question["criteria"]:
            criteria_lines += (
                f"  {c['id']}: {c['description']} "
                f"(උපරිම ලකුණු: {c['marks']})\n"
            )

        warning_text = ""
        if era_warnings:
            warning_text = (
                "\nවැදගත්: පහත යුග දෝෂ හඳුනා ගන්නා ලදී — "
                "මෙය ලකුණු අඩු කිරීමට හේතු විය යුතුය:\n"
                + "\n".join(f"  - {w}" for w in era_warnings)
            )

        prompt = f"""ඔබ ශ්‍රී ලංකා යටත් විජිත ඉතිහාස පිළිතුරු ඇගයීමේ පද්ධතියකි.
පහත ශිෂ්‍ය පිළිතුර ලකුණු නිර්ණායක අනුව ඇගයා JSON පමණක් ලියන්න.

ප්‍රශ්නය:
{question['question_text']}

ලකුණු නිර්ණායක:
{criteria_lines}
සම්පූර්ණ ලකුණු: {question['total_marks']}

RAG සන්දර්භය:
{retrieved_context[:800]}

හඳුනාගත් ඔන්ටොලොජි සංකල්ප:
{ontology_concepts}
{warning_text}

ශිෂ්‍ය පිළිතුර:
{student_answer}

නීති:
- සෑම නිර්ණායකයක් (C1-C5) සඳහාම ලකුණු දෙන්න
- awarded <= max විය යුතුය
- reason සිංහල භාෂාවෙන් ලියන්න
- JSON පමණක් — වෙනත් පෙළ නොලියන්න

{{"criteria_scores":[{{"id":"C1","awarded":0,"max":0,"reason":""}},{{"id":"C2","awarded":0,"max":0,"reason":""}},{{"id":"C3","awarded":0,"max":0,"reason":""}},{{"id":"C4","awarded":0,"max":0,"reason":""}},{{"id":"C5","awarded":0,"max":0,"reason":""}}],"total":0,"overall_comment":""}}"""

        result = generate_json(prompt)

        if "error" in result:
            return self._fallback_score(question, result.get("raw", ""))

        # Clamp awarded marks to valid range
        criteria_map = {c["id"]: c["marks"] for c in question["criteria"]}
        for cs in result.get("criteria_scores", []):
            cs["max"] = criteria_map.get(cs["id"], cs.get("max", 0))
            cs["awarded"] = max(0, min(int(cs.get("awarded", 0)), cs["max"]))

        # Always recalculate total — never trust LLM arithmetic
        result["total"] = sum(
            cs["awarded"] for cs in result.get("criteria_scores", [])
        )

        return result

    def _fallback_score(self, question: dict, raw_response: str) -> dict:
        return {
            "criteria_scores": [
                {
                    "id":      c["id"],
                    "awarded": 0,
                    "max":     c["marks"],
                    "reason":  "ස්වයංක්‍රීය ඇගයීම අසාර්ථක විය.",
                }
                for c in question["criteria"]
            ],
            "total": 0,
            "overall_comment": f"දෝෂය: {raw_response[:200]}",
        }