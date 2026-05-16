import dayjs from "dayjs";
import "dayjs/locale/de";

dayjs.locale("de");

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "";
  return dayjs(iso).format("D. MMMM YYYY");
}

export function formatDateShort(iso: string | null | undefined): string {
  if (!iso) return "";
  return dayjs(iso).format("DD.MM.YYYY");
}

export function readingTimeMinutes(html: string): number {
  const words = html
    .replace(/<[^>]*>/g, " ")
    .split(/\s+/)
    .filter(Boolean).length;
  return Math.max(1, Math.round(words / 220));
}

export function buildZitation(
  titel: string,
  iso: string | null | undefined,
  slug: string,
): string {
  const datum = formatDate(iso) || dayjs().format("D. MMMM YYYY");
  return `Vaeren-Compliance-Brief: „${titel}", ${datum}, vaeren.de/news/${slug}.`;
}
