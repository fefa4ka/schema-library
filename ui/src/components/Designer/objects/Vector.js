import {Component} from 'react';

import {SizePanel, TextPanel,
        StylePanel, ArrangePanel, ImagePanel, PartPanel} from '../panels';


export default class Vector extends Component {
  static panels = [
    SizePanel,
    TextPanel,
    StylePanel,
    ImagePanel,
    PartPanel,
    ArrangePanel
  ];

  getStyle() {
    let {object} = this.props;
    return {
      mixBlendMode: object.blendMode
    }
  }

  getTransformMatrix({rotate, x, y, width, height}) {
    if (rotate) {
      let centerX = width / 2 + x;
      let centerY = height / 2 + y;
      return `rotate(${rotate} ${centerX} ${centerY})`;
    }
  }

  getObjectAttributes() {
    let {object, onRender, ...rest} = this.props;
    return {
      ...object,
      transform: this.getTransformMatrix(object),
      ref: onRender,
      ...rest
    };
  }
}
