// non-locale aware version of formatter if Intl is not supported by the browser
const fallbackFormatter = (items) => {
  return items.join(', ');
};

export default (
  items,
  { type = 'conjunction', style = 'long', locale = 'sl' } = {},
) => {
  if (typeof Intl === 'undefined' || typeof Intl.ListFormat === 'undefined') {
    return fallbackFormatter(items);
  }

  const lang = (locale || '').split('-')[0];
  const formatter = new Intl.ListFormat(lang, { style, type });

  return `${formatter.format(items)}`;
};
