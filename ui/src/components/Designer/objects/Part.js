import React from 'react';
import {default as Icon} from '../Icon';

import Vector from './Vector';

export default class Part extends Vector {
  static meta = {
    icon: <Icon icon={'part'} size={30} />,
    initial: {
      // Just a simple base64-encoded outline
      xlinkHref: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAYAAAAGCAYAAADgzO9IAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAhSURBVHgBtYmxDQAADII8lv9faBNH4yoJLAi4ppxgMZoPoxQrXYyeEfoAAAAASUVORK5CYII=",
      rotate: 1,
      width: 100,
      height: 100
    }
  };

  render() {
    let {object, index} = this.props;
    return (
      <image
            xlinkHref={object.xlinkHref}
            //  style={{transform: `rotate(${object.rotate}deg)`, transformOrigin: 'center center'}}
            {...this.getObjectAttributes()}
            transform={'rotate(' + object.rotate + ' 180 180)'}
            rotate={''}
            width={object.width}
            height={object.height} 
        />
    );
  }
}
