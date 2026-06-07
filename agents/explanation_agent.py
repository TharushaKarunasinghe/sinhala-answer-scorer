from core.ollama_client import generate


class ExplanationAgent:
    def explain(
        self,
        question: dict,
        student_answer: str,
        score_result: dict,
        retrieved_context: str,
        ontology_concepts: str,
    ) -> str:
        """
        Generate a detailed Sinhala explanation of the score.
        Grounds the explanation in retrieved evidence and ontology concepts.
        """

        criteria_breakdown = ""
        for cs in score_result.get("criteria_scores", []):
            awarded = cs.get("awarded", 0)
            max_m   = cs.get("max", 0)
            reason  = cs.get("reason", "")
            criteria_breakdown += (
                f"  [{cs['id']}]: {awarded}/{max_m} ලකුණු — {reason}\n"
            )

        system_prompt = """ඔබ ශ්‍රී ලංකා යටත් විජිත ඉතිහාස විශේෂඥ ගුරුවරයෙකි.
ශිෂ්‍යයාට ඔවුන්ගේ ලකුණු ලැබුණු හේතු සිංහල භාෂාවෙන් පැහැදිලිව විස්තර කරන්න.
ඔබේ පැහැදිලි කිරීම දිරිගන්වන සහ ඵලදායී විය යුතුය."""

        prompt = f"""ශිෂ්‍ය පිළිතුරේ ලකුණු ලැබීමේ හේතු සිංහල භාෂාවෙන් පැහැදිලි කරන්න.

ප්‍රශ්නය: {question['question_text']}

ශිෂ්‍ය පිළිතුර: {student_answer}

ලකුණු විස්තරය:
{criteria_breakdown}
සම්පූර්ණ ලකුණු: {score_result.get('total', 0)}/{question['total_marks']}

RAG සාක්ෂි (නිවැරදි පිළිතුරේ ප්‍රධාන කරුණු):
{retrieved_context}

හඳුනාගත් ඔන්ටොලොජි සංකල්ප:
{ontology_concepts}

කරුණාකර පහත ආකෘතිය අනුව සිංහල භාෂාවෙන් පැහැදිලි කිරීමක් ලියන්න:

1. **ශිෂ්‍යයා නිවැරදිව සඳහන් කළ කරුණු** — ලකුණු ලැබුණු ස්ථාන
2. **වැඩිදියුණු කළ යුතු කරුණු** — ලකුණු අඩු වූ ස්ථාන සහ නිවැරදි තොරතුරු
3. **සාරාංශය** — සමස්ත කාර්යසාධනය පිළිබඳ දිරිගැන්වීමක්"""

        explanation = generate(prompt, system_prompt)
        return explanation