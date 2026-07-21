# Site literário — Adriana Aneli, Escritora

**Data:** 21/07/2026
**Status:** Aprovado em conversa; aguardando revisão final da autora

## Objetivo

Criar um site próprio para a escritora Adriana Aneli disponibilizar **gratuitamente** toda a sua obra em edição de autor: contos, crônicas, poemas, livros completos, resenhas literárias e fortuna literária. O site substitui, na função de acervo, o blog atual (https://adrianaaneli.wordpress.com/), que permanece no ar até decisão futura da autora.

## Decisões tomadas

| Tema | Decisão |
|---|---|
| Acesso ao material | Leitura online (cada texto é uma página) **e** download gratuito (PDF/EPUB por livro) |
| Plataforma | Site estático novo (Astro), hospedagem gratuita no GitHub Pages |
| Domínio | `adrianaaneli.com.br`, registrado pela autora no Registro.br (~R$ 40/ano); único custo do projeto |
| Fonte do conteúdo | Arquivos Word (.docx) da autora, convertidos pelo Claude |
| Atualizações futuras | Autora salva o .docx em pasta combinada e pede ao Claude para publicar; sem painel administrativo |
| Visual | Clássico literário: fundo creme, tipografia serifada, sensação de livro impresso |
| Vídeo e música | Videoclipes de poemas já publicados no YouTube, incorporados nas páginas dos poemas |
| Ilustrações | Aquarelas delicadas para os poemas — **ainda serão criadas**; o layout já nasce preparado para recebê-las |

## Estrutura de páginas

```
Início
├── Textos            → contos, crônicas e poemas, com filtro por gênero
│   └── página individual por texto; poemas podem exibir
│       aquarela em destaque e videoclipe do YouTube
├── Livros            → um cartão por livro: capa, sinopse
│   └── página do livro: leitura online capítulo a capítulo
│       + botões "Baixar PDF" e "Baixar EPUB"
├── Resenhas          → críticas da autora sobre obras de terceiros
├── Fortuna literária → o que já escreveram/disseram sobre a obra da autora
├── Sobre a autora    → biografia e foto
└── Contato           → e-mail, redes sociais e formulário (Formspree, gratuito)
```

A página **Início** apresenta a autora em poucas linhas, destaca os livros com capas, lista os textos mais recentes e comunica com clareza: *"toda a obra disponível gratuitamente"*.

Livros conhecidos do site atual (a confirmar com a autora quais entram): *Amor expresso*, *A construção da primavera*, *O Sol da Tarde*, *Tempestade urbana*, *Mitos e lendas*, *Sol de Pirlimpim* (infantil).

## Visual — clássico literário

- Fundo creme/claro, texto escuro, tipografia serifada elegante (ex.: par serifada para leitura + serifada display para títulos).
- Coluna de leitura estreita e confortável, muito espaço em branco.
- Poemas com diagramação especial: centralizados, com respiro; aquarela acima ou ao lado quando existir; vídeo do YouTube incorporado abaixo quando houver clipe.
- Totalmente responsivo (prioridade para leitura no celular).
- Sem anúncios, sem rastreadores invasivos.

## Arquitetura técnica

- **Gerador:** Astro (site estático). Conteúdo em Markdown com frontmatter (título, gênero, livro de origem, data, aquarela, ID do vídeo YouTube).
- **Coleções de conteúdo:** `textos` (conto | crônica | poema), `livros`, `resenhas`, `fortuna`, páginas avulsas (sobre, contato).
- **Conversão:** .docx → Markdown via pandoc, preservando itálicos, títulos e quebras de estrofe. **Regra de fluxo:** após cada conversão, a autora confere o texto convertido antes da publicação (versos quebrados no lugar errado mudam o poema).
- **PDF/EPUB:** gerados a partir dos mesmos Markdown (pandoc), com capa e sumário; arquivos servidos pelo próprio site.
- **Vídeos:** embed do YouTube (sem upload de mídia pesada no repositório).
- **Hospedagem/Deploy:** GitHub Pages com GitHub Actions (push → build → publica). Domínio `adrianaaneli.com.br` apontado via Registro.br (registro feito pela autora, com orientação passo a passo; configuração DNS e HTTPS feitas no projeto).
- **Formulário de contato:** Formspree (plano gratuito) enviando ao e-mail da autora; e-mail e redes sociais também exibidos diretamente.

## Fluxo de publicação futura

1. Autora salva o texto novo (.docx) na pasta combinada do projeto.
2. Pede ao Claude Code: "publica o texto X".
3. Claude converte, mostra o resultado para conferência da autora, ajusta se preciso, publica (commit + push → deploy automático).

## Fora do escopo (por ora)

- Painel administrativo / CMS.
- Comentários de leitores.
- Venda de livros ou área paga.
- Migração automática do conteúdo do WordPress (textos entram a partir dos .docx da autora; aproveitamento pontual do blog antigo pode ser feito manualmente depois).
- Newsletter (pode ser avaliada no futuro).

## Critérios de sucesso

- Site no ar em `adrianaaneli.com.br`, com HTTPS, sem custo mensal.
- Todos os livros escolhidos pela autora legíveis online e baixáveis em PDF/EPUB.
- Poemas com clipe exibem o vídeo do YouTube na própria página.
- Layout de poema pronto para receber aquarelas quando forem criadas.
- Autora consegue publicar texto novo apenas entregando um .docx e pedindo ao Claude.
- Leitura confortável no celular.
