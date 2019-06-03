import React, { Component } from 'react'
import { KiCad } from './Kicad'
import { Row, Col, Layout, Menu, Table, Button, Modal, Divider, Form, Icon, Input, Popconfirm } from 'antd'
import axios from 'axios'
import { Select, Tooltip, TreeSelect } from 'antd'
import { cn } from '@bem-react/classname'
import { BlocksMenu, insertSpaces, resolveBlock } from '../Blocks/Blocks'
import './Stock.css'
import { Unit } from '../Unit'

const TreeNode = TreeSelect.TreeNode
const Option = Select.Option
const { Sider, Content } = Layout
const { SubMenu } = Menu


const initState = {
    blocks: {},
    parts: [],
    selectedBlock: '',
    addPartModalVisible: false,
    addPartData: {}
}
type Blocks = {
  [name: string]: {
      [mod:string]: string[] | { [block: string]: string[] }
  }
}
type Mods = {
      [mod:string]: string[] 
}

type State = {
    blocks: Blocks,
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
 
const initFormState = {
  selectedBlockProps: {},
  selectedMods: [],
  selectedProps: [],
  footprint: '',
  footprints: {},
  params: {},
  paramsValue: {},
  spiceAttrs: {},
  spice: '',
  spiceParams: {}
}

type Params = {
  [name: string]: {
    description: string,
    value: string | number,
    unit: {
      name: string,
      suffix: string
    }
  }
}

type FormState = {
  selectedBlockProps: {
    [name:string]: string[]
  },
  selectedMods: string[],
  selectedProps: string[],
  footprint: string,
  footprints: Blocks,
  params: Params,
  paramsValue: any,
  spiceAttrs: Params,
  spice: string,
  spiceParams: { [name: string]: number }
}


class AddForm extends React.Component<{ form: any, selectedBlock: string, mods: Mods, data:any }, {}> {
  state: FormState = initFormState
  canvasRef = React.createRef<HTMLCanvasElement>()
  kicadviewer: any = null
  componentWillMount() {
    this.loadStockPart()
  }

  componentDidMount() {
    let options = {
      grid: 1.27
    }
    this.kicadviewer = new KiCad(this.canvasRef.current, options)
  }

  componentDidUpdate(prevProps: any) {
    if (this.props.data.id != prevProps.data.id) {
      this.loadStockPart()
    }
  }
  loadStockPart() {
    const { data } = this.props
      const partData = this.props.data.model && {
        ...this.props.data,
        ...this.props.data.stock[0] || {}
      } || {} 


      this.setState({
        selectedMods: data.mods || [],
        selectedProps: data.props || [],
        footprint: data.footprint,
        paramsValue: data.params || {},
        spice: data.spice,
        spiceParams: data.spice_params
      }, () => this.loadBlock(partData) )   
  }
  
  loadBlock(partData: any = {}) {
    const selectedMods: { [name: string]: string[] } = this.state.selectedMods.reduce((mods: { [name: string]: string[] }, mod) => {
      const [type, value] = mod.split('=')
      mods[type] = mods[type] || []
      mods[type].push(value)

      return mods
    }, {})

    const {
      setFieldsValue
    } = this.props.form
    const modsUrlParam = Object.keys(selectedMods).map((mod: string) => mod + '=' + selectedMods[mod].join(','))
    axios.get('/api/blocks/' + this.props.selectedBlock + '/part_params/?' + modsUrlParam)
      .then(res => {
        const { part, spice, props } = res.data
        const paramsValue = partData ? partData.params || {} : Object.keys(part).reduce((params:any, param) => {
          params[param] = []
          return params
        }, {})
        this.setState({ params: part, spiceAttrs: spice, paramsValue, selectedBlockProps: props }, () => {
          const params = Object.keys(this.state.paramsValue).reduce((params:any, name) => {
            params[`params[${name}]`] = this.state.paramsValue[name]

            return params
          }, {})
          
          setFieldsValue({ ...partData, ...params })

          if (partData.footprint) {
            axios.get('/api/parts/footprint?name=' + partData.footprint.replace('=', ':')).then((data: any) => {

              this.kicadviewer.render(data.data)
            })
          }
        })
      })
  }
  
  handleSubmit = (e:any) => {
    e.preventDefault()
    this.props.form.validateFields((err:any, values:any) => {
      if (!err) {
        console.log('Received values of form: ', values)
      }
    })
  }
  addToSpiceModel(param: string) {
    const {
      setFieldsValue, getFieldValue
    } = this.props.form

    let spiceModel = getFieldValue('spice') || ''
      
    let spaced = false
    if (spiceModel.length && spiceModel[spiceModel.length - 1] !== ' ') {
      spiceModel += ' '
    }

    spiceModel += param + '='
      
    setFieldsValue({ spiceModel })
  }
  
  render() {
    const { selectedBlock, mods } = this.props
    const category: string = selectedBlock.slice(0, selectedBlock.indexOf('.'))
    const block:string = selectedBlock.slice(selectedBlock.indexOf('.') + 1) 
    const props = this.state.selectedBlockProps
    const footprints: any = this.state.footprints

    const {
      getFieldDecorator, getFieldsError, getFieldError, isFieldTouched, setFieldsValue, getFieldValue
    } = this.props.form

    const { spiceAttrs }= this.state
    const params = this.state.params || getFieldValue('params') || {}

    const attributes = Object.keys(params).map(name => {
      const args = params
      const isExists = args.hasOwnProperty(name)

      let suffix = ''
      let value = this.state.paramsValue ? this.state.paramsValue[name] : []
        if (isExists && args[name] && args[name].unit) {
        if (isExists && args[name].unit.name === 'network') {
          return null
        }

        suffix =  args[name].unit.suffix
      }
      if(value === '') {
        value = undefined
      }

       return getFieldDecorator(`params[${name}]`, {})(<Select
          key={name}
          mode="tags"
          style={{ width: '100%' }}
          placeholder={name + ' in ' + suffix}
        //  value={value}
         onChange={(value) => {
           this.setState(({ paramsValue }:FormState) => {

             paramsValue[name] = value  
            
             return { paramsValue }
           }, () => { })
         }}
        >
            
        </Select>)
    })

    const spice_attributes = this.state.spiceParams && Object.keys(spiceAttrs).map((name, index, list) => {
      const args = spiceAttrs
      const isExists = args.hasOwnProperty(name)

      if (isExists && args[name].unit.name === 'network') {
          return null
      }

      return (<Unit
        key={name}
        name={name}
        suffix={args[name].unit.suffix}
        value={this.state.spiceParams[name] || '?'}
        description={args[name].description}
      />)
    })

    return (
      <Form layout="inline" onSubmit={this.handleSubmit} className={cnStock('AddForm')}>
        <Divider orientation="left">Part</Divider>
        <Row>
          <Col span={12}>
            <Form.Item>
            {mods && Object.keys(mods).length 
              ? getFieldDecorator('mods', {})(
                <TreeSelect
                  showSearch
                  style={{ width: '205px' }}
                  
                  placeholder="Modificators"
                  treeCheckable={true}
                  multiple
                  treeDefaultExpandAll
                  onChange={selectedMods => this.setState({ selectedMods }, this.loadBlock)}
              >
                  {Object.keys(mods).map(type =>
                      <TreeNode value={type} title={type} key={type}>
                          {mods[type].map((value: string) => 
                              <TreeNode value={type + ':' + value} title={value} key={type + ':' + value} />
                          )}
                      </TreeNode>
                  )}
              </TreeSelect>)
                : ''}
            </Form.Item>
            <Form.Item>
            {props && Object.keys(props).length 
              ? getFieldDecorator('props', {})(
                <TreeSelect
                  showSearch
                  style={{ width: '205px' }}
                  placeholder="Properties"
                  treeCheckable={true}
                  multiple
                  treeDefaultExpandAll
                  onChange={selectedProps => this.setState({ selectedProps }, this.loadBlock)}
              >
                  {Object.keys(props).map(type =>
                      <TreeNode value={type} title={type} key={type}>
                          {props[type].map(value => 
                              <TreeNode value={type + ':' + value} title={value} key={type + ':' + value} />
                          )}
                      </TreeNode>
                  )}
              </TreeSelect>)
                : ''}
            </Form.Item>
            <Form.Item>
              {getFieldDecorator('model', {
                rules: [{ required: true, message: 'Please input model name' }],
              })(
                <Input placeholder="Model" style={{ width: '205px' }} />
              )}
            </Form.Item>

            <Divider orientation="left">Stock</Divider>
            <Row className={cnStock('AddFormStock')}>
              <Form.Item>
                {getFieldDecorator('quantity', {
                  rules: [{ required: true, message: 'Please input quantity' }],
                })(
                  <Input placeholder="Quantity" />
                )}
              </Form.Item>
              <Form.Item>
                {getFieldDecorator('stock', {
                  rules: [{ required: true, message: 'Please input storage place description' }],
                })(
                  <Input placeholder="Place" />
                )}
              </Form.Item>
            </Row>
          </Col>

          <Col span={12}>
            <Form.Item>
              {getFieldDecorator('scheme', {})(
                <Input placeholder="KICAD Device" style={{ width: '230px' }} />
              )}
            </Form.Item>
            <Form.Item>
              {getFieldDecorator('footprint', {
                rules: [{ required: true, message: 'Please select footprint' }],
              })(
                <TreeSelect
                  showSearch
                  style={{ width: 230 }}
                  
                  dropdownStyle={{ maxHeight: 400, overflow: 'auto' }}
                  placeholder="Footprint"
                  allowClear
                  treeDefaultExpandAll
                  onSearch={(value) => {
                    if (value.length >= 3) {
                      axios.get('/api/parts/footprints/?query=' + value).then((data: any) => {
                        this.setState({ footprints: data.data })
                      })
                    }
                  }}
                  onChange={(value) => {
                    axios.get('/api/parts/footprint?name=' + value).then((data: any) => {

                      this.kicadviewer.render(data.data)
                    })
                  }}>
                
                {Object.keys(this.state.footprints).map((type:string) =>
                  <TreeNode title={type} key={type}>
                      {footprints[type].map((value:string) => 
                          <TreeNode value={type + ':' + value} title={value} key={type + ':' + value} />
                      )}
                  </TreeNode>
                )}
                </TreeSelect>
              )}
            </Form.Item>
            <canvas ref={this.canvasRef} width={1800} height={1500} className={cnStock('AddFootprint')}></canvas>
          </Col>
        </Row> 

        <Form.Item style={{width: '100%'}}>
          {getFieldDecorator('datasheet', {})(
            <Input placeholder="Datasheet Url" />
          )}
        </Form.Item>
        <Form.Item style={{width: '100%'}}>
          {getFieldDecorator('description', {})(
            <Input.TextArea rows={2} placeholder='Description'/>
          )}`
        </Form.Item>

        <Row className={cnStock('AddParams')}>
          <Col span={12}>
            <Divider orientation="left">Part Characteristics</Divider>
            {attributes}
          </Col>
          <Col span={12}>
            <Divider orientation="left">Spice Model</Divider>
            {getFieldDecorator('spice', {})(
                <Input.TextArea rows={4} placeholder='Spice model params'/>
            )}
            {spice_attributes}
          </Col>
        </Row>
      </Form>
    )
  }
}
const WrappedAddForm = Form.create()(AddForm)


export class Stock extends Component {
  state: State = initState
  formRef: any 

    componentWillMount() {    
      axios.get('/api/blocks/')
      .then(res => {
          const blocks: Blocks = {}
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
                  <WrappedAddForm
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
