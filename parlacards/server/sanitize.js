function sanitizeSlug(slug) {
  return String(slug)
    .normalize('NFKD')
    .replace(/[^a-z0-9-_]/gi, '');
}

function sanitizeCardName(cardName) {
  return String(cardName).split('/').map(sanitizeSlug).join('/');
}

export { sanitizeSlug, sanitizeCardName };
