import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const textos = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/textos' }),
  schema: z.object({
    titulo: z.string(),
    genero: z.enum(['conto', 'cronica', 'poema', 'prefacio']),
    autor: z.string().optional(),      // quando não é da autora (ex.: prefácio)
    data: z.coerce.date(),
    livro: z.string().optional(),      // slug do livro de origem
    ordem: z.number().optional(),      // posição no livro
    vinheta: z.enum(['flor', 'passaro', 'folha', 'inseto', 'sol', 'tamareira', 'grao', 'nuvem', 'pomba', 'taca', 'horizonte']).optional(), // separador gráfico dos poemas
    mostrarTitulo: z.boolean().optional(), // exceção: poema com título próprio exibido (ex.: Tempestade urbana)
    divisor: z.boolean().optional(), // marcador de seção do livro: vira cabeçalho na lista, sem página própria
    aquarela: z.string().optional(),   // ex.: /images/aquarelas/nome.jpg
    youtube: z.string().optional(),    // ID do vídeo, ex.: dQw4w9WgXcQ
    resumo: z.string().optional(),
  }),
});

const livros = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/livros' }),
  schema: z.object({
    titulo: z.string(),
    subtitulo: z.string().optional(), // gênero exibido no cartão (ex.: minicrônicas, poemas)
    sinopse: z.string().optional(),
    ano: z.number().optional(),
    capa: z.string().optional(),       // ex.: /images/capas/slug.jpg
    ordem: z.number().default(99),     // ordem na vitrine
    pdf: z.string().optional(),        // ex.: /downloads/slug.pdf
    epub: z.string().optional(),
  }),
});

export const collections = { textos, livros };
