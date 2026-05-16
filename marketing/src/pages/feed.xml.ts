import rss from "@astrojs/rss";
import type { APIContext } from "astro";

import { fetchNewsList, fetchNewsDetail } from "../lib/api";

export async function GET(context: APIContext) {
  const list = await fetchNewsList();
  // Detail nur für die top-50 holen (Feed ist nicht endlos).
  const top = list.slice(0, 50);
  const items = await Promise.all(
    top.map(async (p) => {
      const detail = await fetchNewsDetail(p.slug);
      return {
        title: p.titel,
        link: `/news/${p.slug}`,
        description: p.lead,
        pubDate: p.published_at ? new Date(p.published_at) : new Date(),
        content: detail?.body_html ?? p.lead,
      };
    }),
  );

  return rss({
    title: "Vaeren-Compliance-Brief",
    description:
      "Wöchentlich kuratierte Rechtsnews aus zwölf autoritativen Primärquellen, für den industriellen Mittelstand.",
    site: context.site!,
    items,
    customData: "<language>de-DE</language>",
  });
}
