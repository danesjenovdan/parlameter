const MAX_NAME_LENGTH = 100;

function sanitizeSlug(slug) {
  return String(slug)
    .normalize('NFKD')
    .toLowerCase()
    .replace(/[^a-z0-9-_]/gi, '')
    .slice(0, MAX_NAME_LENGTH);
}

module.exports = {
  sanitizeSlug,
};
