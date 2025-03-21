export default (isoDate, invalidDateText) => {
  if (!isoDate) {
    return invalidDateText ?? 'Invalid Date';
  }
  const date = new Date(isoDate);
  if (Number.isNaN(date.getTime())) {
    return invalidDateText ?? 'Invalid Date';
  }
  return `${date.getDate()}. ${date.getMonth() + 1}. ${date.getFullYear()}`;
};
