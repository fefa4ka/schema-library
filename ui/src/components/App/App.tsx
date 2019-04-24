import React, { Component } from 'react'
import './App.css'
import { Blocks }   from '../Blocks'
import { Stock } from '../Stock'
import { Layout, Menu } from 'antd'
import { BrowserRouter as Router, Route, Link, Switch } from "react-router-dom"

const {
  Header, Footer, Sider, Content,
} = Layout;
const { SubMenu } = Menu;

const initState = {
  page: 'main'
}
type State = {
  page: string
}

class App extends Component<any> {
  state: State = initState

  render() {
    const { page } = this.state
    let PageContent = () => <div className='App-Description'>
          <a href="/" target='blank'><div className='App-LogoDescription'/></a> 
          <p><strong>schema.vc</strong> is a Python library for building electronic circuits.</p>
          <ul>
              <li><strong>Declarative</strong>: schema.vc makes it painless to create electronic schematics. Design simple blocks for each subsystem in your device, and compose system using this functional components. The declarative definition makes your schematic simpler to understand and easier to modify.</li>
              <li><strong>Component-Based</strong>: Build encapsulated components that manage their properties, then compose them to make complex devices. Since component logic is written in Python instead of graphic schematics, you can easily pass rich data through your components and control valuable parameters.</li>
          </ul>
      </div>

    return (
      <Router>
        <div className="App">
          <Layout style={{height:"100vh"}}>
            <Header>
              <a href="https://github.com/fefa4ka/schema.vc" target='blank'><div className='App-LogoHeader'/></a>
              <Menu
                  mode="horizontal"
                >
                <Menu.Item key="block"><Link to='/block'>Blocks</Link></Menu.Item>
                <Menu.Item key="stock"><Link to='/stock'>Stock</Link></Menu.Item>
              </Menu>
              
            </Header>
            <Switch>
              <Route exact path="/" component={PageContent} /> 
              <Route exact path="/block" component={Blocks} />
              <Route exact path="/block/:block" component={Blocks} />
              <Route exact path="/stock" component={Stock} />
            </Switch>
            {PageContent}
            <Footer><strong>⏚ Circuits</strong> builds by <strong>B</strong>locks with <strong>E</strong>lements and <strong>M</strong>odificators<a className='copyright' href="mailto:alex@nder.work?subject=schema.vc">alex@nder.work</a></Footer>
          </Layout>
        </div>
      </Router>
    )
  }
}

export default App
