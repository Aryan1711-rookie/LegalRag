export function getDocumentSlug(document) {
  const title = document.title
    .toLowerCase()
    .trim()
    .replace(/[^\p{L}\p{N}]+/gu, "-")
    .replace(/^-+|-+$/g, "");

  return `${title || "document"}--${document.id}`;
}

export function getDocumentUrl(document, chatId = null) {
  const slug = getDocumentSlug(document);

  return chatId
    ? `/research/${slug}/${chatId}`
    : `/research/${slug}`;
}

export function getDocumentId(slug) {
  if (!slug?.includes("--")) return null;

  return slug.split("--").pop();
}