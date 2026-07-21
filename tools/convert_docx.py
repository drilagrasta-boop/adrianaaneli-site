"""Converte .docx em Markdown com frontmatter para o site.

Uso:
  python tools/convert_docx.py texto.docx --genero poema --titulo "Título" \
      [--livro amor-expresso --ordem 3] [--data 2026-07-21]
"""
import argparse
import re
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "src" / "content" / "textos"


def slugificar(texto: str) -> str:
    s = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("docx", type=Path)
    p.add_argument("--genero", required=True, choices=["conto", "cronica", "poema"])
    p.add_argument("--titulo", required=True)
    p.add_argument("--livro")
    p.add_argument("--ordem", type=int)
    p.add_argument("--data", default=date.today().isoformat())
    args = p.parse_args()

    if not args.docx.exists():
        sys.exit(f"Arquivo nao encontrado: {args.docx}")

    corpo = subprocess.run(
        ["pandoc", str(args.docx), "-t", "markdown_strict+smart", "--wrap=none"],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout.strip()

    fm = [f'titulo: "{args.titulo}"', f"genero: {args.genero}", f"data: {args.data}"]
    if args.livro:
        fm.append(f"livro: {args.livro}")
    if args.ordem is not None:
        fm.append(f"ordem: {args.ordem}")

    slug = slugificar(args.titulo)
    saida = DESTINO / f"{slug}.md"
    saida.write_text("---\n" + "\n".join(fm) + "\n---\n" + corpo + "\n", encoding="utf-8")
    print(f"Criado: {saida}")
    print("IMPORTANTE: a autora deve conferir o texto convertido antes de publicar.")


if __name__ == "__main__":
    main()
