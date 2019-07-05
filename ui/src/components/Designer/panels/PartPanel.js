import React, {Component} from 'react';
import _ from 'lodash';

import {default as PropertyGroup} from './PropertyGroup';
import {default as Columns} from './Columns';
import {default as Column} from './Column';
import Dropzone from 'react-dropzone';

export default class PartPanel extends Component {
  onDrop (acceptedFiles) {
    if (acceptedFiles.length == 0) {
      return;
    }

    const file = acceptedFiles[0];
    const fr = new FileReader();

    const setImage = function(e) {
      this.props.onChange('xlinkHref', e.target.result);
    }.bind(this);
    fr.onload = setImage;
    fr.readAsDataURL(file);
  }

  render() {
    const {object} = this.props;
    return (
      <PropertyGroup object={object} showIf={_.has(object, 'xlinkHref')}>
          <Columns label="Part">
            <Column>
          
            </Column>
          </Columns>
      </PropertyGroup>
    );
  }
}
