import React from 'react';

import {default as styles} from './styles';

const PropertyGroup = ({showIf=true, ...props}) => {
  if (!showIf) {
    return <div style={styles.empty} />;
  }
  return (
    <div style={styles.propertyGroup}>
      {props.children}
    </div>
  );
};

export default PropertyGroup;
