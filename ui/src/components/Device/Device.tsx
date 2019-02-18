import * as React from 'react'
import { IProps, TDevice } from './index'
import { cn } from '@bem-react/classname'
import axios from 'axios'
import { Button, Select, TreeSelect} from 'antd'
import { Form, Divider, Tabs, Row, Col, Modal } from 'antd'
import Markdown from 'react-markdown'
const { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceArea } = require('recharts')
const TabPane = Tabs.TabPane;
import './Device.css'
import { UnitInput } from '../UnitInput'

const nomnoml = require('nomnoml')
const TreeNode = TreeSelect.TreeNode;
const { Option, OptGroup } = Select

const cnPart = cn('Device')

const initialState = {
    name: '',
    pins: {},
    parts: {},
    index: -1,
    footprint: '',
    footprints: {}
}

type State = {
    name: string,
    pins: TDevice['pins'],
    parts: {
        [name: string]: string[]
    },
    device?: TDevice,
    index: number,
    footprint: string,
    footprints: {
        [name: string]: {
            [mod: string]: string[] | {
                [block: string]: string[]
            }
        }
    }
}


export class Device extends React.Component<IProps, {}> {
    state: State = {
        ...initialState,
        name: this.props.device.name,
        index: this.props.device.index >= 0
            ? this.props.device.index 
            : -1
    }

    componentWillMount() {
        // this.loadParts()

        return true
    }
    // loadParts() {
    //     axios.get('http://localhost:3000/api/devices/')
    //         .then(res => {
    //             const parts = res.data
    //             this.setState({ parts }, () => this.loadDevice(this.props.device))
    //         })
    // }
    getCurrentDevice() {
        const device = this.state.device


        return {
            ...device,
            pins: Object.assign({}, this.state.pins),
            index: this.state.index
        }
        return {}
    }
    loadDevice({ name, pins, index }: TDevice) {
        this.setState(({ parts }: State) => {
            if (index === -1 || index === undefined) {
                return {
                    name: undefined,
                    index: -1,
                    pins: {}
                }
            } else {
                return {
                    parts,
                    name,
                    index,
                    pins
                }
            }
        })
    }
    componentDidUpdate(prevProps: IProps) {
        if (prevProps.device.index !== this.props.device.index) {
            this.loadDevice(this.props.device)
        }
    }
    render() { 
        const { onChange } = this.props
        const footprints: any = this.state.footprints
        const { parts } = this.state
        const name = this.state.name 
            ? this.state.name.split('_')[0]
            : undefined
        
        const pins: any = this.state.device
            ? this.state.device.pins
            : []

        const formItemLayout = {
            labelCol: { span: 7 },
            wrapperCol: { span: 12 },
        }

        const Pins = <Form>
            {pins.map((pin:any) => {
                return (<Form.Item label={pin} {...formItemLayout} key={pin}>
                    <Select
                        mode="multiple"
                        placeholder='Select Attached Block Pins'
                        value={this.state.pins && this.state.pins[pin]}
                        onChange={(value: string[]) => {
                            this.setState(({ pins }: State) => {
                                pins[pin] = value

                                return { pins }
                            }, () => onChange(this.getCurrentDevice()))
                        }}
                    >
                        {this.props.pins.map(pin => <Option key={pin} value={pin}>{pin}</Option>)}
                    </Select>
                </Form.Item>)
            })}
            </Form>

        
        return (
            <div className={cnPart()}>
            
                <TreeSelect
                    showSearch
                    style={{ width: 230 }}
                    dropdownStyle={{ maxHeight: 400, overflow: 'auto' }}
                    placeholder="Device"
                    allowClear
                    treeDefaultExpandAll
                    onSearch={(value) => {
                        if (value.length >= 3) {
                        axios.get('/api/devices/?query=' + value).then((res: any) => {
                            this.setState({ parts: res.data })
                        })
                        }
                    }}
                    onChange={(value) => {
                        axios.get('/api/devices?name=' + value).then((res: any) => {
                            this.setState({ device: res.data })
                        })
                    }}>
                    
                    {Object.keys(parts).map((lib, index) => 
                        <TreeNode title={lib} key={lib + index}>
                            {parts[lib].map(item =>
                                <TreeNode value={lib + ':' + item[0]} title={item[0]} key={lib + ':' + item[0]}  />
                            )}
                        </TreeNode>
                    )}
                </TreeSelect>

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

                    //   this.kicadviewer.render(data.data)
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
                {this.state.device && this.state.device.description}
                <Divider orientation="left">Pins</Divider>
                {Pins}
            </div>
        )
    }
}