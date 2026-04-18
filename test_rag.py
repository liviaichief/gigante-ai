"""
Teste rápido do pipeline RAG via terminal — sem WhatsApp.

Uso:
    python test_rag.py
    python test_rag.py "Como manter disciplina nas vendas?"
"""
import sys

from rag.retriever import search
from rag.prompt_builder import build_prompt
from rag.llm_client import ask
from config.persona import FALLBACK_MESSAGE

DEFAULT_QUESTIONS = [
    "O que é necessário para ter sucesso em vendas?",
    "Como desenvolver mentalidade de crescimento?",
    "Qual a importância da disciplina no dia a dia?",
    "Como lidar com rejeição no processo de vendas?",
    "Por onde começo para mudar minha vida profissional?",
]


def run(question: str) -> None:
    print(f"\n{'═'*60}")
    print(f"PERGUNTA: {question}")
    print("─" * 60)

    chunks = search(question)

    if not chunks:
        print("FALLBACK ATIVADO — nenhum chunk acima do score mínimo.")
        print(f"\nRESPOSTA:\n{FALLBACK_MESSAGE}")
        return

    print(f"Chunks encontrados: {len(chunks)}")
    for i, c in enumerate(chunks, 1):
        print(f"  [{i}] score={c['score']} | source={c['source']}")

    system, q = build_prompt(question, chunks, history=[])
    response = ask(system, q)

    print(f"\nRESPOSTA:\n{response}")


if __name__ == "__main__":
    questions = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_QUESTIONS
    for q in questions:
        run(q)
