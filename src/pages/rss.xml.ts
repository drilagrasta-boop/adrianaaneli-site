import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';
import { SITE } from '../site.config';

const rotulo = { conto: 'Conto', cronica: 'Crônica', poema: 'Poema', prefacio: 'Prefácio' } as const;

export async function GET(context: APIContext) {
  const textos = (await getCollection('textos'))
    .sort((a, b) => b.data.data.getTime() - a.data.data.getTime());
  return rss({
    title: SITE.nome,
    description: SITE.descricao,
    site: context.site!,
    items: textos.map((t) => ({
      title: t.data.titulo,
      link: `/textos/${t.id}/`,
      pubDate: t.data.data,
      description: t.data.resumo ?? rotulo[t.data.genero],
    })),
    customData: '<language>pt-BR</language>',
  });
}
