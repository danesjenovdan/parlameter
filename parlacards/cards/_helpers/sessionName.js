export default (session, $t) => {
  if (session.joint_data?.length) {
    let name = `${$t('joint-session')}: `;
    let sessionNames = session.joint_data
      .map((jointSession) => {
        return jointSession.name;
        // return `${jointSession.name} (${jointSession.organization.name})`;
      })
      .join(', ');
    return name + sessionNames;
  } else {
    return session.name;
  }
};
