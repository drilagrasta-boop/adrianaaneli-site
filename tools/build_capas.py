"""Gera as capas dos livros (PNG 600x900) via Chrome headless.

Estilo "tinta" (escolha da autora, 23/07/2026): fundo marrom-escuro (cor do
texto do site), tipografia e vinhetas creme, moldura fina.

Uso: python tools/build_capas.py
"""
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

LIVROS = [
    {
        "slug": "a-construcao-da-primavera",
        "titulo": "A construção<br/>da primavera",
        "subtitulo": "minicrônicas",
        "vinhetas": ["flor", "passaro", "folha", "inseto"],
        "tam": 64,
    },
    {
        "slug": "o-sol-da-tarde",
        "titulo": "O sol<br/>da tarde",
        "subtitulo": "poemas",
        "vinhetas": ["sol"],
        "tam": 120,
    },
    {
        "slug": "a-tamareira-da-judeia",
        "titulo": "A Tamareira<br/>da Judeia",
        "subtitulo": "poemas",
        "vinhetas": ["tamareira"],
        "tam": 130,
    },
    {
        "slug": "amor-expresso",
        "titulo": "Amor<br/>expresso",
        "subtitulo": "50 minicontos sobre o café",
        "vinhetas": ["xicara"],  # só na capa; nos separadores do site fica o grão
        "tam": 110,
    },
    {
        "slug": "tempestade-urbana",
        "titulo": "Tempestade<br/>urbana",
        "subtitulo": "poemas",
        "vinhetas": ["nuvem"],
        "tam": 120,
    },
]

MODELO = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"/>
<link rel="stylesheet" href="/node_modules/@fontsource/eb-garamond/400.css"/>
<link rel="stylesheet" href="/node_modules/@fontsource/eb-garamond/400-italic.css"/>
<link rel="stylesheet" href="/node_modules/@fontsource/eb-garamond/600.css"/>
<link rel="stylesheet" href="/node_modules/@fontsource/cormorant-garamond/600.css"/>
<style>
  html, body {{ margin: 0; padding: 0; }}
  body {{
    width: 600px; height: 900px; box-sizing: border-box;
    background: #411c1e; color: #f6ecdf;
    font-family: 'EB Garamond', Georgia, serif;
    display: flex; align-items: stretch; justify-content: stretch;
  }}
  .moldura {{
    flex: 1; margin: 30px; border: 1px solid #f6ecdf;
    outline: 1px solid rgba(246, 236, 223, 0.45); outline-offset: 6px;
    display: flex; flex-direction: column; align-items: center;
    justify-content: space-between; padding: 60px 30px 48px; text-align: center;
  }}
  .autora {{
    font-weight: 600; font-size: 26px; letter-spacing: 0.2em;
    text-transform: uppercase; color: #c9bda6;
  }}
  .miolo {{ display: flex; flex-direction: column; align-items: center; gap: 34px; }}
  h1 {{
    font-family: 'Cormorant Garamond', Georgia, serif; font-weight: 600;
    font-size: 66px; line-height: 1.12; margin: 0;
  }}
  .subtitulo {{ font-style: italic; font-size: 26px; color: #c9bda6; margin: 0; }}
  .vinhetas {{ display: flex; gap: 34px; align-items: center; justify-content: center; }}
  .vinhetas img {{ width: {tam}px; height: {tam}px; }}
  .filete {{ width: 64px; border: 0; border-top: 1px solid rgba(246, 236, 223, 0.6); margin: 0; }}
</style>
</head>
<body>
  <div class="moldura">
    <div class="autora">Adriana Aneli</div>
    <div class="miolo">
      <h1>{titulo}</h1>
      <hr class="filete"/>
      <p class="subtitulo">{subtitulo}</p>
    </div>
    <div class="vinhetas">{vinhetas}</div>
  </div>
</body>
</html>
"""


def main() -> None:
    chrome = next((c for c in CHROME_CANDIDATOS if c.exists()), None)
    if chrome is None:
        sys.exit("Chrome nao encontrado nos caminhos padrao.")

    destino = RAIZ / "public" / "images" / "capas"
    destino.mkdir(parents=True, exist_ok=True)
    temp = RAIZ / "tools" / "_capas_temp"
    temp.mkdir(exist_ok=True)

    handler = partial(SimpleHTTPRequestHandler, directory=str(RAIZ))
    servidor = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    porta = servidor.server_address[1]
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    try:
        for livro in LIVROS:
            for v in livro["vinhetas"]:
                original = (RAIZ / "public" / "images" / "vinhetas" / f"{v}.svg").read_text(encoding="utf-8")
                claro = original.replace("#6b6156", "#c9bda6")
                (temp / f"clara-{v}.svg").write_text(claro, encoding="utf-8")
            imgs = "".join(
                f'<img src="/tools/_capas_temp/clara-{v}.svg" alt=""/>'
                for v in livro["vinhetas"]
            )
            html = MODELO.format(
                titulo=livro["titulo"], subtitulo=livro["subtitulo"],
                vinhetas=imgs, tam=livro["tam"],
            )
            pagina = temp / f"{livro['slug']}.html"
            pagina.write_text(html, encoding="utf-8")
            png = destino / f"{livro['slug']}.png"
            subprocess.run(
                [str(chrome), "--headless", "--disable-gpu",
                 "--window-size=600,900", "--hide-scrollbars",
                 "--virtual-time-budget=10000",
                 f"--screenshot={png}",
                 f"http://127.0.0.1:{porta}/tools/_capas_temp/{livro['slug']}.html"],
                check=True, capture_output=True,
            )
            print(f"Capa: {png}")
    finally:
        servidor.shutdown()


if __name__ == "__main__":
    main()
