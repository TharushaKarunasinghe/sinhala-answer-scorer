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
                "\nයුග දෝෂ:\n"
                + "\n".join(f"  - {w}" for w in era_warnings)
            )

        # Balance between speed and accuracy — enough context for proper evaluation
        trimmed_context = retrieved_context[:500]
        trimmed_answer  = student_answer[:600]

        prompt = f"""ඔබ ශ්‍රී ලංකා යටත් විජිත ඉතිහාස පිළිතුරු ඇගයීමේ පද්ධතියකි.
පහත ශිෂ්‍ය පිළිතුර ලකුණු නිර්ණායක අනුව ඇගයා JSON ලියන්න.

ප්‍රශ්නය:
{question['question_text']}

ලකුණු නිර්ණායක:
{criteria_lines}සම්පූර්ණ ලකුණු: {question['total_marks']}

RAG සන්දර්භය:
{trimmed_context}

හඳුනාගත් සංකල්ප:
{ontology_concepts}
{warning_text}

ශිෂ්‍ය පිළිතුර:
{trimmed_answer}

නීති:
- සෑම නිර්ණායකයක් (C1-C5) සඳහාම ලකුණු දෙන්න
- ශිෂ්‍යයා නිවැරදි කරුණු සඳහන් කර ඇත්නම් ලකුණු ලබා දෙන්න
- awarded <= max විය යුතුය
- reason සිංහල භාෂාවෙන් ලියන්න

උදාහරණ JSON:
{{"criteria_scores":[{{"id":"C1","awarded":3,"max":4,"reason":"නිවැරදි කරුණු සඳහන් කර ඇත"}}],"total":3,"overall_comment":"හොඳ පිළිතුරකි","explanation":"ශිෂ්‍යයා ප්‍රධාන කරුණු සඳහන් කර ඇත"}}"""

        result = generate_json(prompt)

        if "error" in result:
            return self._fallback_score(question, result.get("raw", ""))

        criteria_map = {c["id"]: c["marks"] for c in question["criteria"]}
        for cs in result.get("criteria_scores", []):
            cs["max"]     = criteria_map.get(cs["id"], cs.get("max", 0))
            cs["awarded"] = max(0, min(int(cs.get("awarded", 0)), cs["max"]))

        result["total"] = sum(
            cs["awarded"] for cs in result.get("criteria_scores", [])
        )

        # Ensure explanation exists even if model skips it
        if not result.get("explanation"):
            reasons = [
                f"{cs['id']}: {cs.get('reason', '')}"
                for cs in result.get("criteria_scores", [])
            ]
            result["explanation"] = "\n".join(reasons)

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
            "total":           0,
            "overall_comment": f"දෝෂය: {raw_response[:150]}",
            "explanation":     "ඇගයීම අසාර්ථක විය.",
        }