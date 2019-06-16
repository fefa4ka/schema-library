import React, { Component } from 'react'
import { Layout, Table, Button, Modal, Divider,  Icon, Popconfirm } from 'antd'
import axios from 'axios'
import { cn } from '@bem-react/classname'
import { TBlocksScope, BlocksMenu, insertSpaces, resolveBlock } from '../Blocks/Blocks'
import './Stock.css'
import { Part } from './Part'
const { Sider, Content } = Layout

const initState = {
    blocks: {},
    parts: [],
    selectedBlock: '',
    addPartModalVisible: false,
    addPartData: {}
}


type State = {
    blocks: TBlocksScope,
    parts: {
        [name: string]: {
            [mod:string]: string | number
        } | string | number
    }[],
    selectedBlock: string,
    addPartModalVisible: boolean,
    addPartData: any
}

const cnStock = cn('Stock')

export class Stock extends Component {
  state: State = initState
  formRef: any 

    componentWillMount() {    
      axios.get('/api/blocks/')
      .then(res => {
          const blocks: TBlocksScope = {}
          const { data } = res
          
          this.setState({ blocks: data })
      })
      
      this.loadStock()
    }

    showAddPartModal = (part:any) => {
        this.setState({
          addPartModalVisible: true,
          addPartData: part
        })
    }
  
    loadStock() {
      axios.get('/api/parts/?block=' + this.state.selectedBlock)
        .then(res => {
            this.setState({
                parts: res.data
            })
        })
    }

    handleAddPartOk = (e:any) => {
      const form = this.formRef.props.form
      form.validateFields((err:any, values:any) => {
        if (err) {
          return
        }

        const prevData = this.state.addPartData
        axios.post('/api/parts/', {
          ...values,
          id: prevData.id,
          block: this.state.selectedBlock
        }).then(res => this.loadStock())
        form.resetFields()

        this.setState({
          addPartModalVisible: false,
          addPartData: {}
        })
    
      })   
    }
    saveFormRef = (formRef:any) => {
      this.formRef = formRef
    }
    handleAddPartCancel = (e:any) => {
      const form = this.formRef.props.form
      form.resetFields()
        this.setState({
            addPartModalVisible: false,
            addPartData: {}
        })
    }
    render() {
      const columns = [{
        title: 'Model',
        dataIndex: 'model',
        key: 'model',
        render: (text: string, record: any) => 
            record.datasheet
              ? <a href={record.datasheet} className={cnStock('PartTitle')} target='_blank'><Icon type='file-pdf' /> {text}</a>
              : text
      }, {
        title: 'Description',
        dataIndex: 'description',
        key: 'description',
        render: (text: string, record: any) => 
          <div className={cnStock('PartDescription')}>
            <a onClick={() => this.showAddPartModal(record)}>{text || record.model}</a>
            {/* {record.spice_params && Object.keys(record.spice_params).map((name, index) => 
                <Unit
                  key={name}
                  name={name}
                  value={record.spice_params[name]}
                />
             )} */}
          </div>
      }, {
        title: 'Footprint',
        dataIndex: 'footprint',
        key: 'footprint',
      }, {
        title: 'Action',
        dataIndex: 'id',
        key: 'id',
        render: (text: string, record: any) => 
          <div className={cnStock('TableAction')}>
            <Popconfirm
              title="Are you sure delete this part?"
              placement='left'
              onConfirm={() => axios.delete('/api/parts/?id=' + record.id).then(() => this.loadStock())}
              onCancel={() => { }} 
              okText="Yes" 
              cancelText="No"
            >
              <Button icon='delete' shape='circle' type='danger'/>
            </Popconfirm>
          </div>
      }]
    
      
    return (
        <Layout>
            <Sider className='App-Side'>
              <BlocksMenu
                onClick={(param:any) => {
                  this.setState({ selectedBlock: param.key }, this.loadStock)
                }}
                onOpenChange={() => { }}
                blocks={this.state.blocks}
              />
            </Sider>
            <Content>
                <Button type='primary' onClick={this.showAddPartModal}>Add part</Button>
                <Modal
                    title="Add Part"
                    visible={this.state.addPartModalVisible}
                    onOk={this.handleAddPartOk}
                    onCancel={this.handleAddPartCancel}
                >
                  <Part
                    wrappedComponentRef={this.saveFormRef}
                    selectedBlock={this.state.selectedBlock}
                    data={this.state.addPartData}
                    mods={resolveBlock(this.state.selectedBlock, this.state.blocks)} />
                </Modal>
                            
                <Divider orientation='left'>Stock of {insertSpaces(this.state.selectedBlock || '')} Parts</Divider>
                <Table dataSource={this.state.parts} columns={columns} rowKey='id' />
            </Content>
          </Layout>
    )
  }
}
