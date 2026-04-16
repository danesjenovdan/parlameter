import axios from 'axios';

const getTextFromRange = (containerElement, selectionRange) => {
  let beforeText = '';
  let text = '';
  let currentNode = containerElement.childNodes[0];
  while (currentNode) {
    if (currentNode.nodeType === Node.TEXT_NODE) {
      if (currentNode === selectionRange.startContainer) {
        text += currentNode.textContent.slice(0, selectionRange.startOffset);
        beforeText = text;
        text = '';
        if (currentNode === selectionRange.endContainer) {
          text += currentNode.textContent.slice(
            selectionRange.startOffset,
            selectionRange.endOffset,
          );
          break;
        } else {
          text += currentNode.textContent.slice(selectionRange.startOffset);
        }
      } else if (currentNode === selectionRange.endContainer) {
        text += currentNode.textContent.slice(0, selectionRange.endOffset);
        break;
      } else {
        text += currentNode.textContent;
      }
    } else {
      if (currentNode === selectionRange.startContainer) {
        beforeText = text;
        text = '';
      }
      if (currentNode === selectionRange.endContainer) {
        break;
      }
      if (
        currentNode.nodeType === Node.ELEMENT_NODE &&
        currentNode.nodeName === 'P' &&
        text.length
      ) {
        text += '\n';
      }
      currentNode = currentNode.childNodes[0];
      continue;
    }
    let nextNode = currentNode.nextSibling;
    if (
      !nextNode &&
      currentNode.parentNode !== selectionRange.commonAncestorContainer
    ) {
      nextNode = currentNode.parentNode.nextSibling;
    }
    currentNode = nextNode;
  }
  return [text, beforeText.length];
};

const getSelectionRange = (containerElement) => {
  const selection = window.getSelection();
  if (selection && !selection.isCollapsed) {
    if (
      containerElement.contains(selection.anchorNode) &&
      containerElement.contains(selection.focusNode) &&
      selection.rangeCount === 1
    ) {
      const [text, offset] = getTextFromRange(
        containerElement,
        selection.getRangeAt(0),
      );
      return [selection.getRangeAt(0), text, offset];
    }
  }
  return [null, '', 0];
};

export default {
  beforeMount(el, binding) {
    const speechTextElement = el.querySelector('.speech-text');
    const quoteButton = el.querySelector('.everything .quote-button');
    const speechId = Number(el.getAttribute('id'));

    if (!speechTextElement || !quoteButton) {
      return;
    }

    // Click outside hides quote button
    let mouseDownWasOutside = false;
    const isOutside = (targetElement) => {
      return !el.contains(targetElement) && el !== targetElement;
    };
    const onMouseDown = (e) => {
      mouseDownWasOutside = isOutside(e.target);
    };
    const onClick = (e) => {
      if (mouseDownWasOutside && isOutside(e.target)) {
        quoteButton.style.display = 'none';
      }
    };
    el.vcoq_onMouseDown = onMouseDown;
    el.vcoq_onClick = onClick;
    document.addEventListener('mousedown', onMouseDown);
    document.addEventListener('click', onClick);
    // End click outside

    el.addEventListener('mouseup', (event) => {
      // Prevent deselection when clicking on selected text
      event.preventDefault();

      const [selectionRange] = getSelectionRange(speechTextElement);
      if (selectionRange) {
        const textRect = speechTextElement.getBoundingClientRect();
        const selectionRect = selectionRange.getBoundingClientRect();
        const selectionOffset = selectionRect.top - textRect.top;
        const quoteIconOffset = selectionOffset + selectionRect.height / 2;
        quoteButton.style.top = `${quoteIconOffset}px`;
        quoteButton.style.display = 'block';
      } else {
        quoteButton.style.display = 'none';
      }
    });

    quoteButton.addEventListener('mousedown', (event) => {
      // Prevent deselection when clicking on quote button
      event.preventDefault();
    });

    quoteButton.addEventListener('click', () => {
      const [selectionRange, selectedText, startIndex] =
        getSelectionRange(speechTextElement);
      if (selectionRange && selectedText) {
        const { urls } = binding.instance.$root.$options.contextData;
        const { locale } = binding.instance.$i18n;
        const url = `${urls.data}/cards/speech/quote/`;
        axios
          .post(url, {
            speech: speechId,
            start_index: startIndex,
            end_index: startIndex + selectedText.length,
            quote_content: selectedText,
          })
          .then((response) => {
            window.open(
              `${urls.cards}/speech/quote/?id=${response.data.id}&locale=${locale}&template=share`,
            );
          });
      }
    });
  },
  unmounted(el) {
    document.removeEventListener('mousedown', el.vcoq_onMouseDown);
    document.removeEventListener('click', el.vcoq_onClick);
    el.vcoq_onMouseDown = undefined;
    el.vcoq_onClick = undefined;
  },
};
