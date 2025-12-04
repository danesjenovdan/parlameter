import { Remarkable } from 'remarkable';

const md = new Remarkable();

md.use((md) => {
  const original_link_open = md.renderer.rules.link_open;
  md.renderer.rules.link_open = (...args) => {
    let result = original_link_open(...args);
    result = result.replace('>', ' target="_blank" rel="noopener">');
    return result;
  };
});

const processLocaleMarkdown = (messages) => {
  if (messages?.card) {
    const cardKeys = Object.keys(messages.card);
    cardKeys.forEach((key) => {
      if (key.startsWith('info')) {
        messages.card[key] = md.render(messages.card[key]);
      }
    });
  }
  return messages;
};

export { processLocaleMarkdown };
