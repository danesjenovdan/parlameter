export const capitalizeFirst = (str) => {
  if (typeof str !== 'string') {
    return str;
  }
  return str.charAt(0).toUpperCase() + str.slice(1);
};

export const titleCase = (str) => {
  if (typeof str !== 'string') {
    return str;
  }
  return str
    .toLowerCase()
    .split(' ')
    .map((word) => capitalizeFirst(word))
    .join(' ');
};
