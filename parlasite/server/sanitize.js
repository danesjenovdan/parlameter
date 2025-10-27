function sanitizeSlug(slug) {
  return String(slug)
    .normalize('NFKD')
    .replace(/[^a-z0-9-_]/gi, '');
}

module.exports = {
  sanitizeSlug,
};
