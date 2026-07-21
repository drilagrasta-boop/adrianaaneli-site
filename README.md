# Site Adriana Aneli — adrianaaneli.com.br

Site literário estático (Astro) da escritora Adriana Aneli. Obra
disponibilizada gratuitamente: textos, livros (PDF/EPUB), resenhas e
fortuna literária.

## Regra inegociável
NUNCA publicar *Sol de Pirlimpim* — os direitos pertencem à editora.

## Fluxo de publicação de texto novo
1. A autora salva o .docx em `entrada-docx/`.
2. `python tools/convert_docx.py entrada-docx/arquivo.docx --genero poema --titulo "Título" [--livro slug --ordem N]`
3. **A autora confere o texto convertido** (obrigatório — versos e itálicos).
4. Se o texto pertence a um livro: `npm run build` e depois
   `python tools/build_book.py <slug>` para regenerar PDF/EPUB.
5. `git add -A && git commit && git push` → deploy automático.

## Comandos
- `npm run dev` — servidor local
- `npm run build` — build de produção
- `python tools/convert_docx.py ...` — converte Word em texto do site
- `python tools/build_book.py <slug>` — gera EPUB e PDF do livro

## Conteúdo
- `src/content/textos/` — contos, crônicas, poemas (frontmatter: titulo,
  genero, data, livro?, ordem?, aquarela?, youtube?, resumo?)
- `src/content/livros/` — livros (titulo, sinopse, ano?, capa?, ordem, pdf?, epub?)
- `src/content/resenhas/` — resenhas (titulo, obra, autorObra, data)
- `src/content/fortuna/` — fortuna literária (titulo, autor, fonte?, data)
- Aquarelas em `public/images/aquarelas/`; capas em `public/images/capas/`
