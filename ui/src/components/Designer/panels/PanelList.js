import React, {Component} from 'react';

import {default as styles} from './styles';

class PanelList extends Component {
  render() {
    let {object, objectComponent, id} = this.props;

    return (
      <div style={{...styles.propertyPanel}} className='Designer-PanelList'>
        {objectComponent.panels.map((Panel, i) => <Panel key={i} id={id} {...this.props} />)}
      </div>
    );
  }
};

export default PanelList;
