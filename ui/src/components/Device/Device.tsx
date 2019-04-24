import * as React from 'react'
import { IProps, TDevice } from './index'
import { cn } from '@bem-react/classname'
import axios from 'axios'
import { Row, Col, Select, TreeSelect} from 'antd'
import { Form, Divider } from 'antd'
import './Device.css'

const TreeNode = TreeSelect.TreeNode;
const { Option } = Select

const cnPart = cn('Device')

const initialState = {
    name: '',
    pins: {},
    parts: {},
    index: -1,
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
        this.loadDevice(this.props.device) 
    }
    getCurrentDevice() {
        const device = this.state.device

        return {
            ...device,
            pins: Object.assign({}, this.state.pins),
            index: this.state.index
        }
        return {}
    }
    loadDevice({ name, description, library, footprint, pins, index }: TDevice) {
        if (index === -1 || index === undefined) {
            this.setState(({ parts }: State) => {
                return {
                    device: {
                        name: undefined,
                        library: undefined,
                        description: undefined,
                        footprint: undefined,
                        index: -1,
                        pins: []
                    },
                    pins: {}
                }
            })
        } else {
            name = name.slice(0, name.lastIndexOf('_'))
            axios.get('/api/devices?name=' + library + ':' + name).then((res: any) => {
                this.setState(({ parts }: State) => {
                    return {
                        parts,
                        device: {
                            name,
                            library,
                            description,
                            footprint,
                            index,
                            pins: res.data.pins
                        },
                        pins
                    }
                })
            })
        }
        
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
        const { device } = this.state
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
                <Row>
                    <Col span={11}>
                        <TreeSelect
                            showSearch
                            style={{ width: 230 }}
                            dropdownStyle={{ maxHeight: 400, overflow: 'auto' }}
                            placeholder="Device"
                            allowClear
                            treeDefaultExpandAll
                            value={device && device.library ? device.library + ':' + device.name : ''}
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
                                <TreeNode value={lib} title={lib} key={lib + index}>
                                    {parts[lib].map(item =>
                                        <TreeNode value={lib + ':' + item[0]} title={item[0]} key={lib + ':' + item[0]}  />
                                    )}
                                </TreeNode>
                            )}
                        </TreeSelect>
                    </Col>
                    <Col span={12} push={1}>
                        <TreeSelect
                        showSearch
                        style={{ width: 230 }}
                        value={device ? device.footprint : ''}
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
                                this.setState(({ device }: any) => {
                                    return ({ device: { ...device || {}, footprint: value } })
                                })
                            //   this.kicadviewer.render(data.data)
                            })
                        }}>
                            {Object.keys(this.state.footprints).map((type:string) =>
                            <TreeNode value={type} title={type} key={type}>
                                {footprints[type].map((value:string) => 
                                    <TreeNode value={type + ':' + value} title={value} key={type + ':' + value} />
                                )}
                            </TreeNode>
                            )}
                        </TreeSelect>
                    </Col>
                </Row>
                {this.state.device && this.state.device.description}
                <Divider orientation="left">Pins</Divider>
                {Pins}
            </div>
        )
    }
}