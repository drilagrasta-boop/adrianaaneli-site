# Site Adriana Aneli — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Site estático literário em `adrianaaneli.com.br` que disponibiliza gratuitamente a obra da autora (textos, livros com download PDF/EPUB, resenhas, fortuna literária), com visual clássico literário.

**Architecture:** Astro 5 (site estático) com content collections em Markdown; conversão .docx→Markdown via pandoc; EPUB via pandoc e PDF via Chrome headless imprimindo página de impressão do próprio site; deploy automático via GitHub Actions → GitHub Pages.

**Tech Stack:** Astro 5, TypeScript (mínimo), CSS puro, @fontsource (EB Garamond + Cormorant Garamond), pandoc, Python 3.13 (scripts de conversão), GitHub Pages.

## Global Constraints

- Conteúdo do site em português brasileiro; código e nomes de arquivos em inglês (exceto slugs de conteúdo, que seguem os títulos das obras).
- Livros publicados: *Amor expresso*, *A construção da primavera*, *O Sol da Tarde*, *Tempestade urbana*, *Mitos e lendas*, *Todas as cores do amor*. **NUNCA publicar *Sol de Pirlimpim*** (direitos da editora).
- Sem anúncios, sem rastreadores. Nenhum recurso externo além de embeds do YouTube e Formspree.
- Domínio: `adrianaaneli.com.br`. Hospedagem: GitHub Pages (gratuita), conta `drilagrasta-boop`.
- Gêneros de texto: `conto`, `cronica`, `poema` (sem acento nos valores internos; exibição com acento).
- Scripts Python sempre executados com `PYTHONUTF8=1` (já configurado na máquina).
- Working dir do projeto: `C:\Users\Dr Caetano\07_PROJETOS_DO_CLAUDE\pessoal\site-adriana-aneli` (repo git já iniciado, branch `main`).
- Todo texto convertido de .docx deve ser conferido pela autora antes de ser considerado publicado (regra de fluxo).

## File Structure

```
site-adriana-aneli/
├── astro.config.mjs
├── package.json / tsconfig.json / .gitignore
├── public/
│   ├── downloads/                  # PDFs e EPUBs gerados
│   └── images/{capas,aquarelas}/   # imagens
├── src/
│   ├── content.config.ts           # schemas das coleções
│   ├── content/{textos,livros,resenhas,fortuna}/*.md
│   ├── site.config.ts              # e-mail, redes, endpoint Formspree
│   ├── layouts/Base.astro
│   ├── components/{Header,Footer,YouTubeEmbed,BookCard,TextList}.astro
│   ├── styles/global.css
│   └── pages/
│       ├── index.astro
│       ├── textos/index.astro, textos/[slug].astro
│       ├── livros/index.astro, livros/[slug]/index.astro, livros/[slug]/imprimir.astro
│       ├── resenhas/index.astro, resenhas/[slug].astro
│       ├── fortuna/index.astro, fortuna/[slug].astro
│       ├── sobre.astro
│       └── contato.astro
├── tools/
│   ├── convert_docx.py             # .docx → Markdown com frontmatter
│   └── build_book.py               # gera EPUB (pandoc) e PDF (Chrome headless)
├── docs/guia-registro-br.md        # passo a passo do domínio para a autora
└── .github/workflows/deploy.yml
```

---

### Task 1: Esqueleto Astro que compila

**Files:**
- Create: `package.json`, `astro.config.mjs`, `tsconfig.json`, `.gitignore`, `src/pages/index.astro` (provisório)

**Interfaces:**
- Produces: projeto Astro que responde a `npm run build` e `npm run dev`; `astro.config.mjs` com `site: 'https://adrianaaneli.com.br'`.

- [ ] **Step 1: Criar arquivos base**

`package.json`:
```json
{
  "name": "site-adriana-aneli",
  "type": "module",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview"
  },
  "dependencies": {
    "astro": "^5.0.0",
    "@fontsource/eb-garamond": "^5.0.0",
    "@fontsource/cormorant-garamond": "^5.0.0"
  }
}
```

`astro.config.mjs`:
```js
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://adrianaaneli.com.br',
});
```

`tsconfig.json`:
```json
{
  "extends": "astro/tsconfigs/base"
}
```

`.gitignore`:
```
node_modules/
dist/
.astro/
```

`src/pages/index.astro`:
```astro
---
---
<html lang="pt-BR">
  <head><meta charset="utf-8" /><title>Adriana Aneli</title></head>
  <body><h1>Adriana Aneli — em construção</h1></body>
</html>
```

- [ ] **Step 2: Instalar e compilar**

Run: `npm install && npm run build`
Expected: `Complete!` sem erros; pasta `dist/` criada com `index.html`.

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: esqueleto Astro inicial"
```

---

### Task 2: Content collections com conteúdo de exemplo

**Files:**
- Create: `src/content.config.ts`
- Create: `src/content/textos/exemplo-poema.md`, `src/content/textos/exemplo-cronica.md`
- Create: `src/content/livros/amor-expresso.md`
- Create: `src/content/resenhas/exemplo-resenha.md`
- Create: `src/content/fortuna/exemplo-fortuna.md`

**Interfaces:**
- Produces: coleções `textos`, `livros`, `resenhas`, `fortuna` consumíveis via `getCollection()`. Schemas exatos abaixo — todas as tasks seguintes dependem destes nomes de campos.

- [ ] **Step 1: Escrever `src/content.config.ts`**

```ts
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const textos = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/textos' }),
  schema: z.object({
    titulo: z.string(),
    genero: z.enum(['conto', 'cronica', 'poema']),
    data: z.coerce.date(),
    livro: z.string().optional(),      // slug do livro de origem
    ordem: z.number().optional(),      // posição no livro
    aquarela: z.string().optional(),   // ex.: /images/aquarelas/nome.jpg
    youtube: z.string().optional(),    // ID do vídeo, ex.: dQw4w9WgXcQ
    resumo: z.string().optional(),
  }),
});

const livros = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/livros' }),
  schema: z.object({
    titulo: z.string(),
    sinopse: z.string(),
    ano: z.number().optional(),
    capa: z.string().optional(),       // ex.: /images/capas/slug.jpg
    ordem: z.number().default(99),     // ordem na vitrine
    pdf: z.string().optional(),        // ex.: /downloads/slug.pdf
    epub: z.string().optional(),
  }),
});

const resenhas = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/resenhas' }),
  schema: z.object({
    titulo: z.string(),
    obra: z.string(),                  // obra resenhada
    autorObra: z.string(),             // autor da obra resenhada
    data: z.coerce.date(),
  }),
});

const fortuna = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/fortuna' }),
  schema: z.object({
    titulo: z.string(),
    autor: z.string(),                 // quem escreveu sobre a obra dela
    fonte: z.string().optional(),      // veículo/publicação
    data: z.coerce.date(),
  }),
});

export const collections = { textos, livros, resenhas, fortuna };
```

- [ ] **Step 2: Criar conteúdo de exemplo**

`src/content/textos/exemplo-poema.md`:
```markdown
---
titulo: "Poema de exemplo"
genero: poema
data: 2026-07-21
livro: amor-expresso
ordem: 1
youtube: "dQw4w9WgXcQ"
---
Verso primeiro do exemplo,\
verso segundo do exemplo.

Segunda estrofe começa aqui,\
e aqui termina.
```

`src/content/textos/exemplo-cronica.md`:
```markdown
---
titulo: "Crônica de exemplo"
genero: cronica
data: 2026-07-20
resumo: "Uma crônica provisória para validar o site."
---
Texto corrido de exemplo, com *itálico* preservado. Será substituído
pelo material real da autora.
```

`src/content/livros/amor-expresso.md`:
```markdown
---
titulo: "Amor expresso"
sinopse: "Sinopse provisória — será substituída pelo texto da autora."
ordem: 1
---
Apresentação do livro (texto opcional da página do livro).
```

`src/content/resenhas/exemplo-resenha.md`:
```markdown
---
titulo: "Resenha de exemplo"
obra: "Obra resenhada"
autorObra: "Autor da obra"
data: 2026-07-19
---
Corpo da resenha de exemplo.
```

`src/content/fortuna/exemplo-fortuna.md`:
```markdown
---
titulo: "Sobre a poesia de Adriana Aneli"
autor: "Crítico de exemplo"
fonte: "Jornal de exemplo"
data: 2026-07-18
---
Texto de exemplo da fortuna literária.
```

- [ ] **Step 3: Verificar que o build valida os schemas**

Run: `npm run build`
Expected: sem erros de schema. (Teste negativo rápido: mudar temporariamente `genero: poema` para `genero: soneto` deve fazer o build FALHAR com erro de enum; reverter em seguida.)

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: content collections (textos, livros, resenhas, fortuna) com exemplos"
```

---

### Task 3: Design system — layout base, header, footer, CSS global

**Files:**
- Create: `src/styles/global.css`, `src/layouts/Base.astro`, `src/components/Header.astro`, `src/components/Footer.astro`, `src/site.config.ts`

**Interfaces:**
- Produces: `Base.astro` com props `{ title: string; description?: string }`; classes CSS `.prose` (texto corrido), `.poema` (diagramação de poema), variáveis `--cor-*`; `site.config.ts` exportando `SITE` (objeto com `email`, `instagram`, `formspreeEndpoint`).

- [ ] **Step 1: Escrever `src/site.config.ts`**

```ts
export const SITE = {
  nome: 'Adriana Aneli',
  descricao: 'Escritora — contos, crônicas, poemas e livros disponíveis gratuitamente.',
  email: 'drilagrasta@gmail.com',
  instagram: '',            // preencher quando a autora informar
  formspreeEndpoint: '',    // preencher quando a conta Formspree for criada
};
```

- [ ] **Step 2: Escrever `src/styles/global.css`**

```css
@import '@fontsource/eb-garamond/400.css';
@import '@fontsource/eb-garamond/400-italic.css';
@import '@fontsource/eb-garamond/600.css';
@import '@fontsource/cormorant-garamond/500.css';
@import '@fontsource/cormorant-garamond/600.css';

:root {
  --cor-fundo: #faf6ee;        /* creme */
  --cor-papel: #fffdf8;        /* cartões */
  --cor-tinta: #2b2620;        /* texto principal */
  --cor-tinta-suave: #6b6156;  /* texto secundário */
  --cor-detalhe: #7a3b2e;      /* bordô — links e acentos */
  --cor-linha: #e4dccb;        /* bordas */
  --fonte-texto: 'EB Garamond', Georgia, serif;
  --fonte-titulo: 'Cormorant Garamond', Georgia, serif;
  --largura-leitura: 42rem;
}

* { box-sizing: border-box; }
html { font-size: 112.5%; }   /* 18px base — conforto de leitura */
body {
  margin: 0;
  background: var(--cor-fundo);
  color: var(--cor-tinta);
  font-family: var(--fonte-texto);
  line-height: 1.65;
}
h1, h2, h3 { font-family: var(--fonte-titulo); font-weight: 600; line-height: 1.15; }
h1 { font-size: 2.4rem; }
h2 { font-size: 1.6rem; }
a { color: var(--cor-detalhe); text-decoration-thickness: 1px; text-underline-offset: 3px; }
a:hover { text-decoration-thickness: 2px; }

main { max-width: var(--largura-leitura); margin: 0 auto; padding: 2rem 1.25rem 4rem; }
.wide { max-width: 64rem; }

.prose p { margin: 0 0 1em; }
.prose em { font-style: italic; }

.poema { text-align: center; }
.poema p { margin: 0 0 1.4em; }
.poema .aquarela { max-width: 100%; border-radius: 4px; margin: 0 auto 2rem; display: block; }

.meta { color: var(--cor-tinta-suave); font-size: 0.85rem; letter-spacing: 0.04em; }
.card {
  background: var(--cor-papel);
  border: 1px solid var(--cor-linha);
  border-radius: 6px;
  padding: 1.25rem;
}
.btn {
  display: inline-block;
  border: 1px solid var(--cor-detalhe);
  color: var(--cor-detalhe);
  padding: 0.5rem 1.1rem;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.95rem;
}
.btn:hover { background: var(--cor-detalhe); color: var(--cor-papel); }

@media print {
  header, footer, .no-print { display: none !important; }
  body { background: #fff; }
}
```

- [ ] **Step 3: Escrever `Header.astro`, `Footer.astro`, `Base.astro`**

`src/components/Header.astro`:
```astro
---
const links = [
  ['/textos/', 'Textos'],
  ['/livros/', 'Livros'],
  ['/resenhas/', 'Resenhas'],
  ['/fortuna/', 'Fortuna literária'],
  ['/sobre/', 'Sobre a autora'],
  ['/contato/', 'Contato'],
];
---
<header>
  <a class="marca" href="/">Adriana Aneli</a>
  <nav>{links.map(([href, label]) => <a href={href}>{label}</a>)}</nav>
</header>
<style>
  header { text-align: center; padding: 2.5rem 1rem 1.5rem; border-bottom: 1px solid var(--cor-linha); }
  .marca { font-family: var(--fonte-titulo); font-size: 2rem; color: var(--cor-tinta); text-decoration: none; display: block; margin-bottom: 0.75rem; }
  nav { display: flex; flex-wrap: wrap; justify-content: center; gap: 0.4rem 1.4rem; }
  nav a { color: var(--cor-tinta-suave); text-decoration: none; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; }
  nav a:hover { color: var(--cor-detalhe); }
</style>
```

`src/components/Footer.astro`:
```astro
---
import { SITE } from '../site.config';
---
<footer>
  <p>© Adriana Aneli — obra disponibilizada gratuitamente pela autora.</p>
  <p><a href={`mailto:${SITE.email}`}>{SITE.email}</a></p>
</footer>
<style>
  footer { border-top: 1px solid var(--cor-linha); text-align: center; padding: 2rem 1rem; color: var(--cor-tinta-suave); font-size: 0.85rem; }
</style>
```

`src/layouts/Base.astro`:
```astro
---
import '../styles/global.css';
import Header from '../components/Header.astro';
import Footer from '../components/Footer.astro';
import { SITE } from '../site.config';
interface Props { title: string; description?: string; wide?: boolean }
const { title, description = SITE.descricao, wide = false } = Astro.props;
---
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content={description} />
    <title>{title === SITE.nome ? title : `${title} — ${SITE.nome}`}</title>
  </head>
  <body>
    <Header />
    <main class:list={[{ wide }]}><slot /></main>
    <Footer />
  </body>
</html>
```

- [ ] **Step 4: Atualizar `src/pages/index.astro` provisório para usar o Base e compilar**

```astro
---
import Base from '../layouts/Base.astro';
---
<Base title="Adriana Aneli">
  <h1>Adriana Aneli</h1>
  <p>Em construção.</p>
</Base>
```

Run: `npm run build` — Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: design system clássico literário (layout base, header, footer)"
```

---

### Task 4: Seção Textos — listagem com filtro por gênero e página individual

**Files:**
- Create: `src/pages/textos/index.astro`, `src/pages/textos/[slug].astro`, `src/components/YouTubeEmbed.astro`, `src/components/TextList.astro`

**Interfaces:**
- Consumes: coleção `textos` (Task 2), `Base.astro` (Task 3).
- Produces: rotas `/textos/`, `/textos/<slug>/`; componente `YouTubeEmbed` com prop `{ id: string; titulo: string }`; `TextList` com prop `{ itens: CollectionEntry<'textos'>[] }`.

- [ ] **Step 1: Escrever `src/components/YouTubeEmbed.astro`**

```astro
---
interface Props { id: string; titulo: string }
const { id, titulo } = Astro.props;
---
<div class="video">
  <iframe
    src={`https://www.youtube-nocookie.com/embed/${id}`}
    title={titulo}
    loading="lazy"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen
  ></iframe>
</div>
<style>
  .video { position: relative; aspect-ratio: 16 / 9; margin: 2rem 0; }
  .video iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; border-radius: 6px; }
</style>
```

- [ ] **Step 2: Escrever `src/components/TextList.astro`**

```astro
---
import type { CollectionEntry } from 'astro:content';
interface Props { itens: CollectionEntry<'textos'>[] }
const { itens } = Astro.props;
const rotulo = { conto: 'Conto', cronica: 'Crônica', poema: 'Poema' } as const;
---
<ul class="lista">
  {itens.map((t) => (
    <li>
      <a href={`/textos/${t.id}/`}>{t.data.titulo}</a>
      <span class="meta"> · {rotulo[t.data.genero]}{t.data.youtube ? ' · vídeo' : ''}</span>
      {t.data.resumo && <p class="meta">{t.data.resumo}</p>}
    </li>
  ))}
</ul>
<style>
  .lista { list-style: none; padding: 0; }
  .lista li { padding: 0.9rem 0; border-bottom: 1px solid var(--cor-linha); }
  .lista a { font-family: var(--fonte-titulo); font-size: 1.25rem; }
</style>
```

- [ ] **Step 3: Escrever `src/pages/textos/index.astro`** (filtro por gênero via query estática de seções)

```astro
---
import { getCollection } from 'astro:content';
import Base from '../../layouts/Base.astro';
import TextList from '../../components/TextList.astro';
const todos = (await getCollection('textos'))
  .sort((a, b) => b.data.data.getTime() - a.data.data.getTime());
const grupos = [
  ['poema', 'Poemas'],
  ['conto', 'Contos'],
  ['cronica', 'Crônicas'],
] as const;
---
<Base title="Textos">
  <h1>Textos</h1>
  <nav class="filtro no-print">
    {grupos.map(([g, label]) => <a href={`#${g}`}>{label}</a>)}
  </nav>
  {grupos.map(([g, label]) => {
    const itens = todos.filter((t) => t.data.genero === g);
    return itens.length > 0 && (
      <section id={g}>
        <h2>{label}</h2>
        <TextList itens={itens} />
      </section>
    );
  })}
</Base>
<style>
  .filtro { display: flex; gap: 1.5rem; margin: 1rem 0 2rem; }
</style>
```

- [ ] **Step 4: Escrever `src/pages/textos/[slug].astro`** (poema com aquarela + vídeo)

```astro
---
import { getCollection, render } from 'astro:content';
import Base from '../../layouts/Base.astro';
import YouTubeEmbed from '../../components/YouTubeEmbed.astro';

export async function getStaticPaths() {
  const textos = await getCollection('textos');
  return textos.map((t) => ({ params: { slug: t.id }, props: { t } }));
}
const { t } = Astro.props;
const { Content } = await render(t);
const rotulo = { conto: 'Conto', cronica: 'Crônica', poema: 'Poema' } as const;
const ehPoema = t.data.genero === 'poema';
---
<Base title={t.data.titulo}>
  <article class:list={[ehPoema ? 'poema' : 'prose']}>
    <p class="meta">{rotulo[t.data.genero]}</p>
    <h1>{t.data.titulo}</h1>
    {t.data.aquarela && <img class="aquarela" src={t.data.aquarela} alt={`Aquarela para ${t.data.titulo}`} />}
    <Content />
    {t.data.youtube && <YouTubeEmbed id={t.data.youtube} titulo={t.data.titulo} />}
  </article>
</Base>
```

- [ ] **Step 5: Build e conferência visual**

Run: `npm run build && npm run preview` — abrir `http://localhost:4321/textos/` e `http://localhost:4321/textos/exemplo-poema/`.
Expected: listagem agrupada por gênero; página do poema centralizada com vídeo do YouTube embaixo.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: seção Textos com filtro por gênero, aquarela e vídeo"
```

---

### Task 5: Seção Livros — vitrine, página do livro com capítulos e downloads, página de impressão

**Files:**
- Create: `src/pages/livros/index.astro`, `src/pages/livros/[slug]/index.astro`, `src/pages/livros/[slug]/imprimir.astro`, `src/components/BookCard.astro`
- Create: `public/downloads/.gitkeep`, `public/images/capas/.gitkeep`, `public/images/aquarelas/.gitkeep`

**Interfaces:**
- Consumes: coleções `livros` e `textos` (campo `livro` referencia o slug do livro; `ordem` ordena capítulos).
- Produces: rotas `/livros/`, `/livros/<slug>/`, `/livros/<slug>/imprimir/` (esta última usada pelo gerador de PDF na Task 8); `BookCard` com prop `{ livro: CollectionEntry<'livros'> }`.

- [ ] **Step 1: Escrever `src/components/BookCard.astro`**

```astro
---
import type { CollectionEntry } from 'astro:content';
interface Props { livro: CollectionEntry<'livros'> }
const { livro } = Astro.props;
---
<a class="card livro" href={`/livros/${livro.id}/`}>
  {livro.data.capa
    ? <img src={livro.data.capa} alt={`Capa de ${livro.data.titulo}`} />
    : <div class="capa-vazia"><span>{livro.data.titulo}</span></div>}
  <h3>{livro.data.titulo}</h3>
  <p class="meta">{livro.data.sinopse}</p>
</a>
<style>
  .livro { display: block; text-decoration: none; color: inherit; }
  .livro img, .capa-vazia { width: 100%; aspect-ratio: 2 / 3; object-fit: cover; border-radius: 4px; }
  .capa-vazia { display: flex; align-items: center; justify-content: center; background: var(--cor-linha); font-family: var(--fonte-titulo); font-size: 1.3rem; text-align: center; padding: 1rem; }
  .livro h3 { margin: 0.75rem 0 0.25rem; }
</style>
```

- [ ] **Step 2: Escrever `src/pages/livros/index.astro`**

```astro
---
import { getCollection } from 'astro:content';
import Base from '../../layouts/Base.astro';
import BookCard from '../../components/BookCard.astro';
const livros = (await getCollection('livros'))
  .sort((a, b) => a.data.ordem - b.data.ordem);
---
<Base title="Livros" wide>
  <h1>Livros</h1>
  <p>Todos os livros estão disponíveis gratuitamente — para ler aqui no site ou baixar.</p>
  <div class="grade">{livros.map((l) => <BookCard livro={l} />)}</div>
</Base>
<style>
  .grade { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1.5rem; margin-top: 2rem; }
</style>
```

- [ ] **Step 3: Escrever `src/pages/livros/[slug]/index.astro`**

```astro
---
import { getCollection, render } from 'astro:content';
import Base from '../../../layouts/Base.astro';

export async function getStaticPaths() {
  const livros = await getCollection('livros');
  return livros.map((l) => ({ params: { slug: l.id }, props: { l } }));
}
const { l } = Astro.props;
const { Content } = await render(l);
const capitulos = (await getCollection('textos', (t) => t.data.livro === l.id))
  .sort((a, b) => (a.data.ordem ?? 0) - (b.data.ordem ?? 0));
---
<Base title={l.data.titulo}>
  <article class="prose">
    <h1>{l.data.titulo}</h1>
    {l.data.capa && <img src={l.data.capa} alt={`Capa de ${l.data.titulo}`} style="max-width: 240px; border-radius: 4px;" />}
    <p>{l.data.sinopse}</p>
    <Content />
    <p class="no-print">
      {l.data.pdf && <a class="btn" href={l.data.pdf} download>Baixar PDF</a>}{' '}
      {l.data.epub && <a class="btn" href={l.data.epub} download>Baixar EPUB</a>}
    </p>
    {capitulos.length > 0 && (
      <section>
        <h2>Ler online</h2>
        <ol>{capitulos.map((c) => <li><a href={`/textos/${c.id}/`}>{c.data.titulo}</a></li>)}</ol>
      </section>
    )}
  </article>
</Base>
```

- [ ] **Step 4: Escrever `src/pages/livros/[slug]/imprimir.astro`** (página única com o livro inteiro, para virar PDF)

```astro
---
import { getCollection, render } from 'astro:content';
import '../../../styles/global.css';

export async function getStaticPaths() {
  const livros = await getCollection('livros');
  return livros.map((l) => ({ params: { slug: l.id }, props: { l } }));
}
const { l } = Astro.props;
const capitulos = (await getCollection('textos', (t) => t.data.livro === l.id))
  .sort((a, b) => (a.data.ordem ?? 0) - (b.data.ordem ?? 0));
const renderizados = await Promise.all(
  capitulos.map(async (c) => ({ c, Content: (await render(c)).Content }))
);
---
<html lang="pt-BR">
  <head><meta charset="utf-8" /><title>{l.data.titulo} — Adriana Aneli</title></head>
  <body class="impressao">
    <section class="folha-rosto">
      <h1>{l.data.titulo}</h1>
      <p>Adriana Aneli</p>
    </section>
    {renderizados.map(({ c, Content }) => (
      <section class="capitulo" class:list={[c.data.genero === 'poema' ? 'poema' : 'prose']}>
        <h2>{c.data.titulo}</h2>
        <Content />
      </section>
    ))}
    <style>
      .impressao { max-width: 40rem; margin: 0 auto; padding: 2rem; }
      .folha-rosto { text-align: center; page-break-after: always; padding-top: 30vh; }
      .capitulo { page-break-before: always; }
    </style>
  </body>
</html>
```

- [ ] **Step 5: Build e conferência**

Run: `npm run build && npm run preview` — conferir `/livros/`, `/livros/amor-expresso/` e `/livros/amor-expresso/imprimir/`.
Expected: vitrine com cartão do livro; página do livro lista "Poema de exemplo" como capítulo; página de impressão mostra folha de rosto + capítulo.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: seção Livros com vitrine, capítulos, downloads e página de impressão"
```

---

### Task 6: Resenhas e Fortuna literária

**Files:**
- Create: `src/pages/resenhas/index.astro`, `src/pages/resenhas/[slug].astro`, `src/pages/fortuna/index.astro`, `src/pages/fortuna/[slug].astro`

**Interfaces:**
- Consumes: coleções `resenhas` e `fortuna` (Task 2), `Base.astro`.
- Produces: rotas `/resenhas/`, `/resenhas/<slug>/`, `/fortuna/`, `/fortuna/<slug>/`.

- [ ] **Step 1: Escrever as quatro páginas**

`src/pages/resenhas/index.astro`:
```astro
---
import { getCollection } from 'astro:content';
import Base from '../../layouts/Base.astro';
const resenhas = (await getCollection('resenhas'))
  .sort((a, b) => b.data.data.getTime() - a.data.data.getTime());
---
<Base title="Resenhas">
  <h1>Resenhas</h1>
  <p>Leituras críticas da autora sobre obras e escritores.</p>
  <ul class="lista">
    {resenhas.map((r) => (
      <li>
        <a href={`/resenhas/${r.id}/`}>{r.data.titulo}</a>
        <p class="meta">Sobre <em>{r.data.obra}</em>, de {r.data.autorObra}</p>
      </li>
    ))}
  </ul>
</Base>
<style>
  .lista { list-style: none; padding: 0; }
  .lista li { padding: 0.9rem 0; border-bottom: 1px solid var(--cor-linha); }
  .lista a { font-family: var(--fonte-titulo); font-size: 1.25rem; }
</style>
```

`src/pages/resenhas/[slug].astro`:
```astro
---
import { getCollection, render } from 'astro:content';
import Base from '../../layouts/Base.astro';
export async function getStaticPaths() {
  const resenhas = await getCollection('resenhas');
  return resenhas.map((r) => ({ params: { slug: r.id }, props: { r } }));
}
const { r } = Astro.props;
const { Content } = await render(r);
---
<Base title={r.data.titulo}>
  <article class="prose">
    <p class="meta">Resenha · <em>{r.data.obra}</em>, de {r.data.autorObra}</p>
    <h1>{r.data.titulo}</h1>
    <Content />
  </article>
</Base>
```

`src/pages/fortuna/index.astro`:
```astro
---
import { getCollection } from 'astro:content';
import Base from '../../layouts/Base.astro';
const itens = (await getCollection('fortuna'))
  .sort((a, b) => b.data.data.getTime() - a.data.data.getTime());
---
<Base title="Fortuna literária">
  <h1>Fortuna literária</h1>
  <p>O que já se escreveu e disse sobre a obra de Adriana Aneli.</p>
  <ul class="lista">
    {itens.map((f) => (
      <li>
        <a href={`/fortuna/${f.id}/`}>{f.data.titulo}</a>
        <p class="meta">{f.data.autor}{f.data.fonte ? ` · ${f.data.fonte}` : ''}</p>
      </li>
    ))}
  </ul>
</Base>
<style>
  .lista { list-style: none; padding: 0; }
  .lista li { padding: 0.9rem 0; border-bottom: 1px solid var(--cor-linha); }
  .lista a { font-family: var(--fonte-titulo); font-size: 1.25rem; }
</style>
```

`src/pages/fortuna/[slug].astro`:
```astro
---
import { getCollection, render } from 'astro:content';
import Base from '../../layouts/Base.astro';
export async function getStaticPaths() {
  const itens = await getCollection('fortuna');
  return itens.map((f) => ({ params: { slug: f.id }, props: { f } }));
}
const { f } = Astro.props;
const { Content } = await render(f);
---
<Base title={f.data.titulo}>
  <article class="prose">
    <p class="meta">{f.data.autor}{f.data.fonte ? ` · ${f.data.fonte}` : ''}</p>
    <h1>{f.data.titulo}</h1>
    <Content />
  </article>
</Base>
```

- [ ] **Step 2: Build**

Run: `npm run build` — Expected: PASS, rotas `/resenhas/exemplo-resenha/` e `/fortuna/exemplo-fortuna/` geradas em `dist/`.

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: seções Resenhas e Fortuna literária"
```

---

### Task 7: Início, Sobre a autora e Contato

**Files:**
- Create: `src/pages/sobre.astro`, `src/pages/contato.astro`
- Modify: `src/pages/index.astro` (substituir o provisório)

**Interfaces:**
- Consumes: `SITE` de `site.config.ts`, coleções `livros` e `textos`, `BookCard`, `TextList`.
- Produces: home completa; `/sobre/`; `/contato/` com formulário Formspree condicional.

- [ ] **Step 1: Reescrever `src/pages/index.astro`**

```astro
---
import { getCollection } from 'astro:content';
import Base from '../layouts/Base.astro';
import BookCard from '../components/BookCard.astro';
import TextList from '../components/TextList.astro';
const livros = (await getCollection('livros'))
  .sort((a, b) => a.data.ordem - b.data.ordem);
const recentes = (await getCollection('textos'))
  .sort((a, b) => b.data.data.getTime() - a.data.data.getTime())
  .slice(0, 5);
---
<Base title="Adriana Aneli" wide>
  <section class="abertura">
    <h1>Adriana Aneli</h1>
    <p class="lema">Contos, crônicas e poemas — <strong>toda a obra disponível gratuitamente</strong>.</p>
  </section>
  <section>
    <h2>Livros</h2>
    <div class="grade">{livros.map((l) => <BookCard livro={l} />)}</div>
  </section>
  <section>
    <h2>Textos recentes</h2>
    <TextList itens={recentes} />
    <p><a href="/textos/">Ver todos os textos →</a></p>
  </section>
</Base>
<style>
  .abertura { text-align: center; padding: 2rem 0 1rem; }
  .abertura h1 { font-size: 3rem; margin-bottom: 0.5rem; }
  .lema { font-size: 1.15rem; color: var(--cor-tinta-suave); }
  .grade { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1.5rem; }
</style>
```

- [ ] **Step 2: Escrever `src/pages/sobre.astro`** (biografia provisória claramente marcada para a autora substituir)

```astro
---
import Base from '../layouts/Base.astro';
---
<Base title="Sobre a autora">
  <article class="prose">
    <h1>Sobre a autora</h1>
    <p><em>[Biografia a ser fornecida pela autora — este texto é provisório
    e deve ser substituído antes do lançamento.]</em></p>
  </article>
</Base>
```

- [ ] **Step 3: Escrever `src/pages/contato.astro`**

```astro
---
import Base from '../layouts/Base.astro';
import { SITE } from '../site.config';
---
<Base title="Contato">
  <h1>Contato</h1>
  <p>Escreva para <a href={`mailto:${SITE.email}`}>{SITE.email}</a>{SITE.instagram && <> ou visite o <a href={SITE.instagram}>Instagram</a></>}.</p>
  {SITE.formspreeEndpoint ? (
    <form action={SITE.formspreeEndpoint} method="POST" class="card">
      <label>Seu nome <input type="text" name="nome" required /></label>
      <label>Seu e-mail <input type="email" name="email" required /></label>
      <label>Mensagem <textarea name="mensagem" rows="6" required></textarea></label>
      <button class="btn" type="submit">Enviar</button>
    </form>
  ) : (
    <p class="meta">Em breve, formulário de contato direto por aqui.</p>
  )}
</Base>
<style>
  form { display: grid; gap: 1rem; margin-top: 1.5rem; }
  label { display: grid; gap: 0.3rem; }
  input, textarea { font: inherit; padding: 0.5rem; border: 1px solid var(--cor-linha); border-radius: 4px; background: #fff; }
  button { cursor: pointer; background: none; }
</style>
```

- [ ] **Step 4: Build e conferência visual completa**

Run: `npm run build && npm run preview` — navegar por todas as seções.
Expected: navegação completa sem links quebrados; home mostra livro e textos de exemplo.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: páginas Início, Sobre e Contato"
```

---

### Task 8: Ferramentas de conversão — .docx → Markdown e geração de EPUB/PDF

**Files:**
- Create: `tools/convert_docx.py`, `tools/build_book.py`

**Interfaces:**
- Consumes: pandoc (instalado neste task), Chrome instalado na máquina, rota `/livros/<slug>/imprimir/` (Task 5).
- Produces: `python tools/convert_docx.py <arquivo.docx> --genero poema --titulo "..." [--livro slug --ordem N]` → cria `src/content/textos/<slug>.md`; `python tools/build_book.py <slug-do-livro>` → gera `public/downloads/<slug>.epub` e `<slug>.pdf`.

- [ ] **Step 1: Instalar pandoc**

Run: `winget install --id JohnMacFarlane.Pandoc --accept-source-agreements --accept-package-agreements`
Depois (novo terminal): `pandoc --version`
Expected: versão 3.x.

- [ ] **Step 2: Escrever `tools/convert_docx.py`**

```python
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
```

- [ ] **Step 3: Teste de ida e volta (roundtrip)**

Criar um .docx de teste com o próprio pandoc e convertê-lo:
```bash
printf 'Primeira linha do poema,\\\nsegunda linha.\n\nSegunda estrofe com *itálico*.\n' > teste-temp.md
pandoc teste-temp.md -o teste-temp.docx
export PYTHONUTF8=1 && python tools/convert_docx.py teste-temp.docx --genero poema --titulo "Teste Roundtrip"
```
Expected: `src/content/textos/teste-roundtrip.md` criado, com frontmatter correto, itálico preservado (`*itálico*`) e quebras de estrofe mantidas.
Depois: `npm run build` — Expected: PASS (o novo arquivo valida no schema).
Limpar: apagar `teste-temp.md`, `teste-temp.docx` e `src/content/textos/teste-roundtrip.md`.

- [ ] **Step 4: Escrever `tools/build_book.py`**

```python
"""Gera EPUB (pandoc) e PDF (Chrome headless) de um livro.

Uso: python tools/build_book.py amor-expresso
Requer: npm run build executado antes (usa dist/).
"""
import re
import subprocess
import sys
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
            capitulos.append((int(fm.get("ordem", 0)), fm["titulo"], fm["_corpo"]))
    capitulos.sort()
    if not capitulos:
        sys.exit(f"Nenhum texto associado ao livro '{slug}'.")

    downloads = RAIZ / "public" / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)

    # EPUB via pandoc
    juntado = "\n\n".join(f"# {t}\n\n{corpo}" for _, t, corpo in capitulos)
    epub = downloads / f"{slug}.epub"
    subprocess.run(
        ["pandoc", "-f", "markdown", "-o", str(epub),
         "--metadata", f"title={titulo}", "--metadata", "author=Adriana Aneli",
         "--metadata", "lang=pt-BR", "--toc"],
        input=juntado, text=True, encoding="utf-8", check=True,
    )
    print(f"EPUB: {epub}")

    # PDF via Chrome headless sobre a pagina de impressao construida
    html = RAIZ / "dist" / "livros" / slug / "imprimir" / "index.html"
    if not html.exists():
        sys.exit("Rode 'npm run build' antes (dist/ nao contem a pagina de impressao).")
    chrome = next((c for c in CHROME_CANDIDATOS if c.exists()), None)
    if chrome is None:
        sys.exit("Chrome nao encontrado nos caminhos padrao.")
    pdf = downloads / f"{slug}.pdf"
    subprocess.run(
        [str(chrome), "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={pdf}", html.as_uri()],
        check=True,
    )
    print(f"PDF: {pdf}")
    print(f"Agora adicione ao frontmatter de {livro_md.name}:")
    print(f"  pdf: /downloads/{slug}.pdf")
    print(f"  epub: /downloads/{slug}.epub")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Testar geração com o livro de exemplo**

```bash
npm run build
export PYTHONUTF8=1 && python tools/build_book.py amor-expresso
```
Expected: `public/downloads/amor-expresso.epub` e `amor-expresso.pdf` criados. Abrir o PDF e conferir folha de rosto + capítulo de exemplo.
Depois: adicionar `pdf: /downloads/amor-expresso.pdf` e `epub: /downloads/amor-expresso.epub` ao frontmatter de `src/content/livros/amor-expresso.md`, rodar `npm run build` e conferir que os botões aparecem em `/livros/amor-expresso/`.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: ferramentas de conversão docx→md e geração de EPUB/PDF"
```

---

### Task 9: Deploy — repositório GitHub, Actions e Pages

**Files:**
- Create: `.github/workflows/deploy.yml`

**Interfaces:**
- Consumes: conta GitHub `drilagrasta-boop` (gh já autenticado).
- Produces: repositório remoto `adrianaaneli-site`; push em `main` → build → publicação automática no GitHub Pages.

- [ ] **Step 1: Escrever `.github/workflows/deploy.yml`**

```yaml
name: Deploy para GitHub Pages
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: withastro/action@v3
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: Criar repositório e enviar**

```bash
gh repo create adrianaaneli-site --public --source . --push
```
Expected: repo criado e branch `main` enviada.

- [ ] **Step 3: Ativar Pages via Actions e disparar o workflow**

```bash
gh api repos/drilagrasta-boop/adrianaaneli-site/pages -X POST -f build_type=workflow
gh workflow run "Deploy para GitHub Pages"
gh run watch
```
Expected: workflow verde. (Observação: no endereço provisório `*.github.io/adrianaaneli-site/` os caminhos absolutos de CSS podem quebrar — é esperado; o endereço definitivo com domínio próprio resolve. A conferência real é o passo seguinte da Task 10.)

- [ ] **Step 4: Commit (workflow já commitado no push acima; garantir árvore limpa)**

Run: `git status` — Expected: árvore limpa.

---

### Task 10: Domínio próprio — CNAME, guia Registro.br e verificação final

**Files:**
- Create: `public/CNAME`, `docs/guia-registro-br.md`

**Interfaces:**
- Consumes: registro do domínio feito pela autora no Registro.br (etapa humana, guiada pelo doc).
- Produces: site no ar em `https://adrianaaneli.com.br` com HTTPS.

- [ ] **Step 1: Criar `public/CNAME`**

```
adrianaaneli.com.br
```

- [ ] **Step 2: Escrever `docs/guia-registro-br.md`** (guia para a autora, linguagem não técnica)

```markdown
# Guia: registrar adrianaaneli.com.br

## 1. Registrar o domínio (você faz, ~10 minutos, ~R$ 40/ano)
1. Acesse https://registro.br e clique em "Criar conta" (precisa de CPF).
2. Busque por `adrianaaneli.com.br` e confirme que está disponível.
3. Registre por 1 ano (renovação anual automática se quiser).

## 2. Apontar o domínio para o site (você faz com meu acompanhamento)
No painel do Registro.br, em "Editar zona" / modo avançado, criar:
- 4 registros tipo A para `adrianaaneli.com.br` com os valores:
  185.199.108.153 · 185.199.109.153 · 185.199.110.153 · 185.199.111.153
- 1 registro CNAME para `www` com o valor: `drilagrasta-boop.github.io.`

## 3. Avisar o Claude
Depois de salvar, me avise na sessão do Claude Code: eu confirmo a
propagação, ativo o HTTPS no GitHub e verificamos o site no ar juntos.
```

- [ ] **Step 3: Configurar o domínio no GitHub e commit**

```bash
git add -A && git commit -m "feat: CNAME e guia de registro do domínio" && git push
gh api repos/drilagrasta-boop/adrianaaneli-site/pages -X PUT -f cname=adrianaaneli.com.br
```
Expected: push dispara deploy; configuração aceita (a verificação DNS ficará pendente até a autora registrar o domínio).

- [ ] **Step 4: Verificação final (após a autora registrar e apontar o DNS)**

```bash
gh api repos/drilagrasta-boop/adrianaaneli-site/pages --jq '.https_enforced, .status'
curl -sI https://adrianaaneli.com.br | head -3
```
Expected: `status: built`, HTTPS ativo, página respondendo `200`. Ativar "Enforce HTTPS" se ainda não estiver:
`gh api repos/drilagrasta-boop/adrianaaneli-site/pages -X PUT -F https_enforced=true`

---

### Task 11: README com o fluxo de publicação da autora

**Files:**
- Create: `README.md`
- Create: `entrada-docx/.gitkeep` (pasta combinada onde a autora deposita os .docx)

**Interfaces:**
- Consumes: scripts da Task 8.
- Produces: documentação do fluxo completo para sessões futuras do Claude.

- [ ] **Step 1: Escrever `README.md`**

```markdown
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
```

- [ ] **Step 2: Commit e push**

```bash
git add -A && git commit -m "docs: README com fluxo de publicação" && git push
```

---

## Pós-plano (trabalho contínuo, fora deste plano)

- Ingestão do material real: a autora entrega os .docx dos seis livros, biografia, sinopses, capas e a lista de vídeos do YouTube; cada lote passa pelo fluxo do README (converter → conferir → publicar). Remover os conteúdos de exemplo no primeiro lote real.
- Criação da conta Formspree pela autora e preenchimento de `formspreeEndpoint` em `src/site.config.ts`.
- Aquarelas: quando criadas, salvar em `public/images/aquarelas/` e referenciar no frontmatter dos poemas.
```
