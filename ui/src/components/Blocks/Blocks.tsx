import React, { Component } from 'react'
import { Block } from '../Block'
import { Layout, Menu, Icon } from 'antd'
import axios from 'axios'
import { BrowserRouter as Router, Route, withRouter } from "react-router-dom";

const {
  Header, Footer, Sider, Content,
} = Layout
const { SubMenu } = Menu
const MenuItemGroup = Menu.ItemGroup

const initState = {
  blocks: {},
  selectedBlock: ''
}
type State = {
  blocks: {
    [pack: string]: {
      [name: string]: {
        [mod: string]: string[]
      }
    }
  },
  selectedBlock: string
}

const icons:any = {
  'abstract': 'build',
  'analog': 'rise',
  'basic': 'sliders',
  'digital': 'barcode'
}

export const insertSpaces = (string:string) => {
  string = string.replace(/([a-z])([A-Z])/g, '$1 $2');
  string = string.replace(/([A-Z])([A-Z][a-z])/g, '$1 $2')

  return string
}

export const BlocksMenu= ({ onClick, onOpenChange, blocks }:any) => 
  <Menu
    mode="inline"
    defaultSelectedKeys={['1']}
    defaultOpenKeys={['basic']}
    style={{ height: '100%' }}
    onClick={onClick}
    onOpenChange={onOpenChange}
  >
    {Object.keys(blocks).map(pack =>
      <SubMenu key={pack} title={<strong><Icon type={icons[pack]} /><span>{insertSpaces(pack)}</span></strong>}>
        {Object.keys(blocks[pack]).filter(block => block[block.length - 1] !== '.').map((block, index) =>
            blocks[pack][block + '.']
            ? <SubMenu key={pack + '.' + block} title={<span>{block}</span>}>
              {Object.keys(blocks[pack][block + '.']).map((element, index) =>
                <Menu.Item key={pack + '.' + block + '.' + element}>{insertSpaces(element)}</Menu.Item>
              )}
          </SubMenu>
          : <Menu.Item key={pack + '.' + block}>{insertSpaces(block)}</Menu.Item>

        )}
      </SubMenu>
    )}
  </Menu>
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
    const { blocks } = this.state
    const selectedBlock = (this.props.match && this.props.match.params.block) || 'basic.Resistor'
    let mods = {}
    
    if (Object.keys(blocks).length > 0) {
      mods = selectedBlock.split('.').reduce((o:any, key:string)=>o[key], blocks)
    } 
    
    return (
          <Layout>
            <Sider className='App-Side'>
            <BlocksMenu 
              onClick={(param:any) => {
                console.log(param.keys)
                this.props.history.push('/block/' + param.key)
              }}
            onOpenChange={(openKeys: any) => {
                console.log(openKeys)
                if (openKeys.length) {
                  this.props.history.push('/block/' + openKeys[openKeys.length - 1])
                }
              }}
              blocks={blocks}
            />
            </Sider>
        <Content>
          
          {selectedBlock &&
            <Block
              name={selectedBlock}
              mods={mods}
            />}
          </Content>
        </Layout>

    );
  }
}
