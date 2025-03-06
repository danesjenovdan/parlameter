export default (email) => {
  if (!email || email.length < 24) {
    return email;
  }
  const [addr, domain] = email.split('@');
  if (addr.length < 18) {
    return email;
  }
  return `${addr.slice(0, 16)}…@${domain}`;
};
