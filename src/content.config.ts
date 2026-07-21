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
