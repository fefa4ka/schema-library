import React, {Component} from 'react';

import {default as Icon} from '../Icon';
import {default as PropertyGroup} from './PropertyGroup';
import { default as Button } from './Button';
import {default as Columns} from './Columns';
import {default as Column} from './Column';

export default class ArrangePanel extends Component {
  render() {
    let {object} = this.props;
    return (
      <PropertyGroup>
          <Columns label="Arrange">
            <Column>
              <Button onClick={this.props.onArrange.bind(this, 'back')}>
                <Icon icon="send-to-back" />
                <span>send to back</span>
              </Button>
              <Button onClick={this.props.onArrange.bind(this, 'front')}>
                <Icon icon="bring-to-front" />
                <span>bring to front</span>
              </Button>
            </Column>
          </Columns>
        </PropertyGroup>
    );
  }
}
