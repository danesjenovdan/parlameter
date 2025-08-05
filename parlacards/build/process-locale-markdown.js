import { Remarkable } from 'remarkable';

const md = new Remarkable();

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
