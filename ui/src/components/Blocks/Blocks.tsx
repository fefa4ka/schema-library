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

type TBlock = {
  [mod:string]: string[]
}

export type TBlocksScope = {
  [scope: string]: {
    [block: string]: TBlock | TBlocksScope
  }
}

type State = {
  blocks: TBlocksScope,
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
  string = string.replace(/\./g,' ')

  return string
}

export const loadBlocks = (callback: (blocks: TBlocksScope) => void) => {
  axios.get('/api/blocks/')
    .then(res => {
        const { data } = res
      
        callback(data)
    })
}

export const resolveBlock = (path: string | string[], blocks: any) => {
  const properties = Array.isArray(path) ? path : path.split('.')
  return properties.reduce((prev, curr) => prev && prev[curr], blocks)
}

const ScopeMenu = ({ blocks, parent='' }: any) => 
    Object.keys(blocks).map(scope =>
      scope.charAt(0).toUpperCase() === scope.charAt(0) 
        ? <Menu.Item key={parent ? parent + '.' + scope : scope}>{insertSpaces(scope)}</Menu.Item>
        : <SubMenu 
            key={scope} 
            title={<strong>{icons[scope] ? <Icon type={icons[scope]} /> : null}<span>{insertSpaces(scope)}</span></strong>}
          >
            {ScopeMenu({ blocks: blocks[scope], parent: parent ? parent + '.' + scope : scope })}
          </SubMenu>
    )

export const BlocksMenu= ({ onClick, onOpenChange, blocks }:any) => 
  <Menu
    mode="inline"
    defaultSelectedKeys={['1']}
    defaultOpenKeys={['basic']}
    style={{ height: '100%' }}
    onClick={onClick}
    onOpenChange={onOpenChange}
  >
    {ScopeMenu({ blocks })} 
  </Menu>
  
export class Blocks extends Component<any> {
  state: State = initState

  componentWillMount() {    
    loadBlocks((blocks: TBlocksScope) => 
      this.setState({ blocks })
    )
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
                this.props.history.push('/block/' + param.key)
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
