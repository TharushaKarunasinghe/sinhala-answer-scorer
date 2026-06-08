from core.ollama_client import generate_explanation


class ExplanationAgent:
    def explain(
        self,
        question: dict,
        student_answer: str,
        score_result: dict,
        retrieved_context: str,
        ontology_concepts: str,
    ) -> str:

        breakdown = ""
        for cs in score_result.get("criteria_scores", []):
            breakdown += (
                f"  {cs['id']}: {cs.get('awarded',0)}/{cs.get('max',0)} — "
                f"{cs.get('reason','')[:80]}\n"
            )

        prompt = f"""ශිෂ්‍ය පිළිතුරේ ලකුණු ලැබීමේ හේතු සිංහල භාෂාවෙන් පැහැදිලි කරන්න.

ප්‍රශ්නය: {question['question_text'][:150]}
ශිෂ්‍ය පිළිතුර: {student_answer[:300]}

ලකුණු විස්තරය:
{breakdown}
සම්පූර්ණ: {score_result.get('total',0)}/{question['total_marks']}

සාක්ෂි: {retrieved_context[:200]}

1. නිවැරදි කරුණු (ලකුණු ලැබුණු ස්ථාන)
2. වැඩිදියුණු කළ යුතු කරුණු
3. සාරාංශය"""

        return generate_explanation(prompt)