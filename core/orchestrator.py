import json
from agents.retrieval_agent import RetrievalAgent
from agents.ontology_agent import OntologyAgent
from agents.scoring_agent import ScoringAgent


class AgentOrchestrator:
    def __init__(self):
        print("🚀 Initializing agents...")
        self.retrieval_agent = RetrievalAgent()
        self.ontology_agent  = OntologyAgent()
        self.scoring_agent   = ScoringAgent()

        with open("data/questions.json", encoding="utf-8") as f:
            data = json.load(f)
        self.questions = {q["question_id"]: q for q in data["questions"]}
        print("✅ All agents ready.")

    def get_question_list(self) -> list[dict]:
        return [
            {
                "id":   qid,
                "text": q["question_text"],
                "era":  q["era"],
            }
            for qid, q in self.questions.items()
        ]

    def run(self, question_id: str, student_answer: str) -> dict:
        if not student_answer.strip():
            return {"error": "පිළිතුර හිස් ය. කරුණාකර පිළිතුරක් ඇතුළත් කරන්න."}

        question = self.questions.get(question_id)
        if not question:
            return {"error": f"ප්‍රශ්නය '{question_id}' හමු නොවීය."}

        # ── Agent 1: Retrieval ──────────────────────────────────
        retrieved_chunks  = self.retrieval_agent.retrieve(
            question["question_text"], student_answer
        )
        retrieved_context = self.retrieval_agent.format_for_prompt(retrieved_chunks)

        # ── Agent 2: Ontology ───────────────────────────────────
        concepts      = self.ontology_agent.check_concepts(student_answer)
        ontology_text = self.ontology_agent.format_for_prompt(concepts)
        era_warnings  = self.ontology_agent.detect_era_mismatches(
            concepts, question["era"]
        )

        # ── Agent 3: Scoring + Explanation (single LLM call) ────
        score_result  = self.scoring_agent.score(
            question,
            student_answer,
            retrieved_context,
            ontology_text,
            era_warnings,
        )

        return {
            "question_id":       question_id,
            "question_text":     question["question_text"],
            "student_answer":    student_answer,
            "criteria_scores":   score_result.get("criteria_scores", []),
            "total":             score_result.get("total", 0),
            "total_marks":       question["total_marks"],
            "overall_comment":   score_result.get("overall_comment", ""),
            "explanation":       score_result.get("explanation", ""),
            "retrieved_chunks":  retrieved_chunks,
            "ontology_concepts": concepts,
            "era_warnings":      era_warnings,
        }