import React, { Component } from 'react';
import './App.css';
import { Block } from '../Block'
import { Layout, Menu, Icon } from 'antd';
import axios from 'axios'
import Item from 'antd/lib/list/Item';

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

class App extends Component {
  state: State = initState

  componentWillMount() {    
    axios.get('http://localhost:3000/api/blocks/')
        .then(res => {
            this.setState({
                blocks: res.data
            })
        })
  }
  render() {
    const blocks = Object.keys(this.state.blocks)
    const { selectedBlock } = this.state
    
    return (
      <div className="App">
        <Layout>
          <Header>
            <Menu
                mode="horizontal"
                defaultSelectedKeys={['1']}
              >
              <Menu.Item key="1">Blocks</Menu.Item>
              <Menu.Item key="2">Circuit</Menu.Item>
              <Menu.Item key="3">Settings</Menu.Item>
            </Menu>
          </Header>
          <Layout>
            <Sider>
              <Menu
                mode="inline"
                defaultSelectedKeys={['1']}
                defaultOpenKeys={['sub1']}
                style={{ height: '100%' }}
                onClick={param => {
                  this.setState({ selectedBlock: param.key })
                }}
              >
                {blocks.map((block, index) =>
                  <Menu.Item key={block}>{block}</Menu.Item>)}
              </Menu>
            </Sider>
            <Content>
              {selectedBlock && <Block name={selectedBlock} mods={this.state.blocks[selectedBlock]} />}
            </Content>
          </Layout>
          <Footer><strong>⏚ Circuits</strong> builds by <strong>B</strong>locks with <strong>E</strong>lements and <strong>M</strong>odificators</Footer>
        </Layout>
      </div>
      
    );
  }
}

export default App;
