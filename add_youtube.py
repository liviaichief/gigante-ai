"""
Roda LOCALMENTE para indexar vídeos do YouTube no servidor em produção.
O YouTube bloqueia IPs de servidores cloud — esse script roda na sua máquina.

Uso:
    python add_youtube.py https://youtube.com/watch?v=ID "Título do vídeo"
    python add_youtube.py https://youtube.com/watch?v=ID  (título automático)
"""
import sys
import httpx
from ingest.youtube import fetch_transcript

SERVER = "https://gigante-ai-production.up.railway.app"
# Mude abaixo se tiver alterado o token admin
ADMIN_TOKEN = "mentor-an-admin"


def main():
    if len(sys.argv) < 2:
        print("Uso: python add_youtube.py <URL> [Título opcional]")
        sys.exit(1)

    url = sys.argv[1]
    custom_title = sys.argv[2] if len(sys.argv) > 2 else ""

    print(f"\nBuscando transcrição: {url}")
    try:
        doc = fetch_transcript(url)
    except ValueError as e:
        print(f"Erro: {e}")
        sys.exit(1)

    if custom_title:
        doc["title"] = custom_title

    print(f"Transcrição obtida: {len(doc['content'])} caracteres")
    print(f"Enviando para o servidor como '{doc['title']}'...")

    resp = httpx.post(
        f"{SERVER}/admin/ingest/text",
        json={"title": doc["title"], "content": doc["content"]},
        headers={"x-admin-token": ADMIN_TOKEN},
        timeout=60,
    )

    if resp.status_code == 200:
        data = resp.json()
        print(f"\n OK: '{data['source']}' indexado com {data['chunks']} chunks.")
    else:
        print(f"\nErro do servidor ({resp.status_code}): {resp.text}")


if __name__ == "__main__":
    main()
