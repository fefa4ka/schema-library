import React, { Component } from 'react';
import './App.css';
import { Blocks }   from '../Blocks'
import { Circuits } from '../Circuits'
import { Stock } from '../Stock'
import { Layout, Menu } from 'antd';


const {
  Header, Footer, Sider, Content,
} = Layout;
const { SubMenu } = Menu;

const initState = {
  page: 'blocks'
}
type State = {
  page: string
}

class App extends Component {
  state: State = initState

  navigate({ item, key, keyPath }:any) {
    this.setState({
      page: key
    })
  }
  render() {
    const { page } = this.state
    let PageContent

    if (page === 'blocks') {
      PageContent = <Blocks/>
    }

    if(page === 'circuits')
    {
      PageContent = <Circuits/>  
    }
    
    if(page === 'stock') {
      PageContent = <Stock/>
    }

    return (
      <div className="App">
        <Layout>
          <Header>
            <Menu
                mode="horizontal"
                defaultSelectedKeys={['blocks']}
                onClick={(params) => this.navigate(params)}
              >
              <Menu.Item key="blocks">Blocks</Menu.Item>
              <Menu.Item key="circuits">Circuit</Menu.Item>
              <Menu.Item key="stock">Stock</Menu.Item>
            </Menu>
          </Header>
          {PageContent}
          <Footer><strong>⏚ Circuits</strong> builds by <strong>B</strong>locks with <strong>E</strong>lements and <strong>M</strong>odificators</Footer>
        </Layout>
      </div>
      
    );
  }
}

export default App;
