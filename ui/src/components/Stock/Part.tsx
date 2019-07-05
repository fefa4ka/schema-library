import React, { Component } from 'react'
import { KiCad } from './Kicad'
import { Row, Col, Divider, Form, Input  } from 'antd'
import axios from 'axios'
import { Select, TreeSelect } from 'antd'
import './Stock.css'
import { Unit } from '../Unit'
import { TParams, TDictList } from '../Block'
import ReactToPrint from 'react-to-print'

import { cn } from '@bem-react/classname'
const cnStock = cn('Stock')

const TreeNode = TreeSelect.TreeNode
const Option = Select.Option
 
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
  spiceParams: {},
  pins: [],
  symbol_pins: []
}

type TFootprints = {
    [name: string]: {
        [mod:string]: string[] | { [block: string]: string[] }
    }
}
  
type FormState = {
  selectedBlockProps: TDictList,
  selectedMods: string[],
  selectedProps: string[],
  footprint: string,
  footprints: TFootprints,
  params: TParams,
  paramsValue: any,
  spiceAttrs: TParams,
  spice: string,
  spiceParams: { [name: string]: number },
  symbol_pins: string[]
  pins: string[], 
}

const PrintLabel = ({ block, model, description, footprint, params }: any) => {
    let [library, symbol] = footprint ? footprint.split(':') : ['', '']
    const blockScope = block.split('.')
    const blockName = blockScope[blockScope.length - 1] 

    const value = params ? params['value'] : []
    
    const blockTitle = library && blockName && library.toLowerCase().indexOf(blockName.toLowerCase()) !== -1
        ? library
        : blockName + ' / ' + library

    return (
        <table className={cnStock('PrintLabel')}>
            <tr>
                <td className={cnStock('PrintLabelBlock')}>
                    {blockTitle}
                </td>
            </tr>
            <tr>
                <td className={cnStock('PrintLabelModel')}>
                    {model
                        ? model
                        : value}
                </td>
            </tr>
            <tr>
                <td className={cnStock('PrintLabelDescription')}>
                    {model ? value || description : description}
                </td>
            </tr>
            <tr>
                <td className={cnStock('PrintLabelFootprint')}>
                    {symbol.replace(/_/g, ' ')}
                </td>
            </tr>
        </table>
    )
}

class AddForm extends React.Component<{ form: any, selectedBlock: string, mods: TDictList, data:any }, {}> {
  state: FormState = initFormState
  canvasRef = React.createRef<HTMLCanvasElement>()
  printLabelRef: any = null
  // kicadviewer: any = null
  componentWillMount() {
    this.loadStockPart()
  }

  componentDidMount() {
    let options = {
      grid: 1.27
    }
    // this.kicadviewer = new KiCad(this.canvasRef.current, options)
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
      const [type, value] = mod.split(':')
      mods[type] = mods[type] || []
      mods[type].push(value)

      return mods
    }, {})

    const modsUrlParam = Object.keys(selectedMods).map((mod: string) => mod + '=' + selectedMods[mod].join(','))
    console.log(modsUrlParam)

    axios.get('/api/blocks/' + this.props.selectedBlock + '/part_params/?' + modsUrlParam)
      .then(res => {
            
        const { part, spice, pins, props } = res.data
        const paramsValue = partData ? partData.params || {} : Object.keys(part).reduce((params: any, param) => {
          params[param] = []
          return params
        }, {})

        // const block_pins: any = pins.reduce((pins: any, pin: string) => {
        //   if (partData.pins) {
        //     pins[pin] = partData.pins[pin]
        //   }

        //   return pins
        // }, {})

        this.setState({
          pins,
          params: part,
          spiceAttrs: spice,
          paramsValue,
          selectedBlockProps: props
        }, () => {
          const params = Object.keys(this.state.paramsValue).reduce((params:any, name) => {
            params[`params[${name}]`] = this.state.paramsValue[name]

            return params
          }, {})
          const {
            setFieldsValue
          } = this.props.form
      
            
          const pinsData: any = params['params[units]']
            ? params['params[units]'].reduce((data: any, unit: any) => {
                pins.forEach((pin: any) => {
                  const pinData = partData.pins[unit]
                    ? partData.pins[unit][pin] || {}
                    : {}
                
                  data[`pins[${unit}][${pin}]`] = pinData
                }, {})

                return data
              }, {})
            : {}
          console.log({ ...partData, ...params})
            // console.log({ ...partData, ...params, ...pinsData })
          

          // if (partData.footprint) {
          //   axios.get('/api/parts/footprint?name=' + partData.footprint.replace('=', ':')).then((res: any) => {
          //     // this.kicadviewer.render(res.data)
          //   })
          // }

          setFieldsValue({ ...partData, ...params, ...pinsData })

            if (partData.library && partData.symbol) {
              axios.get(`/api/parts/pins?library=${partData.library}&symbol=${partData.symbol}`).then((res: any) => {
                this.setState({
                  symbol_pins: res.data
                })
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
  render() {
    const {
      getFieldDecorator, getFieldValue
    } = this.props.form

    const { spiceAttrs, pins, symbol_pins }= this.state
    const { selectedBlock, mods } = this.props
    const props = this.state.selectedBlockProps
    const footprints: any = this.state.footprints
    const params = this.state.params || getFieldValue('params') || {}
    const units = getFieldValue('params[units]') || []

    const attributes = Object.keys(params).map(name => {
      const args = params
      let suffix = this.state.params[name].unit.suffix 

       return getFieldDecorator(`params[${name}]`, {})(<Select
          key={name}
          mode="tags"
          style={{ width: '100%' }}
          placeholder={name + ' in ' + suffix}
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

    
    const pinsValue: any = getFieldValue('pins')

    const Pins:any = ({ unit }:any) => <>
      <Divider orientation="left">Unit "{unit}"</Divider>
      <Row>
        {pins.map(pin => {
          return (<Form.Item label={pin} key={pin} style={{width: '45%'}}>
            {getFieldDecorator(`pins[${unit}][${pin}]`, { initialValue: pinsValue && pinsValue[unit] && pinsValue[unit][pin] })(<Select
              mode="multiple"
              placeholder='Select Attached Block Pins'
            >
              {symbol_pins.map(pin => <Option key={pin} value={pin}>{pin}</Option>)}
            </Select>)}
          </Form.Item>)
          
        })}
      </Row>
      </>
    

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
            <Row className={cnStock('AddFormStock')}>
              <Form.Item>
                {getFieldDecorator('library', {})(
                  <Input placeholder="KICAD Library" />
                )}
              </Form.Item> 
              <Form.Item>
                {getFieldDecorator('symbol', {})(
                  <Input placeholder="KICAD Symbol" />
                )}
              </Form.Item>
            </Row>
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
                >
                
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
            <img className={cnStock('Footprint') }src={'/api/parts/footprint/?name=' + this.state.footprint}/>
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
        
        {units.map((unit:string) =>
          <Pins unit={unit} key={unit}/>
        )}
        
        <Divider orientation="left">Print Label</Divider> 
            <PrintLabel
                block={selectedBlock}
                model={getFieldValue('model')}
                footprint={getFieldValue('footprint')}
                description={getFieldValue('description')}
                params={getFieldValue('params')}
           />
      </Form>
    )
  }
}

export const Part = Form.create()(AddForm)

