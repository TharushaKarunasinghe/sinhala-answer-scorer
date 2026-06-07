import json
from agents.retrieval_agent import RetrievalAgent
from agents.ontology_agent import OntologyAgent
from agents.scoring_agent import ScoringAgent
from agents.explanation_agent import ExplanationAgent

# Load a question
with open("data/questions.json", encoding="utf-8") as f:
    questions = {q["question_id"]: q for q in json.load(f)["questions"]}

question = questions["Q3"]  # Dutch era question

# Test answer (medium quality)
student_answer = """ලන්දේසීන් ශ්‍රී ලංකාවේ VOC සමාගම හරහා කුරුඳු වෙළඳාම පාලනය කළහ.
රෝම-ලන්දේසි නීතිය හඳුන්වා දෙන ලදී. බර්ගර් ප්‍රජාව ද බිහි විය."""

print("🔍 Step 1: Retrieving context...")
retrieval_agent = RetrievalAgent()
chunks = retrieval_agent.retrieve(question["question_text"], student_answer)
retrieved_context = retrieval_agent.format_for_prompt(chunks)
print(f"  Retrieved {len(chunks)} chunks")

print("\n🧠 Step 2: Checking ontology concepts...")
ontology_agent = OntologyAgent()
concepts = ontology_agent.check_concepts(student_answer)
ontology_text = ontology_agent.format_for_prompt(concepts)
era_warnings = ontology_agent.detect_era_mismatches(concepts, question["era"])
print(f"  Found {len(concepts)} concepts")

print("\n📊 Step 3: Scoring...")
scoring_agent = ScoringAgent()
result = scoring_agent.score(
    question, student_answer,
    retrieved_context, ontology_text, era_warnings
)
print(f"  Total: {result['total']}/{question['total_marks']}")
for cs in result["criteria_scores"]:
    print(f"  [{cs['id']}] {cs['awarded']}/{cs['max']} — {cs['reason'][:60]}...")

print("\n💬 Step 4: Generating explanation...")
explanation_agent = ExplanationAgent()
explanation = explanation_agent.explain(
    question, student_answer,
    result, retrieved_context, ontology_text
)
print("\n" + explanation[:500] + "...")