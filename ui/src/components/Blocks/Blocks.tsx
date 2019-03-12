import React, { Component } from 'react';
import { Block } from '../Block'
import { Layout, Menu } from 'antd';
import axios from 'axios'
import { BrowserRouter as Router, Route, withRouter } from "react-router-dom";

const {
  Header, Footer, Sider, Content,
} = Layout;
const { SubMenu } = Menu;

const initState = {
  blocks: {},
  selectedBlock: ''
}
type State = {
  blocks: {
    [name: string]: {
      [mod:string]: string[]
    }
  },
  selectedBlock: string
}

export class Blocks extends Component<any> {
  state: State = initState

  componentWillMount() {    
    axios.get('/api/blocks/')
        .then(res => {
            this.setState({
                blocks: res.data
            })
        })
  }
  render() {
    const blocks = Object.keys(this.state.blocks).filter(block => block[block.length - 1] !== '.')

    const selectedBlock = (this.props.match && this.props.match.params.block) || 'Resistor'
    
    function insertSpaces(string:string) {
      string = string.replace(/([a-z])([A-Z])/g, '$1 $2');
      string = string.replace(/([A-Z])([A-Z][a-z])/g, '$1 $2')
      return string
    }
    
    
    return (
          <Layout>
            <Sider className='App-Side'>
              <Menu
                mode="inline"
                defaultSelectedKeys={['1']}
                defaultOpenKeys={['sub1']}
                style={{ height: '100%' }}
                onClick={param => {
                  this.props.history.push('/block/' + param.key)
                }}
                onOpenChange={openKeys => {
                  if (openKeys.length) {
                    this.props.history.push('/block/' + openKeys[openKeys.length - 1])
                  }
                }}
          >

            {blocks.map((block, index) =>
            
              this.state.blocks[block + '.']
                ? <SubMenu key={block} title={<span>{block}</span>}>
                  {Object.keys(this.state.blocks[block + '.']).map((element, index) =>
                    <Menu.Item key={block + '.' + element}>{insertSpaces(element)}</Menu.Item>
                  )}
              </SubMenu>
              : <Menu.Item key={block}>{insertSpaces(block)}</Menu.Item>
            
              )}
              </Menu>
            </Sider>
        <Content>
          
          {selectedBlock &&
            <Block
              name={selectedBlock}
              mods={selectedBlock.includes('.')
                ? this.state.blocks[selectedBlock.split('.')[0] + '.'][selectedBlock.split('.')[1]]
                : this.state.blocks[selectedBlock] } />}
            </Content>
          </Layout>

    );
  }
}
