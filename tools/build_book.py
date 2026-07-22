"""Gera EPUB (pandoc) e PDF (Chrome headless) de um livro.

Uso: python tools/build_book.py amor-expresso
Requer: npm run build executado antes (usa dist/).
"""
import re
import subprocess
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CHROME_CANDIDATOS = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
]


def frontmatter(md: Path) -> dict:
    texto = md.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", texto, re.DOTALL)
    campos = dict(
        re.findall(r'^(\w+):\s*"?(.*?)"?\s*$', m.group(1), re.MULTILINE)
    )
    campos["_corpo"] = m.group(2)
    return campos


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Uso: python tools/build_book.py <slug-do-livro>")
    slug = sys.argv[1]

    livro_md = RAIZ / "src" / "content" / "livros" / f"{slug}.md"
    if not livro_md.exists():
        sys.exit(f"Livro nao encontrado: {livro_md}")
    titulo = frontmatter(livro_md)["titulo"]

    capitulos = []
    for md in sorted((RAIZ / "src" / "content" / "textos").glob("*.md")):
        fm = frontmatter(md)
        if fm.get("livro") == slug:
            capitulos.append(
                (int(fm.get("ordem", 0)), fm["titulo"], fm.get("autor"),
                 fm.get("genero"), fm["_corpo"])
            )
    capitulos.sort()
    if not capitulos:
        sys.exit(f"Nenhum texto associado ao livro '{slug}'.")

    downloads = RAIZ / "public" / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)

    # EPUB via pandoc
    # Poemas: titulo entra no sumario, mas oculto no corpo (classe .oculto do epub.css)
    juntado = "\n\n".join(
        f"# {t}" + (" {.oculto}" if genero == "poema" else "") + "\n\n"
        + (f"*{autor}*\n\n" if autor else "") + corpo
        for _, t, autor, genero, corpo in capitulos
    )
    epub = downloads / f"{slug}.epub"
    subprocess.run(
        ["pandoc", "-f", "markdown", "-o", str(epub),
         "--css", str(RAIZ / "tools" / "epub.css"),
         "--metadata", f"title={titulo}", "--metadata", "author=Adriana Aneli",
         "--metadata", "lang=pt-BR", "--toc"],
        input=juntado, text=True, encoding="utf-8", check=True,
    )
    print(f"EPUB: {epub}")

    # PDF via Chrome headless sobre a pagina de impressao construida.
    # Servida por HTTP local: com file:// os assets absolutos (/images/...) nao carregam.
    html = RAIZ / "dist" / "livros" / slug / "imprimir" / "index.html"
    if not html.exists():
        sys.exit("Rode 'npm run build' antes (dist/ nao contem a pagina de impressao).")
    chrome = next((c for c in CHROME_CANDIDATOS if c.exists()), None)
    if chrome is None:
        sys.exit("Chrome nao encontrado nos caminhos padrao.")
    pdf = downloads / f"{slug}.pdf"
    handler = partial(SimpleHTTPRequestHandler, directory=str(RAIZ / "dist"))
    servidor = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    porta = servidor.server_address[1]
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    try:
        subprocess.run(
            [str(chrome), "--headless", "--disable-gpu", "--no-pdf-header-footer",
             # Sem virtual time, o Chrome imprime antes de as webfonts carregarem
             # (font-display: swap) e o PDF sai na fonte de fallback (Georgia).
             "--virtual-time-budget=10000",
             f"--print-to-pdf={pdf}",
             f"http://127.0.0.1:{porta}/livros/{slug}/imprimir/"],
            check=True,
        )
    finally:
        servidor.shutdown()
    print(f"PDF: {pdf}")
    print(f"Agora adicione ao frontmatter de {livro_md.name}:")
    print(f"  pdf: /downloads/{slug}.pdf")
    print(f"  epub: /downloads/{slug}.epub")


if __name__ == "__main__":
    main()
