from config.persona import SYSTEM_PROMPT


def build_prompt(
    question: str,
    chunks: list[dict],
    history: list[dict],
) -> tuple[str, str]:
    """Return (system_prompt, user_message) ready for the LLM."""

    # Context block
    if chunks:
        parts = [
            f"[Trecho {i+1}] {c['source']}\n{c['content']}"
            for i, c in enumerate(chunks)
        ]
        context = "\n\n---\n\n".join(parts)
    else:
        context = "Nenhum trecho relevante encontrado."

    # Conversation history (last 3 turns)
    if history:
        turns = [
            f"Usuário: {t['user']}\nMentor AN: {t['assistant']}"
            for t in history[-3:]
        ]
        history_text = "\n\n".join(turns)
    else:
        history_text = "Início da conversa."

    system = SYSTEM_PROMPT.format(context=context, history=history_text)
    return system, question
