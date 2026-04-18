import anthropic
from config.settings import ANTHROPIC_API_KEY

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def ask(system: str, question: str, max_tokens: int = 1024) -> str:
    """Call Claude and return the response text."""
    message = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": question}],
    )
    return message.content[0].text
