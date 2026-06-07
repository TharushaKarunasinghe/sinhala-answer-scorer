from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

CHROMA_DIR  = "chroma_db"
EMBED_MODEL = "nomic-embed-text"
TOP_K       = 4


class RetrievalAgent:
    def __init__(self):
        embeddings = OllamaEmbeddings(model=EMBED_MODEL)
        self.vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings,
            collection_name="colonial_sl"
        )

    def retrieve(self, question_text: str, student_answer: str) -> list[dict]:
        """
        Retrieve top-K relevant chunks for the question + answer pair.
        Returns a list of dicts with 'content', 'source', 'era'.
        """
        query = f"{question_text} {student_answer}"
        results = self.vectorstore.similarity_search(query, k=TOP_K)

        chunks = []
        for doc in results:
            chunks.append({
                "content": doc.page_content,
                "source":  doc.metadata.get("source", "unknown"),
                "era":     doc.metadata.get("era", "unknown")
            })

        return chunks

    def format_for_prompt(self, chunks: list[dict]) -> str:
        """Format retrieved chunks into a readable string for the LLM prompt."""
        if not chunks:
            return "කිසිදු අදාළ සන්දර්භයක් හමු නොවීය."

        parts = []
        for i, chunk in enumerate(chunks, 1):
            parts.append(
                f"[සන්දර්භය {i} | මූලාශ්‍රය: {chunk['era']}]\n{chunk['content']}"
            )
        return "\n\n---\n\n".join(parts)