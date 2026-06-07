from agents.ontology_agent import OntologyAgent

agent = OntologyAgent()

answer = "VOC සමාගම කුරුඳු වෙළඳාම පාලනය කළේය. රෝම-ලන්දේසි නීතිය අදටත් ක්‍රියාත්මක වේ. බර්ගර් ප්‍රජාව බිහි විය."

concepts = agent.check_concepts(answer)
print(f"Found {len(concepts)} concepts:\n")
print(agent.format_for_prompt(concepts))

print("\n--- Era mismatch check (question is dutch era) ---")
warnings = agent.detect_era_mismatches(concepts, "dutch")
if warnings:
    for w in warnings:
        print("⚠️ ", w)
else:
    print("✅ No era mismatches found")