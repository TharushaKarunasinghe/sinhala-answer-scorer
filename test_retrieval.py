from agents.retrieval_agent import RetrievalAgent

agent = RetrievalAgent()
chunks = agent.retrieve(
    'ලන්දේසි පාලනය ශ්‍රී ලංකාවේ ආර්ථිකයට කළ බලපෑම',
    'VOC සමාගම කුරුඳු වෙළඳාම පාලනය කළේය'
)
print(f'Retrieved {len(chunks)} chunks')
for c in chunks:
    print(f'  [{c["era"]}] {c["content"][:80]}...')